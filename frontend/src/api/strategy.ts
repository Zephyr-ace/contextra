import { apiClient, ApiError } from "./client";
import type { Strategy } from "@/types/models";

export interface StrategyService {
  getStrategy(): Promise<Strategy>;
}

class StrategyServiceImpl implements StrategyService {
  async getStrategy(): Promise<Strategy> {
    try {
      return await apiClient.get<Strategy>("/investment-strategy");
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(`Failed to load strategy (${error.status})`);
      }
      throw new Error("Failed to load strategy");
    }
  }
}

export const strategyService = new StrategyServiceImpl();
