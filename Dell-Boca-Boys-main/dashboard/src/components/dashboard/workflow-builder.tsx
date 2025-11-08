'use client'

import { Plus, Play, Pause, Trash2, Save, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Badge, ScrollArea } from '@/components/ui'
import { Button } from '@/components/ui/button'
import { useDashboardStore } from '@/store'
import { formatRelativeTime } from '@/lib/utils'

export function WorkflowBuilder() {
  const { workflows } = useDashboardStore()

  const statusColors = {
    draft: 'bg-gray-500',
    active: 'bg-green-500',
    paused: 'bg-yellow-500',
    archived: 'bg-red-500',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Builder</h1>
          <p className="text-muted-foreground">
            Design and manage automated agent workflows
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Workflow
        </Button>
      </div>

      {/* Workflow Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Workflows</p>
            <p className="text-2xl font-bold mt-1">{workflows.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Active</p>
            <p className="text-2xl font-bold mt-1">
              {workflows.filter(w => w.status === 'active').length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Executions</p>
            <p className="text-2xl font-bold mt-1">
              {workflows.reduce((sum, w) => sum + w.executionCount, 0)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Drafts</p>
            <p className="text-2xl font-bold mt-1">
              {workflows.filter(w => w.status === 'draft').length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Workflow Templates */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Start Templates</CardTitle>
          <CardDescription>Pre-built workflows to get started quickly</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              {
                name: 'Email Auto-Response',
                description: 'Automatically process and respond to emails',
                icon: '📧',
                agents: 'Victoria, Terry',
              },
              {
                name: 'Code Review Pipeline',
                description: 'Multi-agent code review and analysis',
                icon: '🔍',
                agents: 'Terry, Marcus',
              },
              {
                name: 'Research & Report',
                description: 'Collaborative research and documentation',
                icon: '📚',
                agents: 'Eleanor, Victoria',
              },
            ].map((template) => (
              <Card key={template.name} className="cursor-pointer hover:shadow-md transition-all">
                <CardContent className="p-4">
                  <div className="text-3xl mb-3">{template.icon}</div>
                  <h4 className="font-semibold mb-1">{template.name}</h4>
                  <p className="text-xs text-muted-foreground mb-3">{template.description}</p>
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="text-[10px]">{template.agents}</Badge>
                    <Button size="sm" variant="ghost">Use Template</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Existing Workflows */}
      <Card>
        <CardHeader>
          <CardTitle>Your Workflows</CardTitle>
          <CardDescription>Manage and monitor existing workflows</CardDescription>
        </CardHeader>
        <CardContent>
          {workflows.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[300px] text-muted-foreground">
              <div className="text-6xl mb-4">⚙️</div>
              <p className="text-lg font-medium mb-2">No workflows yet</p>
              <p className="text-sm">Create your first workflow to automate agent tasks</p>
              <Button className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </div>
          ) : (
            <ScrollArea className="h-[400px]">
              <div className="space-y-3">
                {workflows.map((workflow) => (
                  <div
                    key={workflow.id}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`h-2 w-2 rounded-full ${statusColors[workflow.status]}`} />
                        <h4 className="font-semibold">{workflow.name}</h4>
                        <Badge variant="outline" className="text-[10px]">
                          {workflow.nodes.length} nodes
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{workflow.description}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>Executed {workflow.executionCount} times</span>
                        {workflow.lastExecuted && (
                          <span>Last run: {formatRelativeTime(workflow.lastExecuted)}</span>
                        )}
                        <span>Updated: {formatRelativeTime(workflow.updatedAt)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {workflow.status === 'active' ? (
                        <Button size="sm" variant="outline">
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline">
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      {/* Workflow Builder Canvas */}
      <Card>
        <CardHeader>
          <CardTitle>Visual Workflow Designer</CardTitle>
          <CardDescription>Drag and drop interface coming soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] rounded-lg border-2 border-dashed flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <div className="text-6xl mb-4">🎨</div>
              <p className="text-lg font-medium mb-2">Interactive Workflow Canvas</p>
              <p className="text-sm">Visual workflow builder with drag-and-drop interface</p>
              <p className="text-xs mt-2">Coming in next update</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
