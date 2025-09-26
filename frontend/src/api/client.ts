const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new ApiError(
        `Request failed: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }
}

export const apiClient = new ApiClient();
