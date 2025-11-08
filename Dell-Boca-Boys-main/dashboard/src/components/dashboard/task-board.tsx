'use client'

import { useState } from 'react'
import { Plus, Filter, Search, Clock, CheckCircle2, AlertCircle, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, Badge, ScrollArea, Avatar, AvatarFallback } from '@/components/ui'
import { Button } from '@/components/ui/button'
import { useDashboardStore } from '@/store'
import { formatRelativeTime, getAgentInitials } from '@/lib/utils'
import { TASK_TYPE_COLORS, PRIORITY_COLORS, AGENT_METADATA } from '@/types'
import type { TaskStatus, AgentPersonality } from '@/types'

export function TaskBoard() {
  const { tasks, agents } = useDashboardStore()
  const [searchQuery, setSearchQuery] = useState('')

  const columns: { status: TaskStatus; title: string; icon: any; color: string }[] = [
    { status: 'pending', title: 'Pending', icon: Clock, color: 'text-yellow-500' },
    { status: 'in_progress', title: 'In Progress', icon: AlertCircle, color: 'text-blue-500' },
    { status: 'completed', title: 'Completed', icon: CheckCircle2, color: 'text-green-500' },
    { status: 'failed', title: 'Failed', icon: XCircle, color: 'text-red-500' },
  ]

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getTasksByStatus = (status: TaskStatus) =>
    filteredTasks.filter(task => task.status === status)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Task Board</h1>
          <p className="text-muted-foreground">
            Kanban-style task management for agent activities
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {columns.map((column) => {
          const Icon = column.icon
          const count = getTasksByStatus(column.status).length
          return (
            <Card key={column.status}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{column.title}</p>
                    <p className="text-2xl font-bold mt-1">{count}</p>
                  </div>
                  <Icon className={`h-8 w-8 ${column.color}`} />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="search"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-lg border bg-background pl-10 pr-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>

      {/* Kanban Board */}
      <div className="grid gap-4 md:grid-cols-4">
        {columns.map((column) => {
          const Icon = column.icon
          const columnTasks = getTasksByStatus(column.status)

          return (
            <div key={column.status} className="flex flex-col">
              {/* Column Header */}
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className={`h-5 w-5 ${column.color}`} />
                  <h3 className="font-semibold">{column.title}</h3>
                  <Badge variant="secondary" className="text-xs">
                    {columnTasks.length}
                  </Badge>
                </div>
              </div>

              {/* Column Content */}
              <ScrollArea className="flex-1 min-h-[600px]">
                <div className="space-y-3 pr-4">
                  {columnTasks.length === 0 ? (
                    <div className="rounded-lg border-2 border-dashed p-8 text-center text-sm text-muted-foreground">
                      No {column.title.toLowerCase()} tasks
                    </div>
                  ) : (
                    columnTasks.map((task) => (
                      <Card
                        key={task.id}
                        className="cursor-pointer hover:shadow-md transition-all"
                      >
                        <CardContent className="p-4 space-y-3">
                          {/* Priority indicator */}
                          <div
                            className="h-1 w-full rounded-full -mt-4 -mx-4 mb-2"
                            style={{ backgroundColor: PRIORITY_COLORS[task.priority] }}
                          />

                          {/* Task Header */}
                          <div className="space-y-1">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-medium text-sm leading-tight line-clamp-2">
                                {task.title}
                              </h4>
                              <Badge
                                variant="secondary"
                                className="text-[10px] shrink-0"
                                style={{
                                  backgroundColor: `${TASK_TYPE_COLORS[task.type]}20`,
                                  color: TASK_TYPE_COLORS[task.type],
                                  border: 'none',
                                }}
                              >
                                {task.type}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {task.description}
                            </p>
                          </div>

                          {/* Assigned Agents */}
                          <div className="flex items-center gap-2">
                            <div className="flex -space-x-2">
                              {task.assignedAgents.slice(0, 3).map((agentId) => {
                                const agent = agents.find(a => a.id === agentId)
                                if (!agent) return null
                                return (
                                  <Avatar
                                    key={agentId}
                                    className="h-6 w-6 border-2 border-background"
                                    style={{ backgroundColor: agent.color }}
                                  >
                                    <AvatarFallback
                                      className="text-[10px] text-white font-semibold"
                                      style={{ backgroundColor: agent.color }}
                                    >
                                      {getAgentInitials(agent.name)}
                                    </AvatarFallback>
                                  </Avatar>
                                )
                              })}
                              {task.assignedAgents.length > 3 && (
                                <div className="h-6 w-6 rounded-full bg-muted border-2 border-background flex items-center justify-center text-[10px] font-semibold">
                                  +{task.assignedAgents.length - 3}
                                </div>
                              )}
                            </div>
                            {task.assignedAgents.length === 0 && (
                              <span className="text-xs text-muted-foreground">Unassigned</span>
                            )}
                          </div>

                          {/* Task Meta */}
                          <div className="flex items-center justify-between pt-2 border-t">
                            <Badge
                              variant="outline"
                              className="text-[10px]"
                              style={{
                                borderColor: PRIORITY_COLORS[task.priority],
                                color: PRIORITY_COLORS[task.priority],
                              }}
                            >
                              {task.priority}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatRelativeTime(task.updatedAt)}
                            </span>
                          </div>

                          {/* Email indicator */}
                          {task.sourceEmail && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <div className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                              From email
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>
          )
        })}
      </div>
    </div>
  )
}
