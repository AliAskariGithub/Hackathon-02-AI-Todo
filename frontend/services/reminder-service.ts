/**
 * Reminder service for frontend API calls.
 *
 * Handles reminder scheduling, retrieval, and cancellation via Dapr Service Invocation.
 */

interface Reminder {
  id: string;
  task_id: string;
  user_id: string;
  scheduled_time: string;
  status: 'scheduled' | 'sent' | 'cancelled';
  created_at: string;
  sent_at?: string;
  dapr_job_name?: string;
}

interface ReminderCreate {
  task_id: string;
  user_id: string;
  scheduled_time: string;
}

class ReminderService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL || 'http://localhost:8000';

  /**
   * Schedule a new reminder for a task
   * @param userId The ID of the user
   * @param taskId The ID of the task
   * @param scheduledTime The time to send the reminder (ISO 8601 format)
   * @param token The authentication token
   * @returns The created reminder
   */
  async scheduleReminder(userId: string, taskId: string, scheduledTime: Date, token: string): Promise<Reminder> {
    try {
      const reminderData: ReminderCreate = {
        task_id: taskId,
        user_id: userId,
        scheduled_time: scheduledTime.toISOString(),
      };

      const response = await fetch(`${this.baseUrl}/api/reminders`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reminderData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 400) {
          const error = await response.json();
          throw new Error(error.detail || 'Invalid reminder data');
        } else {
          throw new Error(`Failed to schedule reminder: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error scheduling reminder:', error);
      throw error;
    }
  }

  /**
   * Get all reminders for a user with optional filtering
   * @param userId The ID of the user
   * @param token The authentication token
   * @param taskId Optional task ID filter
   * @param status Optional status filter
   * @returns Array of reminders
   */
  async getReminders(
    userId: string,
    token: string,
    taskId?: string,
    status?: 'scheduled' | 'sent' | 'cancelled'
  ): Promise<Reminder[]> {
    try {
      const params = new URLSearchParams();
      if (taskId) params.append('task_id', taskId);
      if (status) params.append('status', status);

      const url = `${this.baseUrl}/api/reminders${params.toString() ? `?${params.toString()}` : ''}`;

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
        } else {
          throw new Error(`Failed to fetch reminders: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching reminders:', error);
      throw error;
    }
  }

  /**
   * Get a specific reminder by ID
   * @param userId The ID of the user
   * @param reminderId The ID of the reminder
   * @param token The authentication token
   * @returns The requested reminder
   */
  async getReminderById(userId: string, reminderId: string, token: string): Promise<Reminder> {
    try {
      const response = await fetch(`${this.baseUrl}/api/reminders/${reminderId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 404) {
          throw new Error('Reminder not found');
        } else {
          throw new Error(`Failed to fetch reminder: ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching reminder:', error);
      throw error;
    }
  }

  /**
   * Cancel a scheduled reminder
   * @param userId The ID of the user
   * @param reminderId The ID of the reminder to cancel
   * @param token The authentication token
   * @returns Promise that resolves when cancellation is complete
   */
  async cancelReminder(userId: string, reminderId: string, token: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/reminders/${reminderId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized: Invalid or expired token');
        } else if (response.status === 404) {
          throw new Error('Reminder not found');
        } else if (response.status === 400) {
          const error = await response.json();
          throw new Error(error.detail || 'Cannot cancel reminder');
        } else {
          throw new Error(`Failed to cancel reminder: ${response.statusText}`);
        }
      }
    } catch (error) {
      console.error('Error cancelling reminder:', error);
      throw error;
    }
  }
}

const reminderService = new ReminderService();
export default reminderService;
