export const USD_TO_INR_RATE = 86.5;

export const toINR = (amountUsd: number): number => {
  return amountUsd * USD_TO_INR_RATE;
};

export const formatINR = (amountUsd: number, fractionDigits = 0): string => {
  const inr = toINR(amountUsd);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: fractionDigits,
    minimumFractionDigits: fractionDigits,
  }).format(inr);
};

export const formatUSD = (amountUsd: number): string => {
  return `$${Number(amountUsd).toFixed(2)}`;
};

/**
 * Returns formatted dual currency: e.g. "₹2,163 (~$25.00)"
 */
export const formatDualCurrency = (amountUsd: number, showDecimals = false): string => {
  const inr = formatINR(amountUsd, showDecimals ? 2 : 0);
  const usd = formatUSD(amountUsd);
  return `${inr} (${usd})`;
};
