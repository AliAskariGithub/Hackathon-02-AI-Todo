interface AnalyticsStats {
  all_users: number;
  total_tasks: number;
  uptime_hours: number;
  server_status: string;
}

class AnalyticsService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';
  }

  async getStats(): Promise<AnalyticsStats> {
    try {
      const response = await fetch(`${this.baseUrl}/api/analytics/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Disable cache for fresh data
        cache: 'no-cache',
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch analytics: ${response.statusText}`);
      }

      const data: AnalyticsStats = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching analytics stats:', error);
      // Return default values in case of error
      return {
        all_users: 0,
        total_tasks: 0,
        uptime_hours: 0,
        server_status: 'offline'
      };
    }
  }
}

export const analyticsService = new AnalyticsService();
export type { AnalyticsStats };