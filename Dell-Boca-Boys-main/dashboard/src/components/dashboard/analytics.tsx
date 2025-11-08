'use client'

import { TrendingUp, Activity, Zap, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui'
import { useDashboardStore } from '@/store'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { AGENT_METADATA } from '@/types'

export function Analytics() {
  const { agents, tasks, systemStats } = useDashboardStore()

  // Agent performance data
  const agentPerformanceData = agents.map(agent => ({
    name: agent.name.split(' ')[0],
    completed: agent.tasksCompleted,
    successRate: agent.performance.successRate * 100,
    avgTime: agent.performance.averageTime,
    color: agent.color,
  }))

  // Task type distribution
  const taskTypeData = Object.entries(
    tasks.reduce((acc, task) => {
      acc[task.type] = (acc[task.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  ).map(([type, count]) => ({ name: type, value: count }))

  // Task status distribution
  const taskStatusData = Object.entries(
    tasks.reduce((acc, task) => {
      acc[task.status] = (acc[task.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  ).map(([status, count]) => ({ name: status, value: count }))

  // Mock time series data (would come from backend)
  const timeSeriesData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    tasks: Math.floor(Math.random() * 20) + 5,
    emails: Math.floor(Math.random() * 15) + 2,
  }))

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics & Performance</h1>
        <p className="text-muted-foreground">
          Real-time metrics and insights into agent performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-3xl font-bold mt-2">{(systemStats.successRate * 100).toFixed(1)}%</p>
                <p className="text-xs text-green-500 mt-1 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +5.2% from last week
                </p>
              </div>
              <Activity className="h-12 w-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Response Time</p>
                <p className="text-3xl font-bold mt-2">{Math.round(systemStats.averageResponseTime / 1000)}s</p>
                <p className="text-xs text-green-500 mt-1 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  -12% faster
                </p>
              </div>
              <Clock className="h-12 w-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Tasks</p>
                <p className="text-3xl font-bold mt-2">{systemStats.totalTasks}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {systemStats.tasksToday} today
                </p>
              </div>
              <Zap className="h-12 w-12 text-yellow-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Agents</p>
                <p className="text-3xl font-bold mt-2">{systemStats.activeAgents}/{agents.length}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {((systemStats.activeAgents / agents.length) * 100).toFixed(0)}% utilization
                </p>
              </div>
              <Activity className="h-12 w-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Agent Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Task Completion</CardTitle>
            <CardDescription>Tasks completed by each agent</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.1} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="completed" fill="#3B82F6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Task Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Task Type Distribution</CardTitle>
            <CardDescription>Breakdown of task types</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={taskTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {taskTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Activity Timeline */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>24-Hour Activity Timeline</CardTitle>
            <CardDescription>Tasks and emails processed over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.1} />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Legend />
                <Line type="monotone" dataKey="tasks" stroke="#3B82F6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="emails" stroke="#8B5CF6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Agent Success Rates */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Success Rates</CardTitle>
          <CardDescription>Performance comparison across all agents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {agentPerformanceData.map((agent) => (
              <div key={agent.name} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: agent.color }} />
                    <span className="font-medium">{agent.name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-muted-foreground">
                    <span>{agent.completed} tasks</span>
                    <span>{agent.successRate.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${agent.successRate}%`,
                      backgroundColor: agent.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
