/**
 * E2E tests for advanced search and filtering via frontend.
 *
 * Tests the complete search, filter, and sort flow from frontend to backend.
 */

import { test, expect } from '@playwright/test';

test.describe('Advanced Search and Filtering E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('keyword search finds matching tasks', async ({ page }) => {
    // Create tasks with different titles
    const tasks = [
      'Team meeting preparation',
      'Client meeting notes',
      'Code review session'
    ];

    for (const title of tasks) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', title);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Search for "meeting"
    await page.fill('input[placeholder*="Search"]', 'meeting');
    await page.click('button:has-text("Search")');

    // Verify only matching tasks are shown
    await expect(page.locator('text=Team meeting preparation')).toBeVisible();
    await expect(page.locator('text=Client meeting notes')).toBeVisible();
    await expect(page.locator('text=Code review session')).not.toBeVisible();
  });

  test('filter by priority', async ({ page }) => {
    // Create tasks with different priorities
    const tasks = [
      { title: 'High priority task', priority: 'High' },
      { title: 'Medium priority task', priority: 'Medium' },
      { title: 'Low priority task', priority: 'Low' }
    ];

    for (const task of tasks) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', task.title);
      await page.click('button[id="priority"]');
      await page.click(`text=${task.priority}`);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Open filter panel
    await page.click('button:has-text("Filters")');

    // Select High priority filter
    await page.click('button[id*="priority"]');
    await page.click('text=High');

    // Apply filters
    await page.click('button:has-text("Apply Filters")');

    // Verify only high priority tasks are shown
    await expect(page.locator('text=High priority task')).toBeVisible();
    await expect(page.locator('text=Medium priority task')).not.toBeVisible();
    await expect(page.locator('text=Low priority task')).not.toBeVisible();
  });

  test('filter by status', async ({ page }) => {
    // Create and complete a task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Completed task');
    await page.click('button[type="submit"]');

    await page.click('button:has-text("Mark as Complete")');
    await page.waitForTimeout(500);

    // Create a pending task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Pending task');
    await page.click('button[type="submit"]');

    // Filter by completed status
    await page.click('button:has-text("Filters")');
    await page.click('button[id*="status"]');
    await page.click('text=Completed');
    await page.click('button:has-text("Apply Filters")');

    // Verify only completed tasks are shown
    await expect(page.locator('text=Completed task')).toBeVisible();
    await expect(page.locator('text=Pending task')).not.toBeVisible();
  });

  test('filter by tags', async ({ page }) => {
    // Create tasks with different tags
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Work task');
    await page.fill('input[id="tags"]', 'work, urgent');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Personal task');
    await page.fill('input[id="tags"]', 'personal');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Filter by work tag
    await page.click('button:has-text("Filters")');
    await page.click('text=work');
    await page.click('button:has-text("Apply Filters")');

    // Verify only work-tagged tasks are shown
    await expect(page.locator('text=Work task')).toBeVisible();
    await expect(page.locator('text=Personal task')).not.toBeVisible();
  });

  test('sort by priority', async ({ page }) => {
    // Create tasks with different priorities
    const tasks = [
      { title: 'Low task', priority: 'Low' },
      { title: 'High task', priority: 'High' },
      { title: 'Medium task', priority: 'Medium' }
    ];

    for (const task of tasks) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', task.title);
      await page.click('button[id="priority"]');
      await page.click(`text=${task.priority}`);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Sort by priority
    await page.click('button:has-text("Sort")');
    await page.click('text=Priority');

    // Verify tasks are sorted by priority (High, Medium, Low)
    const taskCards = page.locator('[data-testid="task-card"]');
    const firstTask = taskCards.first();
    await expect(firstTask).toContainText('High task');
  });

  test('natural language search', async ({ page }) => {
    // Create tasks
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Urgent meeting');
    await page.click('button[id="priority"]');
    await page.click('text=High');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Normal task');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Navigate to natural language search
    await page.click('button:has-text("AI Search")');

    // Enter natural language query
    await page.fill('textarea[placeholder*="plain English"]', 'show me high priority tasks');
    await page.click('button:has-text("Search")');

    // Verify parsed filters are shown
    await expect(page.locator('text=High priority')).toBeVisible();

    // Verify only high priority tasks in results
    await expect(page.locator('text=Urgent meeting')).toBeVisible();
    await expect(page.locator('text=Normal task')).not.toBeVisible();
  });

  test('pagination works correctly', async ({ page }) => {
    // Create many tasks
    for (let i = 1; i <= 25; i++) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', `Task ${i}`);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(200);
    }

    // Verify pagination controls appear
    await expect(page.locator('button:has-text("Next")')).toBeVisible();

    // Click next page
    await page.click('button:has-text("Next")');

    // Verify different tasks are shown
    await expect(page.locator('text=Page 2')).toBeVisible();
  });

  test('clear filters resets search', async ({ page }) => {
    // Apply filters
    await page.click('button:has-text("Filters")');
    await page.click('button[id*="priority"]');
    await page.click('text=High');
    await page.click('button:has-text("Apply Filters")');

    // Verify filter badge shows
    await expect(page.locator('text=1')).toBeVisible(); // Filter count badge

    // Clear filters
    await page.click('button:has-text("Filters")');
    await page.click('button:has-text("Clear all")');

    // Verify all tasks are shown again
    await expect(page.locator('text=1')).not.toBeVisible(); // Filter count badge gone
  });

  test('combine search and filters', async ({ page }) => {
    // Create tasks
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'High priority meeting');
    await page.click('button[id="priority"]');
    await page.click('text=High');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Low priority meeting');
    await page.click('button[id="priority"]');
    await page.click('text=Low');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Search for "meeting"
    await page.fill('input[placeholder*="Search"]', 'meeting');
    await page.click('button:has-text("Search")');

    // Apply high priority filter
    await page.click('button:has-text("Filters")');
    await page.click('button[id*="priority"]');
    await page.click('text=High');
    await page.click('button:has-text("Apply Filters")');

    // Verify only high priority meeting is shown
    await expect(page.locator('text=High priority meeting')).toBeVisible();
    await expect(page.locator('text=Low priority meeting')).not.toBeVisible();
  });
});
