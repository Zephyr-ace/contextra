'use client';

import React from 'react';

const AnalysisContent = () => {
  return (
    <div className="space-y-6">
      {/* What Happened Section */}
      <div className="bg-white border border-[var(--ubs-border)] rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <h3 className="text-lg font-semibold text-[var(--ubs-black)]">What Happened</h3>
        </div>
        <div className="prose prose-sm max-w-none">
          <h4 className="text-base font-medium text-[var(--ubs-black)] mb-3">
            Advisory Note – Apple Inc. (AAPL) Exposure Amid Escalating Geopolitical Risk
          </h4>
          <p className="text-sm text-neutral-700 leading-relaxed mb-3">
            If China were to declare war on Taiwan, the implications for Apple would be severe due to its reliance on Taiwanese semiconductor manufacturing (particularly TSMC) and its supply chain exposure in China. Such an event could trigger:
          </p>
          <ul className="text-sm text-neutral-700 leading-relaxed space-y-2 ml-4">
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-1">•</span>
              <span><strong>Severe supply chain disruptions</strong> – Apple's most advanced chips are produced in Taiwan. Any conflict could halt production or shipping.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-1">•</span>
              <span><strong>Market volatility and investor panic</strong> – AAPL shares could experience significant short-term sell-offs as global markets reprice geopolitical risk.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-1">•</span>
              <span><strong>Longer-term uncertainty</strong> – Even if Apple adapts, rebuilding its supply chain outside of Taiwan would take years, not months.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Recommended Action Section */}
      <div className="bg-white border border-[var(--ubs-border)] rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <h3 className="text-lg font-semibold text-[var(--ubs-black)]">Recommended Action</h3>
        </div>
        <div className="prose prose-sm max-w-none">
          <h4 className="text-base font-medium text-[var(--ubs-black)] mb-3">
            Recommended Course of Action
          </h4>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 text-xs font-semibold">1</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-[var(--ubs-black)] mb-1">Risk Management</h5>
                <p className="text-sm text-neutral-700">Consider trimming your AAPL exposure to reduce downside risk. Avoid concentrated positions in the stock given its vulnerability to this specific geopolitical shock.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 text-xs font-semibold">2</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-[var(--ubs-black)] mb-1">Hedging</h5>
                <p className="text-sm text-neutral-700">If you want to maintain your position, explore protective strategies (e.g., put options, stop-loss orders) to manage potential downside.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 text-xs font-semibold">3</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-[var(--ubs-black)] mb-1">Diversification</h5>
                <p className="text-sm text-neutral-700">Reallocate part of your portfolio toward sectors or geographies less exposed to East Asian supply chains—such as U.S.-centric technology, defense, or energy.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-600 text-xs font-semibold">4</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-[var(--ubs-black)] mb-1">Liquidity Preservation</h5>
                <p className="text-sm text-neutral-700">Maintain higher cash levels or allocate to defensive assets (U.S. Treasuries, gold, utilities) to weather heightened volatility.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisContent;
