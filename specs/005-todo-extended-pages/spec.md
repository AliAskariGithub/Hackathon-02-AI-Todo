# Feature Specification: Extended Pages & Carousel

**Feature Branch**: `005-todo-extended-pages`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application - Spec 5: Extended Pages & Carousel

Target functionality:
- **Upgraded Auth UI:** Custom-designed Login and Signup pages using the Spec 4 color palette (#0FFF50 / #161616), replacing generic Better Auth defaults.
- **Dynamic Testimonial Carousel:** A \"Moving Carousel\" that displays 3 testimonials at once, holds for 5 seconds, and then transitions smoothly to the next set.
- **New Core Pages:**
    - **Contact:** A functional form using Shadcn 'Form' and 'Input'.
    - **User Settings:** A private dashboard section for updating user profile and preferences.
- **Comprehensive Footer:** Persistent footer containing Website Logo, organized page routes (Home, Dashboard, Settings, Contact), and Social Links (Twitter, GitHub, LinkedIn).

Focus:
- **Navigation Security:** Use `proxy.ts` to protect the `/settings` route, ensuring only authenticated users can enter.
- **Carousel Engine:** Implement a custom Framer Motion slider with an `autoPlay` interval of 5000ms.
- **Data Binding:** Ensure the User Settings page pulls live data from the Spec 2/3 auth sessions.

Success criteria:
- Testimonials rotate automatically every 5 seconds without user interaction.
- Clicking \"Settings\" in the Navbar correctly redirects to the User Settings page.
- Footer is fully responsive, stacking links vertically on mobile devices.
- Auth pages feel integrated with the \"Electric Lime\" theme.

Constraints:
- **Tooling:** Use Context7 MCP to check for any breaking changes in Next.js 16.1.2's `proxy.ts` regarding complex route nesting.
- **Performance:** Carousel must use `AnimatePresence` for exit animations to prevent layout jumps."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enhanced Authentication Experience (Priority: P1)

As a user of the todo application, I want custom-designed Login and Signup pages with the Electric Lime theme so that I have a consistent and branded authentication experience that feels integrated with the rest of the application.

**Why this priority**: Authentication is the first touchpoint for users and sets the tone for the entire application. A cohesive design increases user trust and engagement.

**Independent Test**: The login and signup pages display the custom color palette (#0FFF50 / #161616) with consistent styling that matches the application's overall theme.

**Acceptance Scenarios**:

1. **Given** I am on the login page, **When** I enter my credentials, **Then** I see the Electric Lime theme colors (#0FFF50) used consistently throughout the UI
2. **Given** I am on the signup page, **When** I fill out the registration form, **Then** the form elements match the application's color scheme and typography
3. **Given** I am viewing either authentication page, **When** I interact with buttons or inputs, **Then** the Electric Lime accent color (#0FFF50) provides visual feedback

---

### User Story 2 - Dynamic Testimonial Carousel (Priority: P1)

As a visitor to the website, I want to see testimonials displayed in an engaging moving carousel that automatically rotates every 5 seconds so that I can easily consume social proof without manual interaction.

**Why this priority**: Testimonials are crucial for building trust with potential users. An automated carousel keeps the content fresh and engaging.

**Independent Test**: The testimonial carousel displays 3 testimonials simultaneously and automatically transitions to the next set every 5 seconds.

**Acceptance Scenarios**:

1. **Given** I am on the homepage, **When** I view the testimonials section, **Then** I see 3 testimonials displayed at once in a carousel format
2. **Given** the carousel is active, **When** 5 seconds pass without user interaction, **Then** the carousel smoothly transitions to the next set of testimonials
3. **Given** I am viewing testimonials on a mobile device, **When** the carousel transitions occur, **Then** there are no layout jumps or performance issues

---

### User Story 3 - Essential Core Pages (Priority: P2)

As a user of the todo application, I want access to a Contact page and a User Settings page so that I can reach out for support and customize my personal preferences.

**Why this priority**: These pages provide essential functionality for user support and personalization, improving overall user satisfaction and retention.

**Independent Test**: The Contact page contains a functional form and the User Settings page allows authenticated users to update their profile and preferences.

**Acceptance Scenarios**:

1. **Given** I am on the contact page, **When** I fill out and submit the contact form, **Then** the form validates inputs and provides appropriate feedback
2. **Given** I am an authenticated user on the settings page, **When** I update my profile information, **Then** the changes are saved and reflected in the application
3. **Given** I am on the settings page, **When** I navigate away and return, **Then** my saved preferences persist across sessions

---

### User Story 4 - Comprehensive Responsive Footer (Priority: P2)

As a user navigating the website, I want a persistent footer with organized navigation and social links so that I can easily access important pages and connect with the company on social media.

**Why this priority**: A well-organized footer improves site navigation and provides important contact and social media links, enhancing user experience.

**Independent Test**: The footer contains the website logo, organized page routes, and social links that are responsive across all device sizes.

**Acceptance Scenarios**:

1. **Given** I am viewing the website on any page, **When** I scroll to the bottom, **Then** I see a consistent footer with organized navigation links
2. **Given** I am on a mobile device, **When** I view the footer, **Then** the links stack vertically and remain easily tappable
3. **Given** I want to visit social media profiles, **When** I click social media icons in the footer, **Then** I am taken to the appropriate social media pages

---

### Edge Cases

- What happens when the carousel has fewer than 3 testimonials?
- How does the settings page handle failed save attempts due to network issues?
- What occurs when a user accesses the settings page without authentication?
- How does the contact form handle spam submissions or validation errors?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement custom Login page with the Electric Lime theme (#0FFF50 / #161616) color palette
- **FR-002**: System MUST implement custom Signup page with the Electric Lime theme (#0FFF50 / #161616) color palette
- **FR-003**: System MUST replace generic Better Auth UI components with custom-designed authentication pages
- **FR-004**: System MUST display 3 testimonials simultaneously in the carousel component
- **FR-005**: System MUST automatically rotate the testimonial carousel every 5000ms (5 seconds)
- **FR-006**: System MUST use Framer Motion for smooth carousel transitions with AnimatePresence
- **FR-007**: System MUST implement a functional Contact page with Shadcn Form and Input components
- **FR-008**: System MUST implement a User Settings page for authenticated users to update profile and preferences
- **FR-009**: System MUST protect the /settings route to ensure only authenticated users can access it
- **FR-010**: System MUST implement a persistent footer with website logo, organized page routes, and social links
- **FR-011**: System MUST ensure the footer is fully responsive and stacks links vertically on mobile devices
- **FR-012**: System MUST bind the User Settings page to live authentication session data
- **FR-013**: System MUST use proxy.ts to protect the /settings route from unauthenticated access
- **FR-014**: System MUST prevent layout jumps during carousel transitions using AnimatePresence
- **FR-015**: System MUST validate contact form inputs before submission

### Key Entities

- **Authentication Session**: Represents the user's authenticated state including profile data and preferences
- **Testimonial**: Represents a user testimonial with author, rating, content, and metadata
- **Contact Form Submission**: Represents user contact requests with validation and processing requirements
- **User Settings**: Represents user preferences and profile information that can be updated

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Testimonials rotate automatically every 5 seconds without user interaction, with smooth transitions lasting between 300-500ms
- **SC-002**: Clicking "Settings" in the Navbar correctly redirects authenticated users to the User Settings page within 100ms
- **SC-003**: Footer is fully responsive with links stacking vertically on mobile devices (screen width < 768px) without horizontal scrolling
- **SC-004**: Auth pages feel integrated with the Electric Lime theme (#0FFF50 accent color) and dark background (#161616) throughout the UI
- **SC-005**: Carousel displays 3 testimonials simultaneously with no layout jumps during transitions, maintaining 60fps performance
- **SC-006**: Contact form validates all inputs and provides clear error messages within 200ms of submission attempt
- **SC-007**: Unauthenticated users attempting to access /settings are redirected to login page within 150ms
- **SC-008**: User Settings page successfully retrieves and saves user profile data with 99% success rate
- **SC-009**: Footer navigation links correctly route to Home, Dashboard, Settings, and Contact pages
- **SC-010**: Social media links in footer open in new tabs and lead to correct Twitter, GitHub, and LinkedIn profiles