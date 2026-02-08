// Centralized API client that automatically attaches JWT from Better Auth session
import { useSession } from '@/lib/auth';

// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

/**
 * Generic API client for making authenticated requests
 */
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || API_BASE_URL;
  }

  /**
   * Make an authenticated request
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    sessionToken?: string
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    } as Record<string, string>;

    // Add authorization header if session token is available
    if (sessionToken) {
      headers['Authorization'] = `Bearer ${sessionToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, sessionToken?: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, sessionToken);
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data: unknown, sessionToken?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      sessionToken
    );
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data: unknown, sessionToken?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      },
      sessionToken
    );
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, sessionToken?: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, sessionToken);
  }
}

// Create a singleton instance
export const apiClient = new ApiClient();

/**
 * Hook to get an API client with session token
 * This would typically be used in client components alongside useSession
 */
export const useApiClient = () => {
  const { data: session } = useSession();
  const token = session?.session?.token; // Access token from session.session

  const request = async <T>(endpoint: string, options: RequestInit = {}) => {
    return apiClient.request<T>(endpoint, options, token);
  };

  return {
    get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
    post: <T>(endpoint: string, data: unknown) =>
      request<T>(endpoint, { method: 'POST', body: JSON.stringify(data) }),
    put: <T>(endpoint: string, data: unknown) =>
      request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
    delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
  };
};