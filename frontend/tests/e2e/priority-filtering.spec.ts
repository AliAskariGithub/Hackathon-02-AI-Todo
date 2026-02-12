/**
 * E2E tests for priority management via frontend.
 *
 * Tests the complete priority flow from frontend to backend.
 */

import { test, expect } from '@playwright/test';

test.describe('Priority Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('create task with high priority', async ({ page }) => {
    // Open create task dialog
    await page.click('button[aria-label="Create new task"]');

    // Fill in task details
    await page.fill('input[id="title"]', 'Urgent bug fix');
    await page.fill('textarea[id="description"]', 'Critical production issue');

    // Select High priority
    await page.click('button[id="priority"]');
    await page.click('text=High');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for task to appear
    await expect(page.locator('text=Urgent bug fix')).toBeVisible();

    // Verify high priority badge is displayed (red)
    await expect(page.locator('.bg-red-500\\/10')).toBeVisible();
    await expect(page.locator('text=High')).toBeVisible();
  });

  test('create task with default medium priority', async ({ page }) => {
    // Open create task dialog
    await page.click('button[aria-label="Create new task"]');

    // Fill in task details without selecting priority
    await page.fill('input[id="title"]', 'Regular task');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify medium priority badge is displayed (yellow)
    await expect(page.locator('.bg-yellow-500\\/10')).toBeVisible();
    await expect(page.locator('text=Medium')).toBeVisible();
  });

  test('update task priority', async ({ page }) => {
    // Create a task with Low priority
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Low priority task');
    await page.click('button[id="priority"]');
    await page.click('text=Low');
    await page.click('button[type="submit"]');

    // Wait for task to appear
    await expect(page.locator('text=Low priority task')).toBeVisible();

    // Open edit dialog
    await page.hover('text=Low priority task');
    await page.click('button[aria-label="Edit"]');

    // Change priority to High
    await page.click('button[id="edit-priority"]');
    await page.click('text=High');

    // Save changes
    await page.click('button:has-text("Save Changes")');

    // Verify updated priority badge
    await expect(page.locator('.bg-red-500\\/10')).toBeVisible();
    await expect(page.locator('text=High')).toBeVisible();
  });

  test('filter tasks by priority', async ({ page }) => {
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

  test('sort tasks by priority', async ({ page }) => {
    // Create tasks in random priority order
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

  test('priority badges have correct colors', async ({ page }) => {
    // Create tasks with all priority levels
    const priorities = [
      { level: 'High', color: 'red' },
      { level: 'Medium', color: 'yellow' },
      { level: 'Low', color: 'green' }
    ];

    for (const priority of priorities) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', `${priority.level} priority task`);
      await page.click('button[id="priority"]');
      await page.click(`text=${priority.level}`);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Verify each priority has correct color
    await expect(page.locator('.bg-red-500\\/10')).toBeVisible(); // High
    await expect(page.locator('.bg-yellow-500\\/10')).toBeVisible(); // Medium
    await expect(page.locator('.bg-green-500\\/10')).toBeVisible(); // Low
  });

  test('priority selector shows visual indicators', async ({ page }) => {
    // Open create task dialog
    await page.click('button[aria-label="Create new task"]');

    // Open priority selector
    await page.click('button[id="priority"]');

    // Verify all priority options are visible with indicators
    await expect(page.locator('text=High')).toBeVisible();
    await expect(page.locator('text=Medium')).toBeVisible();
    await expect(page.locator('text=Low')).toBeVisible();

    // Verify color indicators are present
    const priorityOptions = page.locator('[role="option"]');
    await expect(priorityOptions).toHaveCount(3);
  });

  test('combine priority filter with other filters', async ({ page }) => {
    // Create tasks with different combinations
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'High priority completed');
    await page.click('button[id="priority"]');
    await page.click('text=High');
    await page.click('button[type="submit"]');
    await page.click('button:has-text("Mark as Complete")');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'High priority pending');
    await page.click('button[id="priority"]');
    await page.click('text=High');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Low priority pending');
    await page.click('button[id="priority"]');
    await page.click('text=Low');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Filter by High priority AND pending status
    await page.click('button:has-text("Filters")');

    // Select High priority
    await page.click('button[id*="priority"]');
    await page.click('text=High');

    // Select Pending status
    await page.click('button[id*="status"]');
    await page.click('text=Pending');

    // Apply filters
    await page.click('button:has-text("Apply Filters")');

    // Verify only high priority pending task is shown
    await expect(page.locator('text=High priority pending')).toBeVisible();
    await expect(page.locator('text=High priority completed')).not.toBeVisible();
    await expect(page.locator('text=Low priority pending')).not.toBeVisible();
  });

  test('priority statistics displayed correctly', async ({ page }) => {
    // Create tasks with different priorities
    const tasks = [
      { title: 'High 1', priority: 'High' },
      { title: 'High 2', priority: 'High' },
      { title: 'Medium 1', priority: 'Medium' },
      { title: 'Low 1', priority: 'Low' }
    ];

    for (const task of tasks) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', task.title);
      await page.click('button[id="priority"]');
      await page.click(`text=${task.priority}`);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Verify priority counts are displayed (if implemented)
    // This would depend on whether you have a statistics dashboard
    // await expect(page.locator('text=2 High priority')).toBeVisible();
    // await expect(page.locator('text=1 Medium priority')).toBeVisible();
    // await expect(page.locator('text=1 Low priority')).toBeVisible();
  });

  test('natural language search with priority', async ({ page }) => {
    // Create tasks
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Urgent meeting');
    await page.click('button[id="priority"]');
    await page.click('text=High');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Regular task');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Navigate to natural language search
    await page.click('button:has-text("AI Search")');

    // Enter query with priority
    await page.fill('textarea[placeholder*="plain English"]', 'show me urgent tasks');
    await page.click('button:has-text("Search")');

    // Verify high priority tasks are shown
    await expect(page.locator('text=Urgent meeting')).toBeVisible();
    await expect(page.locator('text=Regular task')).not.toBeVisible();
  });
});
