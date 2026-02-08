
class ApiClient {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

  /**
   * Generic method to make authenticated API requests
   * @param endpoint The API endpoint to call
   * @param options Request options including method, headers, body
   * @param token Optional token to use for authentication
   * @returns Promise with the response data
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    token?: string
  ): Promise<T> {
    // If no token is provided explicitly, try to get it from localStorage
    // Only add authorization header if a token is provided (either explicitly or from storage)
    // Don't add auth header for login/register endpoints
    const shouldIncludeAuth = !endpoint.includes('/login') && !endpoint.includes('/register');
    const authToken = token || (shouldIncludeAuth ? localStorage.getItem('auth-token') : null);

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);

      // Handle authentication errors
      if (response.status === 401) {
        // Token might be expired or invalid
        // Remove the invalid token and optionally redirect to login
        localStorage.removeItem('auth-token');
        console.warn('Unauthorized access - token may be expired or invalid. Logging out.');

        // Optionally redirect to login (but don't do this directly in API client)
        throw new Error('Unauthorized: Invalid or expired token');
      }

      if (response.status === 403) {
        // User doesn't have permission for this resource
        throw new Error('Forbidden: You do not have access to this resource');
      }

      if (!response.ok) {
        // Handle other HTTP errors
        const errorText = await response.text();
        throw new Error(`HTTP Error: ${response.status} - ${errorText}`);
      }

      // For DELETE requests, there might not be a response body
      if (response.status === 204) {
        return undefined as unknown as T; // 204 No Content
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * GET request with authentication
   */
  async get<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, token);
  }

  /**
   * POST request with authentication
   */
  async post<T>(endpoint: string, data: unknown, token?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      token
    );
  }

  /**
   * PUT request with authentication
   */
  async put<T>(endpoint: string, data: unknown, token?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      },
      token
    );
  }

  /**
   * DELETE request with authentication
   */
  async delete(endpoint: string, token?: string): Promise<void> {
    await this.request(
      endpoint,
      {
        method: 'DELETE',
      },
      token
    );
  }
}

const apiClient = new ApiClient();
export default apiClient;