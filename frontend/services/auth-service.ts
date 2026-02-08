import apiClient from "./api-client";

/**
 * Service for handling authentication-related operations
 */
class AuthService {
  /**
   * Get the current session information
   * @returns Session data if authenticated, null otherwise
   */
  async getCurrentSession() {
    try {
      const token = localStorage.getItem('auth-token');
      if (!token) {
        return null;
      }

      // Decode JWT token to get user info
      try {
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));

          // Return user info in the format expected by the auth context
          return {
            data: {
              user: {
                id: payload.sub || '',
                email: payload.email || '',
                name: payload.name || payload.email?.split('@')[0] || 'User',
                image: null,
                createdAt: new Date(),
                updatedAt: new Date(),
                emailVerified: true
              }
            },
            error: null
          };
        }
      } catch (decodeError) {
        console.error("Error decoding token:", decodeError);
        return null;
      }

      return null;
    } catch (error) {
      console.error("Error getting session:", error);
      return null;
    }
  }

  /**
   * Get the JWT token from the session
   * @returns JWT token string if available, null otherwise
   */
  async getJwtToken(): Promise<string | null> {
    try {
      const token = localStorage.getItem('auth-token');
      return token;
    } catch (error) {
      console.error("Error getting JWT token:", error);
      return null;
    }
  }

  /**
   * Check if the user is currently authenticated
   * @returns Boolean indicating authentication status
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      const token = localStorage.getItem('auth-token');
      if (!token) {
        return false;
      }

      // Try to get user info to verify token validity
      const userInfo = await this.getUserInfo();
      return !!userInfo;
    } catch (error) {
      console.error("Error checking authentication status:", error);
      return false;
    }
  }

  /**
   * Logout the current user
   */
  async logout(): Promise<void> {
    try {
      // Remove the auth token from localStorage
      localStorage.removeItem('auth-token');
    } catch (error) {
      console.error("Error during logout:", error);
      throw error;
    }
  }

  /**
   * Get user information from the session
   * @returns User data if authenticated, null otherwise
   */
  async getUserInfo() {
    try {
      const token = localStorage.getItem('auth-token');
      if (!token) {
        return null;
      }

      // We don't have a direct API endpoint to get user info by token
      // So we'll return the user data from localStorage if available
      // Or we can make a call to a protected endpoint to verify and get user data

      // For now, we'll just return a basic structure indicating the user is logged in
      // In a real implementation, you'd have an endpoint like /api/users/me
      return {
        // We'll return a minimal user representation
        // In practice, you'd have an endpoint to get full user data
      };
    } catch (error) {
      console.error("Error getting user info:", error);
      return null;
    }
  }

  /**
   * Get user information from the API
   * @param userId The ID of the user to retrieve
   * @returns User data if authenticated and user exists, null otherwise
   */
  async getUserById(userId: string) {
    try {
      const token = localStorage.getItem('auth-token');
      if (!token) {
        return null;
      }

      const userData = await apiClient.get(`/api/users/${userId}`, token);
      return userData;
    } catch (error) {
      console.error("Error getting user by ID:", error);
      return null;
    }
  }
}

const authService = new AuthService();
export default authService;