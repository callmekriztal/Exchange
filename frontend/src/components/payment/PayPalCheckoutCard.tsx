import React, { useState } from 'react';
import { Contract } from '../../types';
import { api } from '../../services/api';
import { CheckCircle, CreditCard, Lock, ShieldCheck, AlertCircle } from 'lucide-react';
import { PayPalButtons, PayPalScriptProvider } from '@paypal/react-paypal-js';

interface Props {
  objectiveId: string;
  contracts: Contract[];
  onPaymentSuccess: () => void;
}

export const PayPalCheckoutCard: React.FC<Props> = ({ objectiveId, contracts, onPaymentSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [captured, setCaptured] = useState(false);

  const totalAmount = contracts.reduce((acc, c) => acc + Number(c.agreed_amount_usd), 0);
  const paypalClientId = import.meta.env.VITE_PAYPAL_CLIENT_ID || '';
  const isClientIdConfigured = Boolean(
    paypalClientId &&
    paypalClientId !== 'test' &&
    !paypalClientId.toLowerCase().includes('placeholder') &&
    !paypalClientId.toLowerCase().includes('your-paypal')
  );

  if (captured || contracts.every((c) => c.status === 'funded' || c.status === 'active' || c.status === 'completed')) {
    return (
      <div className="bg-emerald-950/40 border border-emerald-700/60 rounded-xl p-5 text-emerald-300 space-y-2">
        <div className="flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <h4 className="font-semibold text-sm text-white">Payment Captured & Funds Escrowed</h4>
        </div>
        <p className="text-xs text-slate-300">
          The PayPal Sandbox order has been captured. Funds are safely held in internal Escrow and will be released to Seller Agents only upon quality evaluation approval.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-6 space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <CreditCard className="w-5 h-5 text-emerald-400" />
          <h3 className="font-bold text-white text-base">Human Authorization Gate: PayPal Sandbox Checkout</h3>
        </div>
        <span className="text-xs text-slate-400 flex items-center gap-1">
          <Lock className="w-3.5 h-3.5 text-emerald-400" /> 256-bit Encrypted
        </span>
      </div>

      <div className="space-y-2">
        <p className="text-xs text-slate-400">
          AI agents have autonomously negotiated prices. To authorize genuine PayPal Sandbox settlement and fund escrow, complete checkout below:
        </p>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 space-y-1.5 text-xs">
          {contracts.map((c, i) => (
            <div key={c.id} className="flex justify-between text-slate-300">
              <span>Task #{i + 1} Contract:</span>
              <span className="font-mono text-emerald-400 font-semibold">${Number(c.agreed_amount_usd).toFixed(2)} USD</span>
            </div>
          ))}
          <div className="border-t border-slate-800 pt-2 flex justify-between text-white font-bold text-sm">
            <span>Total Agreed Settlement:</span>
            <span className="font-mono text-emerald-400">${totalAmount.toFixed(2)} USD</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/40 border border-rose-800 rounded-lg p-3 flex items-start space-x-2 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Real PayPal Script Provider and Button */}
      <div className="space-y-3">
        {!isClientIdConfigured ? (
          <div className="bg-amber-950/40 border border-amber-800 rounded-lg p-4 space-y-2 text-amber-200 text-xs">
            <div className="flex items-center space-x-2 font-semibold text-amber-300">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>PayPal Sandbox Client ID Required</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              To render genuine PayPal Sandbox Checkout buttons, please configure your PayPal Sandbox credentials in <code className="bg-slate-800 px-1.5 py-0.5 rounded text-amber-300">.env</code>:
            </p>
            <pre className="bg-slate-900 border border-slate-800 p-2.5 rounded text-[11px] font-mono text-emerald-400 overflow-x-auto">
{`PAYPAL_CLIENT_ID=your-sandbox-client-id
PAYPAL_CLIENT_SECRET=your-sandbox-client-secret
PAYPAL_MODE=sandbox
PAYPAL_MOCK_MODE=false`}
            </pre>
            <p className="text-[11px] text-slate-400">
              Once configured, the official PayPal JavaScript SDK will load and authenticate live checkout sessions against <code className="text-slate-300">api-m.sandbox.paypal.com</code>.
            </p>
          </div>
        ) : (
          <PayPalScriptProvider options={{ clientId: paypalClientId, currency: 'USD', intent: 'capture' }}>
            <div className="min-h-[120px]">
              <PayPalButtons
                style={{ layout: 'vertical', color: 'gold', shape: 'rect', label: 'pay' }}
                disabled={loading}
                createOrder={async () => {
                  setError(null);
                  try {
                    const contractIds = contracts.map((c) => c.id);
                    const order = await api.createPayPalOrder(objectiveId, contractIds);
                    return order.paypal_order_id;
                  } catch (err: any) {
                    const errMsg = err?.response?.data?.detail || err.message || 'Failed to create PayPal Sandbox order';
                    setError(errMsg);
                    throw err;
                  }
                }}
                onApprove={async (data) => {
                  setLoading(true);
                  setError(null);
                  try {
                    await api.capturePayPalOrder(data.orderID);
                    setCaptured(true);
                    onPaymentSuccess();
                  } catch (err: any) {
                    setError(err?.response?.data?.detail || err.message || 'Failed to capture PayPal Sandbox order');
                  } finally {
                    setLoading(false);
                  }
                }}
                onError={(err: any) => {
                  const msg = err?.message || 'PayPal Checkout SDK encountered an error during authorization';
                  console.error('PayPal Button Error:', err);
                  setError(msg);
                }}
                onCancel={() => {
                  setError('PayPal Checkout was cancelled by user.');
                }}
              />
            </div>
          </PayPalScriptProvider>
        )}

        <div className="flex items-center space-x-2 text-[11px] text-slate-400 justify-center pt-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Payment funds are strictly locked in escrow until AI buyer evaluates output.</span>
        </div>
      </div>
    </div>
  );
};
