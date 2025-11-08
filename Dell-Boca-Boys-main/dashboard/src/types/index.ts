/**
 * Type definitions for Dell Bocca Boys Dashboard
 */

export type AgentPersonality =
  | "terry_delmonaco"
  | "victoria_sterling"
  | "marcus_chen"
  | "isabella_rodriguez"
  | "eleanor_blackwood"
  | "james_oconnor"

export type AgentStatus = "active" | "idle" | "processing" | "error" | "offline"

export type TaskType =
  | "question"
  | "analysis"
  | "coding"
  | "research"
  | "planning"
  | "review"
  | "general"

export type TaskPriority = "low" | "medium" | "high" | "urgent"

export type TaskStatus = "pending" | "in_progress" | "completed" | "failed"

export interface Agent {
  id: AgentPersonality
  name: string
  role: string
  status: AgentStatus
  expertise: string[]
  signaturePhrases: string[]
  color: string
  avatar: string
  currentTask: string | null
  tasksCompleted: number
  performance: {
    successRate: number
    averageTime: number
    tasksToday: number
  }
  lastActive: Date
}

export interface Task {
  id: string
  type: TaskType
  priority: TaskPriority
  status: TaskStatus
  title: string
  description: string
  assignedAgents: AgentPersonality[]
  createdAt: Date
  updatedAt: Date
  completedAt: Date | null
  sourceEmail: EmailMessage | null
  result: string | null
  metadata: Record<string, any>
}

export interface EmailMessage {
  id: string
  messageId: string
  from: string
  to: string
  subject: string
  bodyText: string
  bodyHtml: string | null
  receivedAt: Date
  processed: boolean
  taskId: string | null
  inReplyTo: string | null
  references: string[]
}

export interface EmailServiceStatus {
  isRunning: boolean
  emailAddress: string
  pollInterval: number
  processedMessages: number
  lastCheck: Date | null
  error: string | null
}

export interface AgentCollaboration {
  id: string
  leadAgent: AgentPersonality
  contributingAgents: AgentPersonality[]
  mode: "specialist" | "consultation" | "committee"
  task: Task
  startedAt: Date
  completedAt: Date | null
  messages: CollaborationMessage[]
}

export interface CollaborationMessage {
  id: string
  fromAgent: AgentPersonality
  toAgent: AgentPersonality | "all"
  content: string
  timestamp: Date
  type: "contribution" | "question" | "suggestion" | "decision"
}

export interface WorkflowNode {
  id: string
  type: "agent" | "decision" | "action" | "trigger" | "condition"
  position: { x: number; y: number }
  data: {
    label: string
    agent?: AgentPersonality
    config: Record<string, any>
  }
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
  animated?: boolean
}

export interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  status: "draft" | "active" | "paused" | "archived"
  createdAt: Date
  updatedAt: Date
  executionCount: number
  lastExecuted: Date | null
}

export interface PerformanceMetric {
  timestamp: Date
  agentId: AgentPersonality
  metric: "task_completion" | "response_time" | "accuracy" | "collaboration"
  value: number
}

export interface SystemStats {
  totalTasks: number
  tasksToday: number
  activeAgents: number
  emailsProcessed: number
  averageResponseTime: number
  successRate: number
  uptime: number
}

export interface Notification {
  id: string
  type: "info" | "success" | "warning" | "error"
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    href: string
  }
}

export interface WebSocketMessage {
  type: "agent_update" | "task_update" | "email_received" | "collaboration" | "system_alert"
  payload: any
  timestamp: Date
}

// Agent metadata
export const AGENT_METADATA: Record<AgentPersonality, Omit<Agent, "status" | "currentTask" | "tasksCompleted" | "performance" | "lastActive">> = {
  terry_delmonaco: {
    id: "terry_delmonaco",
    name: "Terry Delmonaco",
    role: "Chief Technology & Quantitative Officer",
    expertise: [
      "Software Engineering",
      "Quantitative Analytics",
      "Derivatives",
      "Economics",
      "Mathematics",
      "Statistics",
      "Psychology"
    ],
    signaturePhrases: [
      "He's a real Bobby-boy!!",
      "You wanna tro downs?",
      "Ey, yo! Sammy!",
      "Whaddya hear, whaddya say?"
    ],
    color: "#FF6B35",
    avatar: "/avatars/terry.png"
  },
  victoria_sterling: {
    id: "victoria_sterling",
    name: "Victoria Sterling",
    role: "Strategic Operations & Research Director",
    expertise: [
      "Strategic Planning",
      "Operations Research",
      "Market Analysis",
      "Competitive Intelligence"
    ],
    signaturePhrases: [
      "Let's architect this brilliantly, sweetheart",
      "The strategic landscape reveals fascinating patterns"
    ],
    color: "#9B59B6",
    avatar: "/avatars/victoria.png"
  },
  marcus_chen: {
    id: "marcus_chen",
    name: "Marcus Chen",
    role: "Systems Integration & Design Lead",
    expertise: [
      "System Architecture",
      "Integration Patterns",
      "Scalability Design",
      "Security Frameworks"
    ],
    signaturePhrases: [
      "The system reveals its truth to those who listen",
      "Like water flowing around obstacles..."
    ],
    color: "#3498DB",
    avatar: "/avatars/marcus.png"
  },
  isabella_rodriguez: {
    id: "isabella_rodriguez",
    name: "Isabella Rodriguez",
    role: "Creative Innovation & User Experience Chief",
    expertise: [
      "Design Thinking",
      "User Psychology",
      "Creative Problem-Solving",
      "Innovation Methodologies"
    ],
    signaturePhrases: [
      "¡Oye, this is going to be absolutely gorgeous!",
      "Mi amor, let's make this beautiful"
    ],
    color: "#E91E63",
    avatar: "/avatars/isabella.png"
  },
  eleanor_blackwood: {
    id: "eleanor_blackwood",
    name: "Eleanor Blackwood",
    role: "Research & Academic Excellence Coordinator",
    expertise: [
      "Academic Research",
      "Literature Review",
      "Methodology Design",
      "Citation Management"
    ],
    signaturePhrases: [
      "The literature suggests a fascinating convergence here",
      "Drawing upon peer-reviewed research..."
    ],
    color: "#16A085",
    avatar: "/avatars/eleanor.png"
  },
  james_oconnor: {
    id: "james_oconnor",
    name: "James O'Connor",
    role: "Project Command & Execution Director",
    expertise: [
      "Project Management",
      "Team Leadership",
      "Resource Allocation",
      "Risk Mitigation"
    ],
    signaturePhrases: [
      "Mission parameters are clear, team - let's execute",
      "All hands on deck, people"
    ],
    color: "#E67E22",
    avatar: "/avatars/james.png"
  }
}

// Task type colors
export const TASK_TYPE_COLORS: Record<TaskType, string> = {
  question: "#3B82F6",
  analysis: "#8B5CF6",
  coding: "#10B981",
  research: "#F59E0B",
  planning: "#EC4899",
  review: "#6366F1",
  general: "#64748B"
}

// Priority colors
export const PRIORITY_COLORS: Record<TaskPriority, string> = {
  low: "#10B981",
  medium: "#F59E0B",
  high: "#F97316",
  urgent: "#EF4444"
}
