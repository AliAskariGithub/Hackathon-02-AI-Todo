
class ApiClient {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

  /**
   * Generic method to make authenticated API requests.
   * Supports both cookie-based auth (local) and token-based auth (production/cross-domain).
   * Cookies are automatically included, and Bearer token is added if available.
   *
   * @param endpoint The API endpoint to call
   * @param options Request options including method, headers, body
   * @returns Promise with the response data
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Get token from localStorage for cross-domain authentication
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add Authorization header if token exists (for cross-domain auth)
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      credentials: 'include', // Include cookies for local development
      headers,
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);

      // Handle authentication errors
      if (response.status === 401) {
        // Token might be expired - try to refresh
        console.warn('Unauthorized access - attempting token refresh');

        try {
          // Attempt to refresh the token
          const refreshResponse = await fetch(`${this.baseUrl}/api/auth/refresh`, {
            method: 'POST',
            credentials: 'include'
          });

          if (refreshResponse.ok) {
            const refreshData = await refreshResponse.json();

            // Update token in localStorage if provided
            if (refreshData.access_token && typeof window !== 'undefined') {
              localStorage.setItem('access_token', refreshData.access_token);

              // Update Authorization header with new token
              if (headers['Authorization']) {
                headers['Authorization'] = `Bearer ${refreshData.access_token}`;
              }
            }

            // Token refreshed successfully, retry the original request
            console.log('Token refreshed successfully, retrying request');
            const retryConfig = {
              ...config,
              headers
            };
            const retryResponse = await fetch(`${this.baseUrl}${endpoint}`, retryConfig);

            if (!retryResponse.ok) {
              throw new Error(`HTTP Error: ${retryResponse.status}`);
            }

            if (retryResponse.status === 204) {
              return undefined as unknown as T;
            }

            return await retryResponse.json();
          } else {
            // Refresh failed - user needs to log in again
            console.error('Token refresh failed - redirecting to login');
            // Clear token from localStorage
            if (typeof window !== 'undefined') {
              localStorage.removeItem('access_token');
              window.location.href = '/login';
            }
            throw new Error('Unauthorized: Session expired. Please log in again.');
          }
        } catch (refreshError) {
          console.error('Error during token refresh:', refreshError);
          // Clear token and redirect to login on refresh failure
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
          }
          throw new Error('Unauthorized: Session expired. Please log in again.');
        }
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
   * GET request with cookie-based authentication
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  /**
   * POST request with cookie-based authentication
   */
  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  /**
   * PUT request with cookie-based authentication
   */
  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
  }

  /**
   * DELETE request with cookie-based authentication
   */
  async delete(endpoint: string): Promise<void> {
    await this.request(
      endpoint,
      {
        method: 'DELETE',
      }
    );
  }
}

const apiClient = new ApiClient();
export default apiClient;