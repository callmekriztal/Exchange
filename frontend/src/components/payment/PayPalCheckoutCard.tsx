import React, { useState } from 'react';
import { Contract } from '../../types';
import { api } from '../../services/api';
import { CheckCircle, CreditCard, ShieldCheck, AlertCircle } from 'lucide-react';
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
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <CreditCard className="w-4 h-4 text-emerald-400" />
          <h3 className="font-semibold text-white text-sm">PayPal Sandbox Authorization</h3>
        </div>
        <span className="font-mono text-emerald-400 font-bold text-sm">
          ${totalAmount.toFixed(2)} USD
        </span>
      </div>

      <p className="text-xs text-slate-400">
        Review negotiated pricing and authorize checkout to lock funds in Escrow.
      </p>

      {error && (
        <div className="bg-rose-950/40 border border-rose-800 rounded-lg p-2.5 flex items-start space-x-2 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Real PayPal Script Provider and Button */}
      <div className="space-y-2">
        {!isClientIdConfigured ? (
          <div className="bg-amber-950/30 border border-amber-800/60 rounded-lg p-3 text-xs text-amber-200 space-y-1">
            <div className="flex items-center space-x-1.5 font-medium text-amber-300">
              <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>PayPal Sandbox Credentials Required</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Set <code className="text-amber-300">PAYPAL_CLIENT_ID</code> and <code className="text-amber-300">PAYPAL_CLIENT_SECRET</code> in <code className="text-slate-300">.env</code> to load the PayPal Checkout button.
            </p>
          </div>
        ) : (
          <PayPalScriptProvider options={{ clientId: paypalClientId, currency: 'USD', intent: 'capture' }}>
            <div className="max-w-md mx-auto">
              <PayPalButtons
                style={{ layout: 'vertical', color: 'gold', shape: 'rect', label: 'pay', height: 40 }}
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
                  setError('PayPal Checkout was cancelled.');
                }}
              />
            </div>
          </PayPalScriptProvider>
        )}

        <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 justify-center pt-1">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          <span>Held in escrow until tasks are accepted</span>
        </div>
      </div>
    </div>
  );
};
