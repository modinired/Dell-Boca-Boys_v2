'use client'

import { Activity, Mail, CheckCircle2, Clock, TrendingUp, Zap } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Avatar, AvatarFallback, ScrollArea } from '@/components/ui'
import { useDashboardStore } from '@/store'
import { formatRelativeTime, getAgentInitials, formatPercentage } from '@/lib/utils'
import { AGENT_METADATA } from '@/types'
import type { AgentPersonality } from '@/types'

export function DashboardOverview() {
  const { agents, tasks, emails, systemStats } = useDashboardStore()

  // Calculate stats
  const activeTasks = tasks.filter(t => t.status === 'in_progress')
  const completedToday = tasks.filter(t =>
    t.status === 'completed' &&
    t.completedAt &&
    new Date(t.completedAt).toDateString() === new Date().toDateString()
  )
  const unprocessedEmails = emails.filter(e => !e.processed)

  const stats = [
    {
      name: 'Active Agents',
      value: agents.filter(a => a.status === 'active').length,
      total: agents.length,
      icon: Zap,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      name: 'Tasks Today',
      value: systemStats.tasksToday,
      change: '+12%',
      icon: CheckCircle2,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      name: 'Emails Processed',
      value: systemStats.emailsProcessed,
      pending: unprocessedEmails.length,
      icon: Mail,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      name: 'Avg Response Time',
      value: `${Math.round(systemStats.averageResponseTime / 1000)}s`,
      icon: Clock,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
        <p className="text-muted-foreground">
          Real-time monitoring of Dell Bocca Boys multi-agent system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.name} className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {stat.name}
                    </p>
                    <div className="flex items-baseline gap-2 mt-2">
                      <p className="text-2xl font-bold">
                        {stat.value}
                        {stat.total && <span className="text-base text-muted-foreground">/{stat.total}</span>}
                      </p>
                      {stat.change && (
                        <span className="text-xs font-medium text-green-500 flex items-center">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {stat.change}
                        </span>
                      )}
                      {stat.pending && stat.pending > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          {stat.pending} pending
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Agent Cards Grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4">CESAR Agent Network</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => {
            const meta = AGENT_METADATA[agent.id as AgentPersonality]
            const statusColors = {
              active: 'bg-green-500',
              idle: 'bg-yellow-500',
              processing: 'bg-blue-500',
              error: 'bg-red-500',
              offline: 'bg-gray-500',
            }

            return (
              <Card key={agent.id} className="card-hover relative overflow-hidden">
                {/* Gradient background */}
                <div
                  className="absolute top-0 right-0 h-24 w-24 opacity-10 blur-2xl"
                  style={{ backgroundColor: agent.color }}
                />

                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12" style={{ backgroundColor: agent.color }}>
                        <AvatarFallback className="text-white font-semibold">
                          {getAgentInitials(agent.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-base">{agent.name}</CardTitle>
                        <CardDescription className="text-xs">
                          {agent.role}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div
                        className={`h-2 w-2 rounded-full ${statusColors[agent.status]} ${
                          agent.status === 'active' ? 'animate-pulse' : ''
                        }`}
                      />
                      <span className="text-xs text-muted-foreground capitalize">
                        {agent.status}
                      </span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Current task */}
                  {agent.currentTask ? (
                    <div className="rounded-md bg-muted p-2">
                      <p className="text-xs text-muted-foreground mb-1">Current Task:</p>
                      <p className="text-sm font-medium line-clamp-2">
                        {tasks.find(t => t.id === agent.currentTask)?.title || 'Processing...'}
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-md border border-dashed p-2">
                      <p className="text-xs text-muted-foreground text-center">
                        No active task
                      </p>
                    </div>
                  )}

                  {/* Performance metrics */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <p className="text-muted-foreground">Completed</p>
                      <p className="font-semibold">{agent.tasksCompleted}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Success Rate</p>
                      <p className="font-semibold">{formatPercentage(agent.performance.successRate)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Today</p>
                      <p className="font-semibold">{agent.performance.tasksToday}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Avg Time</p>
                      <p className="font-semibold">{agent.performance.averageTime}s</p>
                    </div>
                  </div>

                  {/* Expertise tags */}
                  <div className="flex flex-wrap gap-1">
                    {agent.expertise.slice(0, 3).map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-[10px] px-1.5 py-0">
                        {skill}
                      </Badge>
                    ))}
                    {agent.expertise.length > 3 && (
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                        +{agent.expertise.length - 3}
                      </Badge>
                    )}
                  </div>

                  {/* Last active */}
                  <div className="text-xs text-muted-foreground">
                    Last active: {formatRelativeTime(agent.lastActive)}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Active Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Active Tasks</CardTitle>
            <CardDescription>Currently being processed</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              {activeTasks.length === 0 ? (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No active tasks
                </div>
              ) : (
                <div className="space-y-3">
                  {activeTasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-3 rounded-lg border p-3 hover:bg-accent transition-colors"
                    >
                      <div
                        className="h-2 w-2 rounded-full mt-2"
                        style={{
                          backgroundColor: task.priority === 'urgent'
                            ? '#EF4444'
                            : task.priority === 'high'
                            ? '#F97316'
                            : task.priority === 'medium'
                            ? '#F59E0B'
                            : '#10B981',
                        }}
                      />
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none">{task.title}</p>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {task.description}
                        </p>
                        <div className="flex items-center gap-2 pt-1">
                          <Badge variant="outline" className="text-[10px]">
                            {task.type}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {task.assignedAgents.length} agent{task.assignedAgents.length > 1 ? 's' : ''}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Recent Emails */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Emails</CardTitle>
            <CardDescription>Latest communications</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              {emails.length === 0 ? (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No emails yet
                </div>
              ) : (
                <div className="space-y-3">
                  {emails.slice(0, 10).map((email) => (
                    <div
                      key={email.id}
                      className="rounded-lg border p-3 hover:bg-accent transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex-1">
                          <p className="text-sm font-medium line-clamp-1">{email.subject}</p>
                          <p className="text-xs text-muted-foreground">{email.from}</p>
                        </div>
                        {email.processed ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <Clock className="h-4 w-4 text-yellow-500" />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {email.bodyText}
                      </p>
                      <div className="flex items-center justify-between mt-2 pt-2 border-t">
                        <Badge variant={email.processed ? "secondary" : "default"} className="text-[10px]">
                          {email.processed ? 'Processed' : 'Pending'}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(email.receivedAt)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
