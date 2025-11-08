# Dell Bocca Boys Dashboard

> World-class, real-time dashboard for monitoring and managing the Dell Bocca Boys multi-agent AI system

## 🌟 Features

### Real-Time Monitoring
- **Live Agent Status**: Monitor all 6 CESAR agents (Terry, Victoria, Marcus, Isabella, Eleanor, James) in real-time
- **Task Tracking**: Kanban-style task board with drag-and-drop functionality
- **Email Management**: View and manage emails processed by agents
- **WebSocket Integration**: Real-time updates with zero refresh needed

### Advanced Visualization
- **Agent Network Graph**: Interactive visualization of agent collaborations using ReactFlow
- **Performance Analytics**: Real-time charts and metrics using Recharts
- **Success Rate Tracking**: Monitor agent performance and task completion rates
- **Activity Timeline**: 24-hour visualization of system activity

### Workflow Management
- **Visual Workflow Builder**: Create automated agent workflows (n8n-style)
- **Pre-built Templates**: Quick-start templates for common workflows
- **Workflow Execution**: Monitor and control workflow runs

### System Control
- **Service Management**: Start/stop email service and other components
- **Configuration Panel**: Adjust system settings in real-time
- **System Logs**: View recent system events and errors
- **Health Monitoring**: CPU, memory, and uptime tracking

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.10+
- Dell Bocca Boys backend running

### Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Edit .env.local with your configuration
nano .env.local
```

### Environment Variables

Create `.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket URL
NEXT_PUBLIC_WS_URL=http://localhost:8000

# Optional: Enable debug mode
NEXT_PUBLIC_DEBUG=false
```

### Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
dashboard/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Main dashboard page
│   │   └── globals.css        # Global styles
│   │
│   ├── components/
│   │   ├── dashboard/         # Dashboard sections
│   │   │   ├── overview.tsx           # Main overview with agent cards
│   │   │   ├── email-management.tsx   # Email interface
│   │   │   ├── task-board.tsx         # Kanban task board
│   │   │   ├── agent-network.tsx      # Network visualizer
│   │   │   ├── workflow-builder.tsx   # Workflow designer
│   │   │   ├── analytics.tsx          # Charts and metrics
│   │   │   └── control-panel.tsx      # System control
│   │   │
│   │   ├── ui/                # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   └── index.tsx      # Core UI components
│   │   │
│   │   └── providers/         # Context providers
│   │       └── dashboard-provider.tsx
│   │
│   ├── hooks/                 # Custom React hooks
│   │   └── useWebSocket.ts    # WebSocket integration
│   │
│   ├── lib/                   # Utilities
│   │   └── utils.ts           # Helper functions
│   │
│   ├── store/                 # State management
│   │   └── index.ts           # Zustand store
│   │
│   └── types/                 # TypeScript types
│       └── index.ts           # Type definitions
│
├── public/                    # Static assets
├── package.json               # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.ts        # Tailwind CSS config
└── next.config.js            # Next.js config
```

## 🎨 Design System

Built with **shadcn/ui** and **Tailwind CSS** for a modern, accessible interface.

### Color Palette

```typescript
// Agent colors
terry: #FF6B35      // Orange - Technical
victoria: #9B59B6   // Purple - Strategic
marcus: #3498DB     // Blue - Architecture
isabella: #E91E63   // Pink - Creative
eleanor: #16A085    // Teal - Academic
james: #E67E22      // Dark Orange - Command

// Status colors
active: #10B981     // Green
idle: #F59E0B       // Yellow
processing: #3B82F6 // Blue
error: #EF4444      // Red
```

### Typography

- **Font**: Inter (Google Fonts)
- **Headings**: Bold, 2xl-3xl
- **Body**: Regular, sm-base
- **Code**: Monaco, Menlo, monospace

## 🔌 API Integration

### REST Endpoints

```typescript
// Get all agents
GET /api/agents

// Get tasks
GET /api/tasks?status=pending

// Create task
POST /api/tasks

// Get emails
GET /api/emails?processed=false

// Email service control
POST /api/email-service/start
POST /api/email-service/stop

// System stats
GET /api/stats

// Workflows
GET /api/workflows
POST /api/workflows
```

### WebSocket Events

```typescript
// Connect to WebSocket
const socket = io('http://localhost:8000')

// Subscribe to topics
socket.emit('subscribe', { topic: 'agent_updates' })
socket.emit('subscribe', { topic: 'task_updates' })

// Listen for updates
socket.on('agent_update', (data) => {
  // Update agent status
})

socket.on('task_update', (data) => {
  // Update task status
})

socket.on('email_received', (data) => {
  // New email notification
})
```

## 📊 Dashboard Sections

### 1. Overview
- Agent status cards with real-time updates
- System statistics (tasks, emails, success rate)
- Recent activity feed
- Active tasks list

### 2. Email Management
- Email inbox with filtering
- Email detail view
- Associated task tracking
- Reply/Archive/Delete actions

### 3. Task Board
- Kanban-style columns (Pending, In Progress, Completed, Failed)
- Drag-and-drop task cards
- Priority indicators
- Agent assignments
- Search and filter

### 4. Agent Network
- Interactive network graph
- Real-time collaboration visualization
- Agent performance metrics
- Network statistics

### 5. Workflow Builder
- Visual workflow designer
- Pre-built templates
- Workflow execution monitoring
- Import/Export workflows

### 6. Analytics
- Agent performance charts
- Task type distribution
- 24-hour activity timeline
- Success rate trends

### 7. Control Panel
- Service management (start/stop)
- Configuration settings
- System health monitoring
- Recent logs

## 🎯 State Management

### Zustand Store

```typescript
import { useDashboardStore } from '@/store'

// Access state
const { agents, tasks, emails } = useDashboardStore()

// Update state
const { updateAgentStatus, addTask } = useDashboardStore()

// Selectors
const activeAgents = useDashboardStore(selectActiveAgents)
const pendingTasks = useDashboardStore(selectPendingTasks)
```

### State Structure

```typescript
interface DashboardState {
  agents: Agent[]
  tasks: Task[]
  emails: EmailMessage[]
  collaborations: AgentCollaboration[]
  workflows: Workflow[]
  emailService: EmailServiceStatus
  systemStats: SystemStats
  notifications: Notification[]
  sidebarCollapsed: boolean
  darkMode: boolean
}
```

## 🔧 Development

### Adding a New Component

```typescript
// 1. Create component
// src/components/dashboard/my-component.tsx
export function MyComponent() {
  const { agents } = useDashboardStore()
  return <div>My Component</div>
}

// 2. Import in main page
// src/app/page.tsx
import { MyComponent } from '@/components/dashboard/my-component'

// 3. Add to navigation
const navigation = [
  // ...
  { id: 'myview', name: 'My View', icon: Icon, count: null },
]
```

### Adding a New API Endpoint

```typescript
// 1. Define in backend
// api/dashboard_api.py
@app.get("/api/my-data")
async def get_my_data():
    return {"data": "value"}

// 2. Call from frontend
// src/components/dashboard/my-component.tsx
useEffect(() => {
  fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/my-data`)
    .then(res => res.json())
    .then(data => console.log(data))
}, [])
```

### WebSocket Updates

```typescript
// Emit from backend
await manager.broadcast({
  type: "custom_event",
  payload: data,
  timestamp: datetime.utcnow()
})

// Handle in frontend
// src/hooks/useWebSocket.ts
socket.on('custom_event', (data) => {
  // Handle event
  addNotification({
    type: 'info',
    message: data.message
  })
})
```

## 🧪 Testing

```bash
# Run type checking
npm run type-check

# Run linter
npm run lint

# Build test
npm run build
```

## 📦 Deployment

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
# Build and run
docker build -t dell-bocca-dashboard .
docker run -p 3000:3000 dell-bocca-dashboard
```

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Environment Variables (Production)

```bash
NEXT_PUBLIC_API_URL=https://api.dellboccaboys.com
NEXT_PUBLIC_WS_URL=wss://api.dellboccaboys.com
```

## 🎨 Customization

### Changing Theme Colors

Edit `tailwind.config.ts`:

```typescript
colors: {
  agent: {
    terry: "#YOUR_COLOR",
    // ...
  }
}
```

### Adding Custom Agent

1. Update types in `src/types/index.ts`
2. Add to `AGENT_METADATA`
3. Agent will automatically appear in all dashboards

### Custom Widgets

Create widgets in `src/components/widgets/` and import in any dashboard section.

## 🐛 Troubleshooting

### WebSocket Not Connecting

1. Check backend is running on port 8000
2. Verify `NEXT_PUBLIC_WS_URL` in `.env.local`
3. Check browser console for errors

### Agents Not Showing

1. Verify backend API is accessible
2. Check `GET /api/agents` returns data
3. Initialize agents in store with `initializeAgents()`

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## 📝 License

Part of the Dell Bocca Boys project.

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Zustand](https://github.com/pmndrs/zustand)
- [ReactFlow](https://reactflow.dev)
- [Recharts](https://recharts.org)

---

**Built with ❤️ for the Dell Bocca Boys Multi-Agent System**

**Version**: 1.0.0
**Last Updated**: 2025-01-07
