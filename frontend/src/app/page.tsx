"use client";

import Image from "next/image";
import { useState } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"Portfolio" | "Investment Strategy">("Portfolio");

  return (
    <div className="font-sans min-h-screen p-6 sm:p-10">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[calc(100vh-theme(spacing.6)*2)] sm:min-h-[calc(100vh-theme(spacing.10)*2)]">
        {/* Main Column with top-left attached tabs */}
        <div className="lg:col-span-9 flex flex-col gap-3">
          <nav className="sticky top-0 z-10 flex items-center gap-2">
            <button
              type="button"
              title="Portfolio"
              aria-label="Portfolio"
              onClick={() => setActiveTab("Portfolio")}
              className={`h-10 w-10 rounded-md border flex items-center justify-center transition-colors ${
                activeTab === "Portfolio"
                  ? "bg-[var(--ubs-gray-100)] border-[var(--ubs-border)] text-[var(--ubs-black)]"
                  : "bg-white border-[var(--ubs-border)] hover:bg-[var(--ubs-gray-50)] text-[var(--ubs-black)]"
              }`}
            >
              📊
            </button>
            <button
              type="button"
              title="Investment Strategy"
              aria-label="Investment Strategy"
              onClick={() => setActiveTab("Investment Strategy")}
              className={`h-10 w-10 rounded-md border flex items-center justify-center transition-colors ${
                activeTab === "Investment Strategy"
                  ? "bg-[var(--ubs-gray-100)] border-[var(--ubs-border)] text-[var(--ubs-black)]"
                  : "bg-white border-[var(--ubs-border)] hover:bg-[var(--ubs-gray-50)] text-[var(--ubs-black)]"
              }`}
            >
              🧭
            </button>
          </nav>

          {/* Main Content */}
          <section className="surface-card accent-top h-full flex flex-col">
          <div className="p-5 sm:p-6">
            {activeTab === "Portfolio" ? (
              <>
                <h1 className="section-title text-xl sm:text-2xl">Portfolio</h1>
                <p className="text-sm text-neutral-600 mt-1">Overview of positions and performance</p>

                <div className="mt-5 divide-y divide-[var(--ubs-border)]">
                  {/* Accordion items */}
                  <details role="accordion" className="py-3 group" open>
                    <summary className="flex items-center justify-between cursor-pointer">
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full" style={{ backgroundColor: "var(--ubs-red)" }} />
                        <span className="font-medium">Apple Inc. (AAPL)</span>
                      </div>
                      <span className="text-sm text-neutral-600 group-open:rotate-180 transition-transform">▾</span>
                    </summary>
                    <div className="mt-3 pl-5 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-neutral-500">Quantity</div>
                        <div className="font-medium">120</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Avg. Cost</div>
                        <div className="font-medium">$168.40</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Market Value</div>
                        <div className="font-medium">$21,480</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">P/L</div>
                        <div className="font-medium text-green-600">+4.2%</div>
                      </div>
                    </div>
                  </details>

                  <details role="accordion" className="py-3 group">
                    <summary className="flex items-center justify-between cursor-pointer">
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-neutral-300" />
                        <span className="font-medium">Microsoft (MSFT)</span>
                      </div>
                      <span className="text-sm text-neutral-600 group-open:rotate-180 transition-transform">▾</span>
                    </summary>
                    <div className="mt-3 pl-5 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-neutral-500">Quantity</div>
                        <div className="font-medium">80</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Avg. Cost</div>
                        <div className="font-medium">$310.20</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Market Value</div>
                        <div className="font-medium">$25,200</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">P/L</div>
                        <div className="font-medium text-red-600">-1.1%</div>
                      </div>
                    </div>
                  </details>

                  <details role="accordion" className="py-3 group">
                    <summary className="flex items-center justify-between cursor-pointer">
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-neutral-300" />
                        <span className="font-medium">UBS Group (UBSG)</span>
                      </div>
                      <span className="text-sm text-neutral-600 group-open:rotate-180 transition-transform">▾</span>
                    </summary>
                    <div className="mt-3 pl-5 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-neutral-500">Quantity</div>
                        <div className="font-medium">500</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Avg. Cost</div>
                        <div className="font-medium">CHF 23.50</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">Market Value</div>
                        <div className="font-medium">CHF 12,150</div>
                      </div>
                      <div>
                        <div className="text-neutral-500">P/L</div>
                        <div className="font-medium text-green-600">+2.7%</div>
                      </div>
                    </div>
                  </details>
                </div>
              </>
            ) : (
              <>
                <h1 className="section-title text-xl sm:text-2xl">Investment Strategy</h1>
                <p className="text-sm text-neutral-600 mt-1">Coming soon</p>
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
