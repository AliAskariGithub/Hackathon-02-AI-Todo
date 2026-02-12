/**
 * Search service for frontend API calls.
 *
 * Handles search, filtering, sorting, and natural language queries.
 */

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date?: string;
  recurrence?: string | null;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

interface SearchFilters {
  query?: string;
  status?: string;
  priority?: string;
  tags?: string[];
  has_recurrence?: boolean;
  due_before?: string;
  due_after?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

interface PaginatedResponse<T> {
  items: T[];
  metadata: {
    total: number;
    limit: number;
    offset: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

interface NaturalLanguageSearchResponse {
  query: string;
  parsed_filters: Record<string, unknown>;
  description: string;
  results: PaginatedResponse<Task>;
}

class SearchService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

  /**
   * Search and filter tasks with pagination
   * @param filters Search and filter criteria
   * @param token Authentication token
   * @returns Paginated search results
   */
  async searchTasks(filters: SearchFilters, token: string): Promise<PaginatedResponse<Task>> {
    try {
      const params = new URLSearchParams();

      if (filters.query) params.append('query', filters.query);
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.tags) filters.tags.forEach(tag => params.append('tags', tag));
      if (filters.has_recurrence !== undefined) params.append('has_recurrence', filters.has_recurrence.toString());
      if (filters.due_before) params.append('due_before', filters.due_before);
      if (filters.due_after) params.append('due_after', filters.due_after);
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());

      const response = await fetch(`${this.baseUrl}/api/search/tasks?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error searching tasks:', error);
      throw error;
    }
  }

  /**
   * Search tasks using natural language query
   * @param query Natural language query string
   * @param token Authentication token
   * @param limit Maximum results
   * @param offset Pagination offset
   * @returns Search results with parsed filters
   */
  async naturalLanguageSearch(
    query: string,
    token: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<NaturalLanguageSearchResponse> {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const response = await fetch(`${this.baseUrl}/api/search/natural-language?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Natural language search failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error in natural language search:', error);
      throw error;
    }
  }

  /**
   * Get all unique tags for the user
   * @param token Authentication token
   * @returns Array of unique tag strings
   */
  async getUserTags(token: string): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/search/tags`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tags: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching tags:', error);
      throw error;
    }
  }
}

const searchService = new SearchService();
export default searchService;
