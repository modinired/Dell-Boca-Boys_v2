/**
 * Zustand Store for Dell Bocca Boys Dashboard
 * Manages global state with real-time updates
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type {
  Agent,
  Task,
  EmailMessage,
  EmailServiceStatus,
  AgentCollaboration,
  Workflow,
  SystemStats,
  Notification,
  AgentPersonality,
  AgentStatus,
} from '@/types'
import { AGENT_METADATA } from '@/types'

interface DashboardState {
  // Agents
  agents: Agent[]
  updateAgentStatus: (agentId: AgentPersonality, status: AgentStatus) => void
  updateAgentTask: (agentId: AgentPersonality, taskId: string | null) => void
  incrementAgentTasks: (agentId: AgentPersonality) => void

  // Tasks
  tasks: Task[]
  addTask: (task: Task) => void
  updateTask: (taskId: string, updates: Partial<Task>) => void
  removeTask: (taskId: string) => void

  // Emails
  emails: EmailMessage[]
  addEmail: (email: EmailMessage) => void
  markEmailProcessed: (emailId: string, taskId: string) => void

  // Email Service
  emailService: EmailServiceStatus
  updateEmailService: (status: Partial<EmailServiceStatus>) => void

  // Collaborations
  collaborations: AgentCollaboration[]
  addCollaboration: (collaboration: AgentCollaboration) => void
  updateCollaboration: (id: string, updates: Partial<AgentCollaboration>) => void

  // Workflows
  workflows: Workflow[]
  addWorkflow: (workflow: Workflow) => void
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void
  deleteWorkflow: (id: string) => void

  // System Stats
  systemStats: SystemStats
  updateSystemStats: (stats: Partial<SystemStats>) => void

  // Notifications
  notifications: Notification[]
  addNotification: (notification: Notification) => void
  markNotificationRead: (id: string) => void
  clearNotifications: () => void

  // UI State
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  darkMode: boolean
  toggleDarkMode: () => void

  // Initialize
  initializeAgents: () => void
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        agents: [],
        tasks: [],
        emails: [],
        collaborations: [],
        workflows: [],
        notifications: [],

        emailService: {
          isRunning: false,
          emailAddress: 'ace.llc.nyc@gmail.com',
          pollInterval: 60,
          processedMessages: 0,
          lastCheck: null,
          error: null,
        },

        systemStats: {
          totalTasks: 0,
          tasksToday: 0,
          activeAgents: 0,
          emailsProcessed: 0,
          averageResponseTime: 0,
          successRate: 0,
          uptime: 0,
        },

        sidebarCollapsed: false,
        darkMode: false,

        // Agent actions
        updateAgentStatus: (agentId, status) =>
          set((state) => ({
            agents: state.agents.map((agent) =>
              agent.id === agentId
                ? { ...agent, status, lastActive: new Date() }
                : agent
            ),
          })),

        updateAgentTask: (agentId, taskId) =>
          set((state) => ({
            agents: state.agents.map((agent) =>
              agent.id === agentId ? { ...agent, currentTask: taskId } : agent
            ),
          })),

        incrementAgentTasks: (agentId) =>
          set((state) => ({
            agents: state.agents.map((agent) =>
              agent.id === agentId
                ? {
                    ...agent,
                    tasksCompleted: agent.tasksCompleted + 1,
                    performance: {
                      ...agent.performance,
                      tasksToday: agent.performance.tasksToday + 1,
                    },
                  }
                : agent
            ),
          })),

        // Task actions
        addTask: (task) =>
          set((state) => ({
            tasks: [task, ...state.tasks],
            systemStats: {
              ...state.systemStats,
              totalTasks: state.systemStats.totalTasks + 1,
              tasksToday: state.systemStats.tasksToday + 1,
            },
          })),

        updateTask: (taskId, updates) =>
          set((state) => ({
            tasks: state.tasks.map((task) =>
              task.id === taskId
                ? { ...task, ...updates, updatedAt: new Date() }
                : task
            ),
          })),

        removeTask: (taskId) =>
          set((state) => ({
            tasks: state.tasks.filter((task) => task.id !== taskId),
          })),

        // Email actions
        addEmail: (email) =>
          set((state) => ({
            emails: [email, ...state.emails],
          })),

        markEmailProcessed: (emailId, taskId) =>
          set((state) => ({
            emails: state.emails.map((email) =>
              email.id === emailId
                ? { ...email, processed: true, taskId }
                : email
            ),
            emailService: {
              ...state.emailService,
              processedMessages: state.emailService.processedMessages + 1,
            },
            systemStats: {
              ...state.systemStats,
              emailsProcessed: state.systemStats.emailsProcessed + 1,
            },
          })),

        // Email service actions
        updateEmailService: (status) =>
          set((state) => ({
            emailService: { ...state.emailService, ...status },
          })),

        // Collaboration actions
        addCollaboration: (collaboration) =>
          set((state) => ({
            collaborations: [collaboration, ...state.collaborations],
          })),

        updateCollaboration: (id, updates) =>
          set((state) => ({
            collaborations: state.collaborations.map((collab) =>
              collab.id === id ? { ...collab, ...updates } : collab
            ),
          })),

        // Workflow actions
        addWorkflow: (workflow) =>
          set((state) => ({
            workflows: [workflow, ...state.workflows],
          })),

        updateWorkflow: (id, updates) =>
          set((state) => ({
            workflows: state.workflows.map((workflow) =>
              workflow.id === id
                ? { ...workflow, ...updates, updatedAt: new Date() }
                : workflow
            ),
          })),

        deleteWorkflow: (id) =>
          set((state) => ({
            workflows: state.workflows.filter((workflow) => workflow.id !== id),
          })),

        // System stats actions
        updateSystemStats: (stats) =>
          set((state) => ({
            systemStats: { ...state.systemStats, ...stats },
          })),

        // Notification actions
        addNotification: (notification) =>
          set((state) => ({
            notifications: [notification, ...state.notifications],
          })),

        markNotificationRead: (id) =>
          set((state) => ({
            notifications: state.notifications.map((notif) =>
              notif.id === id ? { ...notif, read: true } : notif
            ),
          })),

        clearNotifications: () =>
          set({ notifications: [] }),

        // UI actions
        toggleSidebar: () =>
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

        toggleDarkMode: () =>
          set((state) => ({ darkMode: !state.darkMode })),

        // Initialize agents from metadata
        initializeAgents: () =>
          set({
            agents: Object.values(AGENT_METADATA).map((meta) => ({
              ...meta,
              status: 'idle' as AgentStatus,
              currentTask: null,
              tasksCompleted: 0,
              performance: {
                successRate: 0,
                averageTime: 0,
                tasksToday: 0,
              },
              lastActive: new Date(),
            })),
          }),
      }),
      {
        name: 'dell-bocca-boys-dashboard',
        partialize: (state) => ({
          darkMode: state.darkMode,
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    )
  )
)

// Selectors
export const selectActiveAgents = (state: DashboardState) =>
  state.agents.filter((agent) => agent.status === 'active')

export const selectPendingTasks = (state: DashboardState) =>
  state.tasks.filter((task) => task.status === 'pending')

export const selectInProgressTasks = (state: DashboardState) =>
  state.tasks.filter((task) => task.status === 'in_progress')

export const selectUnprocessedEmails = (state: DashboardState) =>
  state.emails.filter((email) => !email.processed)

export const selectUnreadNotifications = (state: DashboardState) =>
  state.notifications.filter((notif) => !notif.read)
