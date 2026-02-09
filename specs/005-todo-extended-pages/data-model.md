# Data Model: Extended Pages & Carousel

**Feature**: Extended Pages & Carousel
**Date**: 2026-02-05
**Status**: Draft

## Overview
This feature primarily focuses on UI enhancements and new pages but still involves some data models for form inputs and testimonial display.

## Form Data Models

### ContactForm
Represents data for the contact form submission

- **name**: string - User's full name
- **email**: string - User's email address (validation: email format)
- **subject**: string - Subject of the message (min length: 5)
- **message**: string - Message content (min length: 10)
- **createdAt**: Date - Timestamp of submission

### UserProfile
Represents user profile data for settings page

- **userId**: string - Unique identifier for the user
- **name**: string - Full name of the user
- **email**: string - Email address
- **avatarUrl**: string? - URL to user's profile picture (optional)
- **bio**: string? - User biography (optional)
- **updatedAt**: Date - Last updated timestamp

## Testimonial Model

### Testimonial
Represents a single testimonial for the carousel

- **id**: string - Unique identifier for the testimonial
- **author**: string - Name of the person giving the testimonial
- **position**: string? - Job title or position of the author (optional)
- **company**: string? - Company name of the author (optional)
- **quote**: string - The testimonial content
- **rating**: number? - Rating score (1-5) (optional)
- **avatar**: string? - Avatar URL of the author (optional)
- **createdAt**: Date - Date when testimonial was created

## Settings Preferences Model

### UserPreferences
Represents user-specific preferences

- **userId**: string - Reference to the user
- **theme**: string - Preferred theme ('light'|'dark'|'system')
- **notifications**: object - Notification settings
  - emailNotifications: boolean - Enable email notifications
  - pushNotifications: boolean - Enable push notifications
  - smsNotifications: boolean? - Enable SMS notifications (optional)
- **privacy**: object - Privacy settings
  - profileVisibility: string - Who can see profile ('public'|'registered-users'|'followers-only')
  - dataSharing: boolean - Allow data sharing with partners
- **updatedAt**: Date - Last updated timestamp

## Carousel Configuration Model

### CarouselSettings
Represents configuration for the testimonial carousel

- **itemsPerPage**: number - Number of testimonials to display simultaneously (default: 3)
- **autoPlayInterval**: number - Interval in milliseconds for automatic rotation (default: 5000)
- **transitionDuration**: number - Duration in milliseconds for transition animation (default: 500)
- **enableNavigation**: boolean - Whether to show navigation arrows
- **enableDots**: boolean - Whether to show dot indicators
- **pauseOnHover**: boolean - Pause autoplay when hovering over carousel

## Footer Navigation Model

### FooterLink
Represents a single link in the footer navigation

- **id**: string - Unique identifier
- **title**: string - Link title
- **url**: string - Target URL
- **category**: string - Category group ('pages'|'legal'|'resources')

### SocialLink
Represents a social media link in the footer

- **id**: string - Unique identifier
- **platform**: string - Social media platform ('twitter'|'github'|'linkedin'|'facebook'|'instagram')
- **url**: string - Profile URL on the platform
- **icon**: string - Icon identifier for the platform

## Validation Rules

### Contact Form Validation
- **name**: Required, minimum 2 characters
- **email**: Required, valid email format
- **subject**: Required, minimum 5 characters
- **message**: Required, minimum 10 characters

### User Profile Validation
- **name**: Required, minimum 2 characters
- **email**: Required, valid email format
- **bio**: Optional, maximum 280 characters

## State Models

### FormState
Represents the state of a form component

- **isSubmitting**: boolean - Whether the form is currently submitting
- **isSubmitted**: boolean - Whether the form has been successfully submitted
- **errors**: object - Field-specific validation errors
- **successMessage**: string? - Success message to display after submission

### CarouselState
Represents the state of the carousel component

- **currentIndex**: number - Index of currently visible testimonial chunk
- **totalPages**: number - Total number of pages in the carousel
- **isPlaying**: boolean - Whether the auto-rotation is active
- **hovered**: boolean - Whether mouse is hovering over the carousel