# Data Model: Advanced UI/UX & Animations

**Feature**: Advanced UI/UX & Animations
**Date**: 2026-02-05
**Status**: Draft

## Overview
This feature is primarily a UI/UX enhancement that doesn't introduce new data models but enhances existing components with theme, animation, and loading state capabilities. The data model focuses on the state and configuration required for the enhanced UI components.

## Theme Configuration

### ThemeState
Represents the current theme configuration and preferences

- **theme**: string (dark | light) - Current active theme
- **resolvedTheme**: string (dark | light | system) - Actual theme being displayed after system preferences
- **setTheme**: function - Setter for theme preference
- **systemTheme**: string (dark | light) - User's system preference

### ThemeSettings
Represents customizable theme settings

- **primaryColor**: string - Primary accent color (#0FFF50 as default)
- **darkModeColors**: object - Color palette for dark mode
  - primaryBackground: string - Primary background color (#161616)
  - secondaryBackground: string - Secondary background color (#232323)
- **lightModeColors**: object - Color palette for light mode
  - primaryBackground: string - Primary background color (#f6f6f6)
  - secondaryBackground: string - Secondary background color (#f5f4f2)

## Animation Configuration

### AnimationState
Represents animation-related state and preferences

- **isReducedMotion**: boolean - Whether user prefers reduced motion
- **animationSpeed**: string (slow | normal | fast) - Animation speed preference
- **transitionConfig**: object - Animation transition parameters
  - type: string (spring | tween) - Animation type
  - stiffness: number - Spring stiffness value
  - damping: number - Spring damping value

## Loading State Configuration

### LoadingState
Represents loading state for various UI components

- **isLoading**: boolean - Whether a component is in loading state
- **loadingType**: string (skeleton | spinner | progress) - Type of loading indicator
- **targetDimensions**: object - Dimensions to maintain during loading
  - width: number | string
  - height: number | string

## Dashboard Card Configuration

### DashboardCard
Represents configuration for dashboard summary cards

- **type**: string (total | completed | remaining) - Card type
- **count**: number - Value to display
- **label**: string - Descriptive label
- **icon**: string - Icon identifier
- **color**: string - Color theme for the card
- **animated**: boolean - Whether to animate the counter

## Dialog Configuration

### DialogState
Represents the state of modal/dialog components

- **isOpen**: boolean - Whether the dialog is visible
- **type**: string (create-task | edit-task | confirm-action) - Purpose of the dialog
- **title**: string - Dialog title
- **content**: string - Dialog content
- **actions**: array - Available actions
- **animationProps**: object - Animation configuration for the dialog
  - initial: object - Initial animation state
  - animate: object - Animated state
  - exit: object - Exit animation state

## Font Configuration

### FontState
Represents font configuration for the application

- **headingFont**: object - Configuration for heading font
  - family: string - Font family (Montserrat)
  - weight: string - Font weight
  - isUppercase: boolean - Whether to apply uppercase styling
- **bodyFont**: object - Configuration for body text font
  - family: string - Font family (Montserrat)
  - weight: string - Regular weight
  - weights: array - Available font weights