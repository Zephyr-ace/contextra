import { apiClient } from "./client";
import type { ChatRequest, ChatResponse } from "@/types/models";

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>("/chat", request);
  },
};
