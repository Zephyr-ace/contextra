// Shared frontend types matching backend Pydantic models

export type Position = {
  symbol: string;
  name: string;
  quantity: number;
  average_cost: number;
  market_value: number;
  pl_percent: number;
  currency?: string;
  urgency?: string;
};

export type Portfolio = {
  positions: Position[];
};

export type RebalancingFrequency = "monthly" | "quarterly" | "semiannually" | "annually";

export type Strategy = {
  name: string;
  description: string;
  time_horizon: string;
  risk_level: string;
  rebalancing_frequency: RebalancingFrequency;
  allocation_targets: Record<string, number>;
  preferences?: string[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
};

export type ChatRequest = {
  message: string;
  chat_history?: ChatMessage[];
};

export type ChatResponse = {
  message: string;
  chat_history: ChatMessage[];
};


