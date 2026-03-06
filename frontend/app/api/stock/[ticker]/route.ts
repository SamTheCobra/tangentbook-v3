import { NextResponse } from "next/server";

const cache = new Map<string, { data: StockData; ts: number }>();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

interface StockData {
  prices: number[];
  dates: string[];
  pctChanges: string[];
}

export async function GET(
  _req: Request,
  { params }: { params: { ticker: string } }
) {
  const ticker = params.ticker.toUpperCase();

  // Check cache
  const cached = cache.get(ticker);
  if (cached && Date.now() - cached.ts < CACHE_TTL) {
    return NextResponse.json(cached.data);
  }

  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1mo&range=1y`;
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0",
      },
    });

    if (!res.ok) {
      return NextResponse.json({ prices: [], dates: [], pctChanges: [] });
    }

    const json = await res.json();
    const result = json?.chart?.result?.[0];
    if (!result) {
      return NextResponse.json({ prices: [], dates: [], pctChanges: [] });
    }

    const timestamps: number[] = result.timestamp || [];
    const closes: (number | null)[] =
      result.indicators?.quote?.[0]?.close || [];

    const prices: number[] = [];
    const dates: string[] = [];

    for (let i = 0; i < timestamps.length; i++) {
      const close = closes[i];
      if (close != null) {
        prices.push(close);
        const d = new Date(timestamps[i] * 1000);
        dates.push(
          d.toLocaleDateString("en-US", { month: "short", year: "numeric" })
        );
      }
    }

    const pctChanges: string[] = [];
    for (let i = 1; i < prices.length; i++) {
      const pct = ((prices[i] - prices[i - 1]) / prices[i - 1]) * 100;
      pctChanges.push(pct.toFixed(1));
    }

    const data: StockData = { prices, dates, pctChanges };
    cache.set(ticker, { data, ts: Date.now() });

    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ prices: [], dates: [], pctChanges: [] });
  }
}
