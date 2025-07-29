# SBM AI CRM Frontend

## Overview

The SBM AI CRM Frontend is a comprehensive React TypeScript application that provides a modern, Creatio-inspired interface for the Super Brand Mall AI Customer Relationship Management system. It integrates all 22 backend AI engines with 7 additional mall-specific features into an intuitive, enterprise-grade user interface.

## Features

### Core Modules (16 Total)

1. **Customer Intelligence Hub** - 360° customer insights with AI-powered personalization
2. **AI Campaign Command Center** - ROI prediction and real-time optimization  
3. **Intelligent Segmentation Studio** - ML-based customer clustering and segmentation
4. **Analytics & Insights Center** - Predictive analytics with AI-generated insights
5. **Journey & Automation Control** - Visual journey mapping and workflow automation
6. **AI Assistant & Chat Suite** - Natural language data queries and conversational AI
7. **Real-time Operations Center** - Live monitoring, notifications, and webhooks
8. **Reports & Visualization Studio** - 18+ chart types with automated insights
9. **Mall Operations Analytics** - Store performance and traffic optimization
10. **Camera Intelligence Dashboard** - AI-powered video analytics and crowd intelligence
11. **Chinese Market & Competition Suite** - Local market insights and competitive analysis
12. **Loyalty & VIP Management** - Comprehensive loyalty program (橙卡/金卡/钻卡会员)
13. **Retail Intelligence Engine** - Inventory forecasting and price optimization
14. **Economic & What-If Simulator** - Strategic planning with scenario modeling
15. **Voice of Customer Analytics** - Multi-platform feedback analysis
16. **Configuration & Admin Center** - System management and security

### Technology Stack

- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Tailwind CSS** for modern styling
- **Framer Motion** for smooth animations
- **React Query** for efficient data fetching
- **Zustand** for state management
- **React Router** for navigation
- **Chart.js & Recharts** for data visualization
- **Socket.io** for real-time features

### Design System

- **Creatio-inspired UI** with modern enterprise aesthetics
- **Responsive design** supporting mobile, tablet, and desktop
- **Dark/Light theme** support
- **Accessibility compliant** (WCAG 2.1 AA)
- **Glass morphism effects** and gradient backgrounds
- **Micro-interactions** and loading states

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- SBM AI CRM Backend running on port 8080

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080 (auto-proxied)

### Build for Production

```bash
# Type check
npm run type-check

# Build
npm run build

# Preview build
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── dashboard/      # Dashboard-specific components
│   ├── Layout.tsx      # Main layout with navigation
│   ├── AIChat.tsx      # AI assistant chat interface
│   └── ...
├── pages/              # Main page components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── CustomerIntelligence.tsx
│   ├── CampaignCenter.tsx
│   └── ...
├── stores/             # Zustand state management
│   └── authStore.ts    # Authentication state
├── lib/                # Utilities and API
│   └── api.ts          # API client configuration
├── App.tsx             # Main app component
└── main.tsx           # Application entry point
```

## Key Features Implementation

### 1. Comprehensive Backend Integration

All 22 backend AI engines are fully integrated:

- **Customer Management** with 360° profiles
- **Campaign Intelligence** with ROI prediction
- **Adaptive Clustering** with ML algorithms
- **Hyper-Personalization** for individual experiences
- **Predictive Analytics** for CLV and churn
- **Real-time Monitoring** with WebSocket connections
- **AI Chat Assistant** with database integration

### 2. Mall-Specific Features

Enhanced with 7 additional capabilities for Super Brand Mall:

- **Store Performance Comparison** across different brands
- **Camera Intelligence** with emotion and demographics analysis
- **Chinese Market Tools** (WeChat/Alipay integration, social monitoring)
- **Loyalty Tier Management** (橙卡/金卡/钻卡会员 system)
- **Retail Intelligence** with inventory forecasting
- **Economic Simulation** for strategic planning
- **Voice of Customer** analytics across platforms

### 3. AI-Powered User Experience

- **Natural Language Search** across all modules
- **Intelligent Recommendations** in every interface
- **Predictive Data Loading** based on user behavior
- **Smart Notifications** with priority filtering
- **Voice Input Support** for hands-free operation
- **Visual Query Builder** for complex data analysis

### 4. Enterprise-Grade Performance

- **Lazy Loading** for optimal performance
- **Infinite Scrolling** for large datasets
- **Real-time Updates** via WebSocket
- **Offline Capabilities** with service workers
- **Progressive Web App** features
- **Code Splitting** by route and feature

## Authentication

The application uses JWT-based authentication with:

- **Secure token storage** in localStorage
- **Automatic token refresh** via response headers
- **Role-based access control** for different features
- **Session management** with idle timeout

### Demo Credentials

```
Email: admin@sbm.com
Password: admin123
```

## API Integration

The frontend integrates with all backend endpoints:

- **REST API** for standard CRUD operations
- **WebSocket** for real-time updates
- **Server-Sent Events** for live notifications
- **File Upload** with progress tracking
- **Batch Operations** for bulk actions

## Customization

### Theming

The application supports extensive theming via Tailwind CSS:

```css
/* Custom color scheme */
--primary: your-primary-color;
--secondary: your-secondary-color;
--accent: your-accent-color;
```

### Localization

Built-in support for Chinese/English switching:

- **Dynamic language switching**
- **Date/time localization**
- **Number formatting** (Chinese/Western)
- **Cultural adaptations** for Chinese market

## Performance Optimization

- **Bundle splitting** by route and vendor
- **Image optimization** with lazy loading
- **API response caching** via React Query
- **Virtual scrolling** for large lists
- **Memoization** of expensive calculations

## Security Features

- **XSS Protection** via Content Security Policy
- **CSRF Protection** with secure headers
- **Input Validation** on all forms
- **Secure API Communication** with HTTPS
- **Role-based Feature Access** throughout UI

## Deployment

### Docker Deployment

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8080
VITE_WEBSOCKET_URL=ws://localhost:8080
VITE_APP_NAME="SBM AI CRM"
```

## Contributing

1. Follow TypeScript best practices
2. Use ESLint and Prettier for code formatting
3. Write unit tests for new components
4. Update documentation for new features
5. Follow the established component patterns

## Support

For technical support or questions:

- **Backend Integration**: Check API documentation at `/docs`
- **Frontend Issues**: Review browser console for errors
- **Performance**: Use React Developer Tools for profiling
- **Deployment**: Refer to Docker configuration

---

This frontend application provides a complete, production-ready interface for the SBM AI CRM system, incorporating all backend capabilities while adding mall-specific functionality and enterprise-grade user experience features.