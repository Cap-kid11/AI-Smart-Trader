// Real backtest results produced by the project's own engine on the bundled
// sample data. NOT cherry-picked — one strategy made money, one lost money,
// and we show both. The losing result is the point: honesty is the product.
//
// Regenerate with backend/demo.py logic; do not hand-edit the numbers.

export type BacktestResult = {
  name: string;
  totalReturn: number;
  winRate: number;
  numTrades: number;
  maxDrawdown: number;
  sharpe: number;
  profitFactor: number;
  spark: number[];
};

export const RESULTS: Record<"rsi" | "ma", BacktestResult> = {
  rsi: {
    name: "RSI Mean Reversion",
    totalReturn: 0.0233,
    winRate: 0.5455,
    numTrades: 11,
    maxDrawdown: -0.0841,
    sharpe: 0.18,
    profitFactor: 1.18,
    spark: [
      10000, 10000, 10032, 10311.5, 10311.5, 10311.5, 10311.5, 10311.5, 10311.5,
      10162.78, 9829.03, 10008.17, 10008.17, 10008.17, 10008.17, 10008.17,
      10008.17, 10008.17, 10008.17, 10008.17, 10008.17, 10346.3, 10346.3,
      10346.3, 10346.3, 10346.3, 10346.3, 10346.3, 10346.3, 10346.3, 10346.3,
      10346.3, 10346.3, 10346.3, 10346.3, 10575.38, 10225.78, 9800.13, 9961.81,
      9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81,
      9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81, 9961.81,
      9991.21, 10287.61, 10287.61, 10287.61, 10247.31, 10098.97, 10232.97,
    ],
  },
  ma: {
    name: "Moving Average Crossover",
    totalReturn: -0.1918,
    winRate: 0.1579,
    numTrades: 19,
    maxDrawdown: -0.2473,
    sharpe: -0.91,
    profitFactor: 0.34,
    spark: [
      10000, 10000, 10000, 10000, 10000, 9847.45, 9676.74, 9819.34, 9819.34,
      9819.34, 9819.34, 9819.34, 9819.34, 9819.34, 9819.34, 9797.92, 10160.02,
      10273.24, 10149.82, 10553.23, 10013.65, 10022.83, 10022.83, 9971.98,
      9909.43, 9797.81, 9827.18, 10184.51, 9896.84, 9807.83, 10093.35, 10378.01,
      10366.83, 10255.03, 10243.85, 10243.85, 10243.85, 10243.85, 10243.85,
      9992.9, 9992.9, 10100.9, 9535.01, 9469.13, 9469.13, 8892.15, 8834.61,
      8834.61, 8834.61, 8834.61, 8834.61, 8834.61, 8834.61, 8834.61, 8834.61,
      8738.93, 8331.91, 8331.91, 8082.39, 8082.39, 8082.39, 8082.39, 8082.39,
    ],
  },
};
