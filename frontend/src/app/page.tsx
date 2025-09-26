"use client";

import { useEffect, useState, useRef } from "react";
import GraphViz from "./components/GraphViz";
import type { Portfolio, Strategy, ChatMessage } from "@/types/models";
import { portfolioService, strategyService, chatService } from "@/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"Portfolio" | "Investment Strategy" | "Stock Details">("Portfolio");
  const [selectedStock, setSelectedStock] = useState<string>("AAPL");
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState<{ portfolio: boolean; strategy: boolean }>({ portfolio: true, strategy: true });
  const [error, setError] = useState<string | null>(null);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI financial analyst. I can help you analyze your portfolio, discuss investment strategies, and provide insights on market trends. What would you like to know?",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Resize state
  const [isResizing, setIsResizing] = useState(false);
  const [contentWidth, setContentWidth] = useState(75); // Percentage
  const [isDesktop, setIsDesktop] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Check if desktop layout
  useEffect(() => {
    const checkDesktop = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    
    checkDesktop();
    window.addEventListener('resize', checkDesktop);
    
    return () => window.removeEventListener('resize', checkDesktop);
  }, []);

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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: chatInput.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: userMessage.content,
        chat_history: chatMessages,
      });

      setChatMessages(response.chat_history);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isChatLoading]);

  // Resize handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return;
    
    const containerRect = containerRef.current.getBoundingClientRect();
    const newContentWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    // Constrain between 50% and 80% (chat minimum 20%, content maximum 80%)
    const constrainedWidth = Math.min(Math.max(newContentWidth, 50), 80);
    setContentWidth(constrainedWidth);
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  // Add global mouse event listeners
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  return (
    <div className="font-sans h-screen p-6 sm:p-10">
      <div 
        ref={containerRef}
        className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-2 h-[calc(100vh-theme(spacing.6)*2)] sm:h-[calc(100vh-theme(spacing.10)*2)]"
      >
        {/* Main Column with side tabs */}
        <div 
          className="flex gap-3 w-full lg:w-auto"
          style={{ width: isDesktop ? `${contentWidth}%` : '100%' }}
        >
          {/* UBS Logo and Side tabs on the left */}
          <div className="flex flex-col gap-3 w-12 flex-shrink-0">
            {/* UBS Logo */}
            <div className="flex justify-center">
              <img 
                src="https://upload.wikimedia.org/wikipedia/de/a/a0/UBS_Logo_SVG.svg" 
                alt="UBS Logo" 
                className="h-8 w-auto"
              />
            </div>
            
            {/* Side tabs */}
            <nav className="flex flex-col gap-2">
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
          </div>

          {/* Main Content Window */}
          <section className="surface-card accent-top flex-1 flex flex-col overflow-hidden">
          <div className="p-5 sm:p-6 flex-1 flex flex-col overflow-auto">
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

        {/* Resize Handle */}
        <div
          className="hidden lg:flex items-center justify-center"
        >
          <div
            className="w-0.5 h-8 bg-gray-300 hover:bg-gray-400 cursor-col-resize transition-colors rounded-full"
            onMouseDown={handleMouseDown}
          />
        </div>

        {/* Chat Panel */}
        <aside 
          className="surface-card accent-top flex flex-col flex-1 overflow-hidden"
          style={{ width: isDesktop ? `${100 - contentWidth}%` : '100%' }}
        >
          <div className="p-5 sm:p-6 border-b border-[var(--ubs-border)]">
            <h2 className="section-title text-lg">Analyst Chat</h2>
            <p className="text-sm text-neutral-600 mt-1">Discuss insights and next steps</p>
          </div>

          <div className="flex-1 overflow-auto p-5 space-y-4">
            {chatMessages.map((message, index) => (
              <div key={index} className={`flex gap-3 items-start ${message.role === "user" ? "justify-end" : ""}`}>
                {message.role === "assistant" && <div className="h-7 w-7 rounded-full bg-[var(--ubs-black)]" />}
                <div>
                  <div className="text-[13px] text-neutral-500">{message.role === "user" ? "You" : "Analyst"}</div>
                  <div className={`mt-1 px-3 py-2 rounded-lg text-sm max-w-[28rem] ${
                    message.role === "user" 
                      ? "bg-white border border-[var(--ubs-border)]" 
                      : "bg-[var(--ubs-gray-100)]"
                  }`}>
                    {message.content}
                  </div>
                </div>
                {message.role === "user" && <div className="h-7 w-7 rounded-full bg-[var(--ubs-red)]" />}
              </div>
            ))}
            
            {isChatLoading && (
              <div className="flex gap-3 items-start">
                <div className="h-7 w-7 rounded-full bg-[var(--ubs-black)]" />
                <div>
                  <div className="text-[13px] text-neutral-500">Analyst</div>
                  <div className="mt-1 px-3 py-2 rounded-lg bg-[var(--ubs-gray-100)] text-sm max-w-[28rem]">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t border-[var(--ubs-border)] flex items-center gap-2 min-w-0">
            <input
              type="text"
              placeholder="Type your message..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={isChatLoading}
              className="flex-1 min-w-0 rounded-md border border-[var(--ubs-border)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--ubs-red)] disabled:opacity-50"
            />
            <button
              type="submit"
              title="Send"
              aria-label="Send"
              disabled={isChatLoading || !chatInput.trim()}
              className="h-10 w-10 flex-shrink-0 grid place-items-center rounded-md bg-[var(--ubs-red)] text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
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
