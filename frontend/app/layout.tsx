import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veridian — honest strategy backtesting for traders",
  description:
    "Build trading strategies, backtest them with honest metrics, and learn to read the market. No guaranteed-win promises. Paper trading under risk limits you set.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
