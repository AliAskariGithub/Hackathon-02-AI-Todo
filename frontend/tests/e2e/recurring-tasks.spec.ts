/**
 * E2E tests for recurring tasks via frontend.
 *
 * Tests the complete flow from frontend to backend for recurring task creation.
 */

import { test, expect } from '@playwright/test';

test.describe('Recurring Tasks E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('create daily recurring task', async ({ page }) => {
    // Open create task dialog
    await page.click('button[aria-label="Create new task"]');

    // Fill in task details
    await page.fill('input[id="title"]', 'Daily standup');
    await page.fill('textarea[id="description"]', 'Team standup meeting');

    // Select priority
    await page.click('button[id="priority"]');
    await page.click('text=High');

    // Select recurrence
    await page.click('button[id="recurrence"]');
    await page.click('text=Daily');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for task to appear in list
    await expect(page.locator('text=Daily standup')).toBeVisible();

    // Verify recurrence indicator is displayed
    await expect(page.locator('text=Daily')).toBeVisible();

    // Verify priority badge is displayed
    await expect(page.locator('.bg-red-500\\/10')).toBeVisible();
  });

  test('create weekly recurring task with day of week', async ({ page }) => {
    await page.click('button[aria-label="Create new task"]');

    await page.fill('input[id="title"]', 'Weekly review');
    await page.fill('textarea[id="description"]', 'Team weekly review');

    // Select recurrence
    await page.click('button[id="recurrence"]');
    await page.click('text=Weekly');

    // Select day of week
    await page.click('button[id="day-of-week"]');
    await page.click('text=Friday');

    await page.click('button[type="submit"]');

    // Verify task appears with weekly indicator
    await expect(page.locator('text=Weekly review')).toBeVisible();
    await expect(page.locator('text=Weekly')).toBeVisible();
    await expect(page.locator('text=Fri')).toBeVisible();
  });

  test('create monthly recurring task with day of month', async ({ page }) => {
    await page.click('button[aria-label="Create new task"]');

    await page.fill('input[id="title"]', 'Monthly report');
    await page.fill('textarea[id="description"]', 'Submit monthly report');

    // Select recurrence
    await page.click('button[id="recurrence"]');
    await page.click('text=Monthly');

    // Select day of month
    await page.click('button[id="day-of-month"]');
    await page.click('text=1st');

    await page.click('button[type="submit"]');

    // Verify task appears with monthly indicator
    await expect(page.locator('text=Monthly report')).toBeVisible();
    await expect(page.locator('text=Monthly')).toBeVisible();
    await expect(page.locator('text=1st')).toBeVisible();
  });

  test('complete recurring task shows next instance notification', async ({ page }) => {
    // Create a daily recurring task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Daily exercise');
    await page.click('button[id="recurrence"]');
    await page.click('text=Daily');
    await page.click('button[type="submit"]');

    // Wait for task to appear
    await expect(page.locator('text=Daily exercise')).toBeVisible();

    // Complete the task
    await page.click('button:has-text("Mark as Complete")');

    // Verify success notification with recurrence info
    await expect(page.locator('text=Next daily instance will be generated')).toBeVisible();
  });

  test('filter recurring tasks', async ({ page }) => {
    // Create multiple tasks with different recurrence patterns
    const tasks = [
      { title: 'Daily task', recurrence: 'Daily' },
      { title: 'Weekly task', recurrence: 'Weekly' },
      { title: 'One-time task', recurrence: null }
    ];

    for (const task of tasks) {
      await page.click('button[aria-label="Create new task"]');
      await page.fill('input[id="title"]', task.title);
      if (task.recurrence) {
        await page.click('button[id="recurrence"]');
        await page.click(`text=${task.recurrence}`);
        if (task.recurrence === 'Weekly') {
          await page.click('button[id="day-of-week"]');
          await page.click('text=Monday');
        }
      }
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Apply recurrence filter
    await page.click('button:has-text("All Tasks")');
    await page.click('text=All Recurring');

    // Verify only recurring tasks are shown
    await expect(page.locator('text=Daily task')).toBeVisible();
    await expect(page.locator('text=Weekly task')).toBeVisible();
    await expect(page.locator('text=One-time task')).not.toBeVisible();
  });

  test('edit recurring task updates recurrence fields', async ({ page }) => {
    // Create a daily recurring task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Original task');
    await page.click('button[id="recurrence"]');
    await page.click('text=Daily');
    await page.click('button[type="submit"]');

    // Wait for task to appear
    await expect(page.locator('text=Original task')).toBeVisible();

    // Open edit dialog
    await page.hover('text=Original task');
    await page.click('button[aria-label="Edit"]');

    // Change recurrence to Weekly
    await page.click('button[id="edit-recurrence"]');
    await page.click('text=Weekly');

    // Select day of week
    await page.click('button[id="edit-day-of-week"]');
    await page.click('text=Wednesday');

    // Save changes
    await page.click('button:has-text("Save Changes")');

    // Verify updated recurrence indicator
    await expect(page.locator('text=Weekly')).toBeVisible();
    await expect(page.locator('text=Wed')).toBeVisible();
  });

  test('display tags and due dates on task cards', async ({ page }) => {
    await page.click('button[aria-label="Create new task"]');

    await page.fill('input[id="title"]', 'Tagged task');
    await page.fill('input[id="tags"]', 'urgent, work, meeting');

    // Set due date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().slice(0, 16);
    await page.fill('input[id="due-date"]', dateString);

    await page.click('button[type="submit"]');

    // Verify tags are displayed (first 2 + count)
    await expect(page.locator('text=urgent')).toBeVisible();
    await expect(page.locator('text=work')).toBeVisible();
    await expect(page.locator('text=+1')).toBeVisible();

    // Verify due date is displayed
    await expect(page.locator('[class*="bg-purple-500"]')).toBeVisible();
  });
});
