import { apiClient, ApiError } from "./client";
import type { Portfolio } from "@/types/models";

export interface PortfolioService {
  getPortfolio(): Promise<Portfolio>;
}

class PortfolioServiceImpl implements PortfolioService {
  async getPortfolio(): Promise<Portfolio> {
    try {
      return await apiClient.get<Portfolio>("/portfolio");
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(`Failed to load portfolio (${error.status})`);
      }
      throw new Error("Failed to load portfolio");
    }
  }
}

export const portfolioService = new PortfolioServiceImpl();
