# Dell Boca Boys - Customer Portal

A modern, customer-facing portal for the Dell Boca Boys workflow automation platform. Built with React, TypeScript, and Tailwind CSS.

## Features

- **Dashboard** - Overview of workflow requests, active workflows, and key metrics
- **Request Management** - Create, track, and manage workflow automation requests
- **Workflow Library** - View and manage deployed workflow automations
- **Template Marketplace** - Browse and deploy pre-built workflow templates
- **Analytics** - Detailed performance metrics and insights
- **Real-time Notifications** - Stay updated on request status and workflow execution
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **React 18.2** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Query (TanStack Query)** - Data fetching and caching
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Recharts** - Beautiful, responsive charts
- **React Hook Form** - Performant form handling
- **Sonner** - Elegant toast notifications

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_ENVIRONMENT=development
```

### Development

Start the development server:

```bash
npm run dev
```

The portal will be available at `http://localhost:3001`.

### Build

Create a production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Project Structure

```
customer-portal/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Base UI components (Button, Card, etc.)
│   │   ├── customer/      # Business components (WorkflowCard, etc.)
│   │   └── layout/        # Layout components (Header, Sidebar, etc.)
│   ├── pages/             # Page components (Dashboard, Requests, etc.)
│   ├── services/          # API services and utilities
│   ├── stores/            # Zustand state management stores
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── index.html             # HTML entry point
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Project dependencies
```

## Key Components

### Authentication
- Login page with email/password
- Registration page for new customers
- Protected routes with automatic redirect
- JWT token management with automatic refresh

### Dashboard
- Overview metrics and KPIs
- Recent workflow requests
- Active workflows
- Recent notifications
- Execution history charts

### Request Management
- Create new workflow requests
- Search and filter requests
- Track request status
- Add attachments and comments
- Priority management

### Workflow Library
- View active and inactive workflows
- Execute workflows manually
- Toggle workflow status (activate/pause)
- View workflow metrics and performance

### Template Marketplace
- Browse workflow templates
- Filter by category and complexity
- Sort by popularity or rating
- One-click template deployment

### Analytics
- Detailed performance metrics
- Interactive charts and visualizations
- Success rate tracking
- Execution time analysis
- Category and status distribution

## API Integration

The portal communicates with the Dell Boca Boys backend API. All API calls are handled through the centralized `apiService` in `src/services/api.ts`.

### Key Features:
- Automatic authentication token injection
- Token refresh on expiration
- Request/response interceptors
- Error handling
- Type-safe API calls

## State Management

The portal uses Zustand for lightweight state management:

- **authStore** - Authentication state and user session
- **notificationStore** - Real-time notifications

## Styling

The portal uses Tailwind CSS with a custom design system:

- Consistent color palette
- Reusable component classes
- Responsive breakpoints
- Dark mode support (planned)

## Best Practices

- **Type Safety** - Comprehensive TypeScript types for all data structures
- **Component Reusability** - Modular, composable components
- **Performance** - React Query caching, lazy loading, pagination
- **Accessibility** - Semantic HTML, ARIA attributes
- **Error Handling** - User-friendly error messages and fallbacks
- **Security** - XSS protection, CSRF tokens, secure authentication

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Proprietary - Dell Boca Boys Workflow Automation Platform
