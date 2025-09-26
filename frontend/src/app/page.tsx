"use client";

import { useEffect, useState } from "react";
import GraphViz from "./components/GraphViz";
import type { Portfolio, Strategy } from "@/types/models";
import { portfolioService, strategyService } from "@/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"Portfolio" | "Investment Strategy" | "Stock Details">("Portfolio");
  const [selectedStock, setSelectedStock] = useState<string>("AAPL");
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState<{ portfolio: boolean; strategy: boolean }>({ portfolio: true, strategy: true });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchPortfolio = async () => {
      try {
        const data = await portfolioService.getPortfolio();
        if (isMounted) setPortfolio(data);
      } catch (e: unknown) {
        if (isMounted) setError(e instanceof Error ? e.message : "Failed to load portfolio");
      } finally {
        if (isMounted) setLoading((prev) => ({ ...prev, portfolio: false }));
      }
    };

    const fetchStrategy = async () => {
      try {
        const data = await strategyService.getStrategy();
        if (isMounted) setStrategy(data);
      } catch (e: unknown) {
        if (isMounted) setError(e instanceof Error ? e.message : "Failed to load strategy");
      } finally {
        if (isMounted) setLoading((prev) => ({ ...prev, strategy: false }));
      }
    };

    fetchPortfolio();
    fetchStrategy();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="font-sans min-h-screen p-6 sm:p-10">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[calc(100vh-theme(spacing.6)*2)] sm:min-h-[calc(100vh-theme(spacing.10)*2)]">
        {/* Main Column with floating tabs above content */}
        <div className="lg:col-span-9 flex flex-col gap-3">
          {/* Floating tabs above the content window */}
          <nav className="relative z-10 flex items-center gap-2 -mb-3">
            <button
              type="button"
              title="Portfolio"
              aria-label="Portfolio"
              onClick={() => setActiveTab("Portfolio")}
              className={`h-10 w-10 rounded-md flex items-center justify-center transition-colors cursor-pointer-on-hover ${
                activeTab === "Portfolio"
                  ? "bg-[var(--ubs-gray-100)] text-[var(--ubs-black)]"
                  : "bg-white hover:bg-[var(--ubs-gray-50)] text-[var(--ubs-black)]"
              }`}
            >
              📊
            </button>
            <button
              type="button"
              title="Investment Strategy"
              aria-label="Investment Strategy"
              onClick={() => setActiveTab("Investment Strategy")}
              className={`h-10 w-10 rounded-md flex items-center justify-center transition-colors cursor-pointer-on-hover ${
                activeTab === "Investment Strategy"
                  ? "bg-[var(--ubs-gray-100)] text-[var(--ubs-black)]"
                  : "bg-white hover:bg-[var(--ubs-gray-50)] text-[var(--ubs-black)]"
              }`}
            >
              🧭
            </button>
            <button
              type="button"
              title="Stock Details"
              aria-label="Stock Details"
              onClick={() => setActiveTab("Stock Details")}
              className={`h-10 w-10 rounded-md flex items-center justify-center transition-colors cursor-pointer-on-hover ${
                activeTab === "Stock Details"
                  ? "bg-[var(--ubs-gray-100)] text-[var(--ubs-black)]"
                  : "bg-white hover:bg-[var(--ubs-gray-50)] text-[var(--ubs-black)]"
              }`}
            >
              📈
            </button>
          </nav>

          {/* Main Content Window */}
          <section className="surface-card accent-top h-full flex flex-col">
          <div className="p-5 sm:p-6 flex-1 flex flex-col min-h-0">
            {activeTab === "Portfolio" && (
              <>
                <h1 className="section-title text-xl sm:text-2xl">Portfolio</h1>
                <p className="text-sm text-neutral-600 mt-1">Overview of positions and performance</p>

                <div className="mt-5 divide-y divide-[var(--ubs-border)]">
                  {loading.portfolio && (
                    <div className="py-3 text-sm text-neutral-600">Loading portfolio…</div>
                  )}
                  {error && (
                    <div className="py-3 text-sm text-red-600">{error}</div>
                  )}
                  {!loading.portfolio && !error && portfolio?.positions?.map((p) => (
                    <details key={p.symbol} role="accordion" className="py-3 group" open>
                      <summary className="flex items-center justify-between cursor-pointer">
                        <div className="flex items-center gap-3">
                          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color || "var(--ubs-gray-300)" }} />
                          <span className="font-medium">{p.name} ({p.symbol})</span>
                        </div>
                        <span className="text-sm text-neutral-600 group-open:rotate-180 transition-transform">▾</span>
                      </summary>
                      <div className="mt-3 pl-5 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-neutral-500">Quantity</div>
                          <div className="font-medium">{p.quantity}</div>
                        </div>
                        <div>
                          <div className="text-neutral-500">Avg. Cost</div>
                          <div className="font-medium">{p.currency ? `${p.currency} ` : "$"}{p.average_cost.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-neutral-500">Market Value</div>
                          <div className="font-medium">{p.currency ? `${p.currency} ` : "$"}{p.market_value.toLocaleString()}</div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-neutral-500">P/L</div>
                            <div className={`font-medium ${p.pl_percent >= 0 ? "text-green-600" : "text-red-600"}`}>
                              {p.pl_percent >= 0 ? "+" : ""}{p.pl_percent}%
                            </div>
                          </div>
                          <button
                            type="button"
                            title="Stock Information"
                            aria-label="Stock Information"
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveTab("Stock Details");
                              setSelectedStock(p.symbol);
                            }}
                            className="h-8 w-8 rounded-md flex items-center justify-center transition-colors hover:bg-[var(--ubs-gray-50)] cursor-pointer-on-hover"
                            style={{ color: p.color || "var(--ubs-black)" }}
                          >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              <path d="M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </details>
                  ))}
                </div>
              </>
            )}

            {activeTab === "Investment Strategy" && (
              <>
                <h1 className="section-title text-xl sm:text-2xl">Investment Strategy</h1>
                <p className="text-sm text-neutral-600 mt-1">Your personalized approach to financial growth.</p>

                <div className="mt-5 divide-y divide-[var(--ubs-border)]">
                  {loading.strategy && (
                    <div className="py-3 text-sm text-neutral-600">Loading strategy…</div>
                  )}
                  {error && (
                    <div className="py-3 text-sm text-red-600">{error}</div>
                  )}
                  {!loading.strategy && !error && strategy && (
                    <>
                      <div className="py-3">
                        <div className="text-neutral-500">Name</div>
                        <div className="font-medium">{strategy.name}</div>
                      </div>
                      <div className="py-3">
                        <div className="text-neutral-500">Description</div>
                        <div className="font-medium">{strategy.description}</div>
                      </div>
                      <div className="py-3">
                        <div className="text-neutral-500">Risk Level</div>
                        <div className="font-medium">{strategy.risk_level}</div>
                      </div>
                      <div className="py-3">
                        <div className="text-neutral-500">Investment Horizon</div>
                        <div className="font-medium">{strategy.time_horizon}</div>
                      </div>
                      <div className="py-3">
                        <div className="text-neutral-500">Rebalancing</div>
                        <div className="font-medium capitalize">{strategy.rebalancing_frequency}</div>
                      </div>
                      {strategy.preferences?.length ? (
                        <div className="py-3">
                          <div className="text-neutral-500">Preferences</div>
                          <div className="font-medium">{strategy.preferences.join(", ")}</div>
                        </div>
                      ) : null}
                      {strategy.allocation_targets && (
                        <div className="py-3">
                          <div className="text-neutral-500">Allocation Targets</div>
                          <div className="font-medium grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
                            {Object.entries(strategy.allocation_targets).map(([k, v]) => (
                              <div key={k} className="flex items-center justify-between border border-[var(--ubs-border)] rounded-md px-2 py-1">
                                <span className="text-neutral-600">{k.replaceAll("_", " ")}</span>
                                <span>{(v * 100).toFixed(0)}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </>
            )}

            {activeTab === "Stock Details" && (
              <>
                <h1 className="section-title text-xl sm:text-2xl">Stock Details</h1>
                <p className="text-sm text-neutral-600 mt-1">Detailed information and historical performance.</p>

                <div className="mt-5">
                  <label htmlFor="stock-select" className="block text-sm font-medium text-neutral-700">Select Stock</label>
                  <select
                    id="stock-select"
                    name="stock-select"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-ubs-red focus:border-ubs-red sm:text-sm rounded-md"
                    value={selectedStock}
                    onChange={(e) => setSelectedStock(e.target.value)}
                  >
                    <option value="AAPL">Apple Inc. (AAPL)</option>
                    <option value="MSFT">Microsoft (MSFT)</option>
                    <option value="UBSG">UBS Group (UBSG)</option>
                  </select>
                </div>

                <div className="mt-4 flex-1 min-h-0">
                  <GraphViz />
                </div>
              </>
            )}

            </div>
          </section>
        </div>

        {/* Chat Panel */}
        <aside className="surface-card accent-top flex flex-col lg:col-span-3 h-full lg:mt-[52px] lg:h-[calc(100%_-_52px)] overflow-hidden">
          <div className="p-5 sm:p-6 border-b border-[var(--ubs-border)]">
            <h2 className="section-title text-lg">Analyst Chat</h2>
            <p className="text-sm text-neutral-600 mt-1">Discuss insights and next steps</p>
          </div>

          <div className="flex-1 overflow-auto p-5 space-y-4">
            {/* Sample messages */}
            <div className="flex gap-3 items-start">
              <div className="h-7 w-7 rounded-full bg-[var(--ubs-black)]" />
              <div>
                <div className="text-[13px] text-neutral-500">Analyst</div>
                <div className="mt-1 px-3 py-2 rounded-lg bg-[var(--ubs-gray-100)] text-sm max-w-[28rem]">
                  Apple is approaching resistance near $180. Consider trimming 10% of the position.
                </div>
              </div>
            </div>

            <div className="flex gap-3 items-start justify-end">
              <div>
                <div className="text-[13px] text-neutral-500 text-right">You</div>
                <div className="mt-1 px-3 py-2 rounded-lg bg-white border border-[var(--ubs-border)] text-sm max-w-[28rem]">
                  Noted. What is the updated target for UBSG after the latest report?
                </div>
              </div>
              <div className="h-7 w-7 rounded-full bg-[var(--ubs-red)]" />
            </div>
          </div>

          <form className="p-4 border-t border-[var(--ubs-border)] flex items-center gap-3">
            <input
              type="text"
              placeholder="Type your message..."
              className="flex-1 rounded-md border border-[var(--ubs-border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--ubs-red)]"
            />
            <button
              type="button"
              title="Send"
              aria-label="Send"
              className="h-10 w-10 grid place-items-center rounded-md bg-[var(--ubs-red)] text-white hover:opacity-90"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M3.4 20.6L21 12L3.4 3.4L3 10L15 12L3 14L3.4 20.6Z" fill="currentColor"/>
              </svg>
            </button>
          </form>
        </aside>
      </div>
    </div>
  );
}
