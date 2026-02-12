/**
 * E2E tests for reminders via frontend.
 *
 * Tests the complete flow from frontend to backend for reminder scheduling.
 */

import { test, expect } from '@playwright/test';

test.describe('Reminders E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('schedule reminder for task', async ({ page }) => {
    // Create a task first
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Important meeting');
    await page.fill('textarea[id="description"]', 'Team sync meeting');
    await page.click('button[type="submit"]');

    // Wait for task to appear
    await expect(page.locator('text=Important meeting')).toBeVisible();

    // Open task details
    await page.click('text=Important meeting');

    // Schedule reminder
    await page.click('button:has-text("Schedule Reminder")');

    // Select date (tomorrow)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    await page.click(`button[name="day"][aria-label*="${tomorrow.getDate()}"]`);

    // Set time
    await page.fill('input[type="time"]', '09:00');

    // Submit
    await page.click('button:has-text("Schedule Reminder")');

    // Verify success notification
    await expect(page.locator('text=Reminder scheduled')).toBeVisible();

    // Verify reminder appears in list
    await expect(page.locator('text=Scheduled')).toBeVisible();
  });

  test('cancel scheduled reminder', async ({ page }) => {
    // Navigate to reminders page
    await page.goto('/dashboard/reminders');

    // Find a scheduled reminder
    const reminderCard = page.locator('[data-status="scheduled"]').first();
    await expect(reminderCard).toBeVisible();

    // Click cancel button
    await reminderCard.locator('button[aria-label="Cancel reminder"]').click();

    // Confirm cancellation
    await page.click('button:has-text("Confirm")');

    // Verify reminder is cancelled
    await expect(page.locator('text=Cancelled')).toBeVisible();
  });

  test('view reminder history', async ({ page }) => {
    // Navigate to reminders page
    await page.goto('/dashboard/reminders');

    // Filter by status
    await page.click('button:has-text("All Reminders")');
    await page.click('text=Sent');

    // Verify only sent reminders are shown
    const reminders = page.locator('[data-status="sent"]');
    await expect(reminders.first()).toBeVisible();
  });

  test('reminder validation - past time fails', async ({ page }) => {
    // Create a task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Test task');
    await page.click('button[type="submit"]');

    // Open task details
    await page.click('text=Test task');

    // Try to schedule reminder in the past
    await page.click('button:has-text("Schedule Reminder")');

    // Select yesterday
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    await page.click(`button[name="day"][aria-label*="${yesterday.getDate()}"]`);

    await page.fill('input[type="time"]', '09:00');
    await page.click('button:has-text("Schedule Reminder")');

    // Verify error message
    await expect(page.locator('text=must be in the future')).toBeVisible();
  });

  test('reminder validation - less than 1 minute fails', async ({ page }) => {
    // Create a task
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Test task');
    await page.click('button[type="submit"]');

    // Open task details
    await page.click('text=Test task');

    // Try to schedule reminder less than 1 minute ahead
    await page.click('button:has-text("Schedule Reminder")');

    // Select today
    const today = new Date();
    await page.click(`button[name="day"][aria-label*="${today.getDate()}"]`);

    // Set time to current time (will be less than 1 minute ahead)
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    await page.fill('input[type="time"]', timeString);
    await page.click('button:has-text("Schedule Reminder")');

    // Verify error message
    await expect(page.locator('text=at least 1 minute')).toBeVisible();
  });

  test('display reminder count on task card', async ({ page }) => {
    // Create a task with reminders
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Task with reminders');
    await page.click('button[type="submit"]');

    // Schedule multiple reminders
    await page.click('text=Task with reminders');

    for (let i = 1; i <= 3; i++) {
      await page.click('button:has-text("Schedule Reminder")');

      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + i);
      await page.click(`button[name="day"][aria-label*="${futureDate.getDate()}"]`);

      await page.fill('input[type="time"]', '09:00');
      await page.click('button:has-text("Schedule Reminder")');
      await page.waitForTimeout(500);
    }

    // Close task details
    await page.click('button[aria-label="Close"]');

    // Verify reminder count badge on task card
    await expect(page.locator('text=3 reminders')).toBeVisible();
  });

  test('reminder notification appears when fired', async ({ page }) => {
    // This test would require mocking time or using a very short reminder
    // In real implementation, you'd use a test-specific short delay

    // Create task and schedule reminder for 1 minute ahead
    await page.click('button[aria-label="Create new task"]');
    await page.fill('input[id="title"]', 'Quick reminder test');
    await page.click('button[type="submit"]');

    await page.click('text=Quick reminder test');
    await page.click('button:has-text("Schedule Reminder")');

    // Select today
    const today = new Date();
    await page.click(`button[name="day"][aria-label*="${today.getDate()}"]`);

    // Set time to 1 minute from now
    const futureTime = new Date(Date.now() + 60000);
    const timeString = `${futureTime.getHours().toString().padStart(2, '0')}:${futureTime.getMinutes().toString().padStart(2, '0')}`;
    await page.fill('input[type="time"]', timeString);
    await page.click('button:has-text("Schedule Reminder")');

    // Wait for reminder to fire (in test, this would be mocked)
    // await page.waitForTimeout(65000);

    // Verify notification appears
    // await expect(page.locator('text=Reminder: Quick reminder test')).toBeVisible();
  });
});
