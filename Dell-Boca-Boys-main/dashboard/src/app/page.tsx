'use client'

import { useState } from 'react'
import { Menu, Search, Bell, Settings, LayoutDashboard, Mail, ListTodo, Network, Workflow, BarChart3, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useDashboardStore, selectUnreadNotifications } from '@/store'
import { cn } from '@/lib/utils'

// Import dashboard sections
import { DashboardOverview } from '@/components/dashboard/overview'
import { EmailManagement } from '@/components/dashboard/email-management'
import { TaskBoard } from '@/components/dashboard/task-board'
import { AgentNetwork } from '@/components/dashboard/agent-network'
import { WorkflowBuilder } from '@/components/dashboard/workflow-builder'
import { Analytics } from '@/components/dashboard/analytics'
import { ControlPanel } from '@/components/dashboard/control-panel'

type View = 'overview' | 'email' | 'tasks' | 'network' | 'workflows' | 'analytics' | 'settings'

export default function DashboardPage() {
  const [currentView, setCurrentView] = useState<View>('overview')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const { systemStats, agents } = useDashboardStore()
  const unreadNotifications = useDashboardStore(selectUnreadNotifications)

  const navigation = [
    { id: 'overview', name: 'Dashboard', icon: LayoutDashboard, count: null },
    { id: 'email', name: 'Email Management', icon: Mail, count: systemStats.emailsProcessed },
    { id: 'tasks', name: 'Task Board', icon: ListTodo, count: systemStats.tasksToday },
    { id: 'network', name: 'Agent Network', icon: Network, count: agents.filter(a => a.status === 'active').length },
    { id: 'workflows', name: 'Workflows', icon: Workflow, count: null },
    { id: 'analytics', name: 'Analytics', icon: BarChart3, count: null },
    { id: 'settings', name: 'Control Panel', icon: Shield, count: null },
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col bg-card border-r transition-all duration-300",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b px-4">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold">
                DB
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-semibold">Dell Bocca Boys</span>
                <span className="text-xs text-muted-foreground">Agent Dashboard</span>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="h-8 w-8"
          >
            <Menu className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id

            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id as View)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {sidebarOpen && (
                  <>
                    <span className="flex-1 text-left">{item.name}</span>
                    {item.count !== null && (
                      <span className={cn(
                        "rounded-full px-2 py-0.5 text-xs",
                        isActive ? "bg-primary-foreground/20" : "bg-accent"
                      )}>
                        {item.count}
                      </span>
                    )}
                  </>
                )}
              </button>
            )
          })}
        </nav>

        {/* User section */}
        {sidebarOpen && (
          <div className="border-t p-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-orange-400 to-pink-600" />
              <div className="flex-1 overflow-hidden">
                <div className="text-sm font-medium truncate">System Admin</div>
                <div className="text-xs text-muted-foreground truncate">admin@dellboccaboys.com</div>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <div className={cn("flex-1 flex flex-col transition-all duration-300", sidebarOpen ? "ml-64" : "ml-16")}>
        {/* Top bar */}
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60 px-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search agents, tasks, emails..."
                className="w-full max-w-sm rounded-lg border bg-background pl-9 pr-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </div>

          {/* Status indicators */}
          <div className="flex items-center gap-2">
            <div className="text-xs text-muted-foreground hidden md:block">
              {systemStats.activeAgents}/{agents.length} agents active
            </div>
            <div className="h-4 w-px bg-border hidden md:block" />
            <div className="text-xs text-muted-foreground hidden md:block">
              Success Rate: {(systemStats.successRate * 100).toFixed(1)}%
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              {unreadNotifications.length > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
                  {unreadNotifications.length}
                </span>
              )}
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {currentView === 'overview' && <DashboardOverview />}
          {currentView === 'email' && <EmailManagement />}
          {currentView === 'tasks' && <TaskBoard />}
          {currentView === 'network' && <AgentNetwork />}
          {currentView === 'workflows' && <WorkflowBuilder />}
          {currentView === 'analytics' && <Analytics />}
          {currentView === 'settings' && <ControlPanel />}
        </main>
      </div>
    </div>
  )
}
