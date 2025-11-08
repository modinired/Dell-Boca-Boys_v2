'use client'

import { Power, RefreshCw, Settings, Database, Server, Mail, Wifi, Shield } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Badge, Separator } from '@/components/ui'
import { Button } from '@/components/ui/button'
import { useDashboardStore } from '@/store'

export function ControlPanel() {
  const { emailService, systemStats, agents } = useDashboardStore()

  const services = [
    {
      name: 'Email Service',
      status: emailService.isRunning ? 'running' : 'stopped',
      icon: Mail,
      config: {
        'Email Address': emailService.emailAddress,
        'Poll Interval': `${emailService.pollInterval}s`,
        'Messages Processed': emailService.processedMessages,
      },
    },
    {
      name: 'WebSocket Server',
      status: 'running',
      icon: Wifi,
      config: {
        'Port': '8000',
        'Active Connections': '1',
        'Uptime': '2h 15m',
      },
    },
    {
      name: 'CESAR Agent Network',
      status: 'running',
      icon: Server,
      config: {
        'Total Agents': agents.length,
        'Active Agents': agents.filter(a => a.status === 'active').length,
        'Success Rate': `${(systemStats.successRate * 100).toFixed(1)}%`,
      },
    },
    {
      name: 'Database',
      status: 'running',
      icon: Database,
      config: {
        'Type': 'PostgreSQL 16',
        'Total Tasks': systemStats.totalTasks,
        'Storage Used': '1.2 GB',
      },
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Control Panel</h1>
          <p className="text-muted-foreground">
            Manage system services and configuration
          </p>
        </div>
        <Button variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh Status
        </Button>
      </div>

      {/* System Overview */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>Overall system health and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium">All Systems Operational</span>
              </div>
              <p className="text-xs text-muted-foreground">Last checked: Just now</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">System Uptime</p>
              <p className="text-2xl font-bold">{Math.floor(systemStats.uptime / 3600)}h</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">CPU Usage</p>
              <div className="flex items-baseline gap-2">
                <p className="text-2xl font-bold">23%</p>
                <p className="text-xs text-green-500">Normal</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Memory Usage</p>
              <div className="flex items-baseline gap-2">
                <p className="text-2xl font-bold">2.4GB</p>
                <p className="text-xs text-muted-foreground">/ 8GB</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Management */}
      <div className="grid gap-4 md:grid-cols-2">
        {services.map((service) => {
          const Icon = service.icon
          const isRunning = service.status === 'running'

          return (
            <Card key={service.name}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${isRunning ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                      <Icon className={`h-5 w-5 ${isRunning ? 'text-green-500' : 'text-red-500'}`} />
                    </div>
                    <div>
                      <CardTitle className="text-base">{service.name}</CardTitle>
                      <CardDescription className="text-xs">
                        <Badge
                          variant={isRunning ? "default" : "destructive"}
                          className="mt-1 text-[10px]"
                        >
                          {service.status}
                        </Badge>
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {isRunning ? (
                      <Button size="sm" variant="outline">
                        <Power className="h-3 w-3" />
                      </Button>
                    ) : (
                      <Button size="sm">
                        <Power className="h-3 w-3" />
                      </Button>
                    )}
                    <Button size="sm" variant="ghost">
                      <Settings className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(service.config).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">{key}</span>
                      <span className="font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>System Configuration</CardTitle>
          <CardDescription>Adjust system-wide settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Email Settings */}
          <div>
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Email Service Configuration
            </h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Auto-Process Emails</p>
                  <p className="text-xs text-muted-foreground">
                    Automatically process incoming emails with subject "Dell Bocca Boys"
                  </p>
                </div>
                <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  emailService.isRunning ? 'bg-primary' : 'bg-muted'
                }`}>
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    emailService.isRunning ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Poll Interval</p>
                  <p className="text-xs text-muted-foreground">
                    How often to check for new emails (in seconds)
                  </p>
                </div>
                <input
                  type="number"
                  value={emailService.pollInterval}
                  className="w-20 rounded border px-2 py-1 text-sm"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Agent Settings */}
          <div>
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Server className="h-4 w-4" />
              Agent Configuration
            </h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Auto-Scale Agents</p>
                  <p className="text-xs text-muted-foreground">
                    Automatically adjust active agents based on load
                  </p>
                </div>
                <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-muted">
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-1" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Max Concurrent Tasks</p>
                  <p className="text-xs text-muted-foreground">
                    Maximum tasks per agent
                  </p>
                </div>
                <input
                  type="number"
                  defaultValue={5}
                  className="w-20 rounded border px-2 py-1 text-sm"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Security */}
          <div>
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security
            </h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Enable Authentication</p>
                  <p className="text-xs text-muted-foreground">
                    Require login to access dashboard
                  </p>
                </div>
                <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">API Rate Limiting</p>
                  <p className="text-xs text-muted-foreground">
                    Limit API requests per minute
                  </p>
                </div>
                <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary">
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4">
            <Button>Save Configuration</Button>
          </div>
        </CardContent>
      </Card>

      {/* System Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent System Logs</CardTitle>
          <CardDescription>Latest system events and messages</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 font-mono text-xs">
            {[
              { time: '14:32:15', level: 'INFO', message: 'Email service: New email processed from user@example.com' },
              { time: '14:31:48', level: 'INFO', message: 'Agent terry_delmonaco: Task completed successfully' },
              { time: '14:30:22', level: 'INFO', message: 'WebSocket: New client connected' },
              { time: '14:29:55', level: 'WARN', message: 'Email service: Rate limit approaching (45/50)' },
              { time: '14:28:10', level: 'INFO', message: 'Agent victoria_sterling: Started task analysis' },
            ].map((log, index) => (
              <div key={index} className="flex items-start gap-3 rounded p-2 hover:bg-muted/50">
                <span className="text-muted-foreground">{log.time}</span>
                <Badge
                  variant={log.level === 'INFO' ? 'secondary' : 'destructive'}
                  className="text-[10px]"
                >
                  {log.level}
                </Badge>
                <span className="flex-1">{log.message}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
