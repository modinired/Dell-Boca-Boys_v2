'use client'

import React, { useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Badge } from '@/components/ui'
import { useDashboardStore } from '@/store'
import { AGENT_METADATA } from '@/types'
import type { AgentPersonality } from '@/types'

const AgentNode = ({ data }: { data: any }) => {
  const statusColors = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    processing: 'bg-blue-500',
    error: 'bg-red-500',
    offline: 'bg-gray-500',
  }

  return (
    <div
      className="px-4 py-3 shadow-lg rounded-lg bg-card border-2 min-w-[180px]"
      style={{ borderColor: data.color }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className={`h-2 w-2 rounded-full ${statusColors[data.status]}`} />
        <div className="font-bold text-sm">{data.label}</div>
      </div>
      <div className="text-xs text-muted-foreground mb-2">{data.role}</div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Tasks:</span>
        <span className="font-semibold">{data.tasksCompleted}</span>
      </div>
      {data.currentTask && (
        <div className="mt-2 pt-2 border-t">
          <div className="text-[10px] text-muted-foreground">Processing task</div>
        </div>
      )}
    </div>
  )
}

const nodeTypes = {
  agent: AgentNode,
}

export function AgentNetwork() {
  const { agents, collaborations, tasks } = useDashboardStore()

  // Create nodes from agents
  const initialNodes: Node[] = agents.map((agent, index) => {
    const angle = (index / agents.length) * 2 * Math.PI
    const radius = 250
    return {
      id: agent.id,
      type: 'agent',
      position: {
        x: 400 + radius * Math.cos(angle),
        y: 300 + radius * Math.sin(angle),
      },
      data: {
        label: agent.name,
        role: agent.role.split(' ').slice(0, 2).join(' '),
        color: agent.color,
        status: agent.status,
        currentTask: agent.currentTask,
        tasksCompleted: agent.tasksCompleted,
      },
    }
  })

  // Create edges from collaborations
  const initialEdges: Edge[] = collaborations.flatMap((collab) =>
    collab.contributingAgents.map((contributorId, index) => ({
      id: `${collab.leadAgent}-${contributorId}-${index}`,
      source: collab.leadAgent,
      target: contributorId,
      type: 'smoothstep',
      animated: collab.completedAt === null,
      style: { stroke: '#8B5CF6', strokeWidth: 2 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#8B5CF6',
      },
    }))
  )

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // Calculate network stats
  const activeCollaborations = collaborations.filter(c => c.completedAt === null).length
  const totalConnections = edges.length
  const networkDensity = (totalConnections / (agents.length * (agents.length - 1))).toFixed(2)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Agent Collaboration Network</h1>
        <p className="text-muted-foreground">
          Visualize real-time interactions between CESAR agents
        </p>
      </div>

      {/* Network Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Agents</p>
            <p className="text-2xl font-bold mt-1">{agents.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Active Collaborations</p>
            <p className="text-2xl font-bold mt-1">{activeCollaborations}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Connections</p>
            <p className="text-2xl font-bold mt-1">{totalConnections}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Network Density</p>
            <p className="text-2xl font-bold mt-1">{networkDensity}</p>
          </CardContent>
        </Card>
      </div>

      {/* Network Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Interactive Network Graph</CardTitle>
          <CardDescription>
            Drag nodes to rearrange • Click and drag to pan • Scroll to zoom
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[600px] rounded-lg border bg-muted/30">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-left"
            >
              <Background />
              <Controls />
            </ReactFlow>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle>Network Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-semibold mb-3">Agent Status</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm">Active - Currently processing</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-blue-500" />
                  <span className="text-sm">Processing - Working on task</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-yellow-500" />
                  <span className="text-sm">Idle - Waiting for tasks</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-gray-500" />
                  <span className="text-sm">Offline - Not connected</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-3">Connection Types</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-0.5 w-8 bg-purple-500" />
                  <span className="text-sm">Active collaboration</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-0.5 w-8 bg-purple-500 opacity-50" />
                  <span className="text-sm">Completed collaboration</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
