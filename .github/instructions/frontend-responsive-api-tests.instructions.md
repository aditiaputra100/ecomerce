---
description: "Use when creating or updating frontend pages, components, or API communication logic. Favor mobile-responsive UI and add integration-style tests for frontend-backend API communication using Vitest and React Testing Library with mocked API responses."
name: "Frontend Responsive API Quality"
applyTo: ["src/**/*.ts", "src/**/*.tsx", "src/**/*.css"]
---
# Frontend Responsive API Quality

These are best-effort preferences for frontend changes.

- Build UI with mobile responsiveness in mind first, then scale up for tablet and desktop.
- Ensure layouts remain usable on small screens: avoid horizontal overflow, clipped controls, and unreadable text.
- For features that call backend APIs, add integration-style frontend tests that validate API communication paths.
- Prefer Vitest and React Testing Library with mocked API responses for frontend-backend communication tests.
- Cover success and error states for API flows, including loading, failure handling, and user-visible feedback.
- Keep tests close to the feature and aligned with the existing test setup used in this repository.
