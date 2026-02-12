interface Task {
  id: string;
  title: string;
  description?: string;
  status: string; // 'pending' | 'in_progress' | 'completed' | 'deleted'
  priority: string; // 'High' | 'Medium' | 'Low'
  due_date?: string;
  recurrence?: string | null; // 'Daily' | 'Weekly' | 'Monthly'
  recurrence_day_of_week?: number | null; // 0-6 for Weekly
  recurrence_day_of_month?: number | null; // 1-31 for Monthly
  tags?: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  parent_task_id?: string | null;
  correlation_id?: string | null;
  // Backward compatibility
  completed?: boolean;
}

interface TaskFilters {
  status?: string;
  priority?: string;
  has_recurrence?: boolean;
}

interface CompleteTaskResponse {
  task: Task;
  message: string;
  has_recurrence: boolean;
  next_instance_will_be_generated: boolean;
}

class TaskService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

  /**
   * Get all tasks for a user with optional filtering
   * @param userId The ID of the user
   * @param token The authentication token
   * @param filters Optional filters (status, priority, has_recurrence)
   * @returns Array of tasks
   */
  async getUserTasks(userId: string, token: string, filters?: TaskFilters): Promise<Task[]> {
    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.priority) params.append('priority', filters.priority);
      if (filters?.has_recurrence !== undefined) params.append('has_recurrence', filters.has_recurrence.toString());

      const url = `${this.baseUrl}/api/${userId}/tasks${params.toString() ? `?${params.toString()}` : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to these tasks');
        } else {
          throw new Error(`Failed to fetch tasks: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user tasks:', error);
      throw error;
    }
  }

  /**
   * Create a new task for a user
   * @param userId The ID of the user
   * @param taskData The task data to create
   * @param token The authentication token
   * @returns The created task
   */
  async createTask(userId: string, taskData: Partial<Task>, token: string): Promise<Task> {
    try {
      const response = await fetch(`${this.baseUrl}/api/${userId}/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to create tasks for this user');
        } else {
          throw new Error(`Failed to create task: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  /**
   * Get a specific task by ID for a user
   * @param userId The ID of the user
   * @param taskId The ID of the task
   * @param token The authentication token
   * @returns The requested task
   */
  async getTaskById(userId: string, taskId: string, token: string): Promise<Task> {
    try {
      const response = await fetch(`${this.baseUrl}/api/${userId}/tasks/${taskId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to this task');
        } else if (response.status === 404) {
          throw new Error('Task not found');
        } else {
          throw new Error(`Failed to fetch task: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching task:', error);
      throw error;
    }
  }

  /**
   * Update a specific task for a user
   * @param userId The ID of the user
   * @param taskId The ID of the task to update
   * @param taskData The updated task data
   * @param token The authentication token
   * @returns The updated task
   */
  async updateTask(userId: string, taskId: string, taskData: Partial<Task>, token: string): Promise<Task> {
    try {
      const response = await fetch(`${this.baseUrl}/api/${userId}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to update this task');
        } else if (response.status === 404) {
          throw new Error('Task not found');
        } else {
          throw new Error(`Failed to update task: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  }

  /**
   * Delete a specific task for a user
   * @param userId The ID of the user
   * @param taskId The ID of the task to delete
   * @param token The authentication token
   * @returns Promise that resolves when deletion is complete
   */
  async deleteTask(userId: string, taskId: string, token: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/${userId}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to delete this task');
        } else if (response.status === 404) {
          throw new Error('Task not found');
        } else {
          throw new Error(`Failed to delete task: ${response.statusText}`);
        }
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      throw error;
    }
  }

  /**
   * Mark a task as completed (triggers recurring task generation if applicable)
   * @param userId The ID of the user
   * @param taskId The ID of the task to complete
   * @param token The authentication token
   * @returns Response with completed task and next instance info
   */
  async completeTask(userId: string, taskId: string, token: string): Promise<CompleteTaskResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/${userId}/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 403) {
          throw new Error('Forbidden: You do not have access to complete this task');
        } else if (response.status === 404) {
          throw new Error('Task not found');
        } else {
          throw new Error(`Failed to complete task: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error completing task:', error);
      throw error;
    }
  }
}

const taskService = new TaskService();
export default taskService;