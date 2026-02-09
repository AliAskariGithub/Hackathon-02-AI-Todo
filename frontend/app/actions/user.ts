'use server';

import { revalidatePath } from 'next/cache';

/**
 * Server Action to update user profile information
 * @param formData - Form data containing updated profile information
 * @returns Object with success status and message
 */
export async function updateProfile(formData: FormData): Promise<{ success: boolean; message: string; errors?: Record<string, string[]> }> {
  try {
    // In a real implementation, we would verify the user is authenticated
    // For this example, we'll skip authentication verification in the server action
    // and instead rely on the page to ensure authentication before calling this function

    // Extract the fields from the form data
    const name = formData.get('name') as string;
    const bio = formData.get('bio') as string;

    // Validate inputs
    const errors: Record<string, string[]> = {};

    if (name && name.trim().length < 2) {
      errors.name = ['Name must be at least 2 characters'];
    }

    if (bio && bio.length > 280) {
      errors.bio = ['Bio must not exceed 280 characters'];
    }

    if (Object.keys(errors).length > 0) {
      return {
        success: false,
        message: 'Validation failed',
        errors
      };
    }

    // In a real implementation, this would update the user in the database
    // For this demo, we'll simulate the update
    console.log(`Updating user profile with token:`, { name, bio });

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // In a real implementation, you would call the Better Auth API to update the user
    // This would require calling the API endpoint directly or using Better Auth's server API
    // await fetch(`${process.env.AUTH_URL}/api/users/update`, {
    //   method: 'PUT',
    //   headers: {
    //     'Authorization': `Bearer ${token}`,
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     name,
    //     bio,
    //   }),
    // });

    // Revalidate the settings page to show updated data
    revalidatePath('/settings');

    return {
      success: true,
      message: 'Profile updated successfully'
    };
  } catch (error) {
    console.error('Error updating profile:', error);
    return {
      success: false,
      message: 'An error occurred while updating your profile'
    };
  }
}