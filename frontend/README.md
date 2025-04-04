# Stash

A minimalist link-saving application focused on speed, simplicity, and low-friction workflow.

## About

Stash is a clean, elegant application for saving and organizing links. It allows you to quickly save links, categorize them, and access them later with minimal friction.

## Features

- Simple link saving with optional notes
- Category management
- Read/unread status tracking
- Link details page with metadata
- iOS Shortcut integration
- Firefox browser extension

## Development

Once you've installed dependencies with `npm install`, start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

## Production Roadmap

### Critical Path (Must-Have)

1. **Search Functionality**
   - Implement real-time search across titles, URLs, and notes
   - Add a simple search bar at the top of the stash page
   - Enable filtering by category and read status

2. **Mobile Experience Optimization**
   - Improve touch targets for better mobile usability
   - Ensure responsive layout works well on all device sizes
   - Add swipe gestures for common actions

3. **Performance Optimization**
   - Implement pagination for links list to handle large collections
   - Add loading states for API operations
   - Consider client-side caching for faster loading

4. **Error Handling Improvements**
   - Add more descriptive error messages
   - Implement proper error UI components
   - Add offline handling capabilities

5. **Subscription/Payment Integration**
   - Implement Stripe integration for premium features
   - Create subscription management UI in profile
   - Set up webhook handlers for subscription events

### Premium Features (Revenue Generators)

6. **AI Summary Integration**
   - Implement the backend processing for link summarization
   - Add UI for viewing summaries in link details
   - Gate this behind the premium subscription

7. **Weekly Digest Emails**
   - Create email templates for link digests
   - Implement scheduling system
   - Make this a premium feature

8. **Browser Extensions**
   - Complete the Chrome extension
   - Ensure Firefox extension works properly
   - Add premium features to extensions

### User Experience Enhancements

9. **Link Archiving**
   - Add archive functionality as alternative to deletion
   - Create an archive view
   - Include batch restore options

10. **Bulk Actions**
    - Implement multi-select for links
    - Add bulk category assignment
    - Enable bulk read/unread toggle

11. **Import/Export**
    - Add browser bookmark import
    - Implement export functionality
    - Include backup/restore options

### Technical Improvements

12. **Testing Infrastructure**
    - Add unit tests for critical components
    - Implement integration tests for key flows
    - Set up CI/CD pipeline

13. **Code Cleanup**
    - Standardize API call patterns
    - Refactor repeated code
    - Improve type definitions

14. **Security Audit**
    - Review authentication flow
    - Ensure proper CSRF protection
    - Validate input sanitization

## Stripe Integration Plan

For monetizing premium features, we'll implement Stripe with the following approach:

1. **Subscription Tiers**
   - Free tier with basic functionality
   - Premium tier with AI features and advanced options

2. **Backend Components**
   - Webhook handler for subscription events
   - User subscription status tracking
   - Feature access control based on subscription

3. **Frontend Components**
   - Subscription management page
   - Payment method management
   - Upgrade prompts for premium features

4. **Implementation Steps**
   - Add Stripe SDK to the project
   - Create subscription products in Stripe dashboard
   - Implement checkout flow
   - Add subscription status to user profile