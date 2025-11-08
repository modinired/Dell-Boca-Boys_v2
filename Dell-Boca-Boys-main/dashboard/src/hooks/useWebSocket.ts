/**
 * WebSocket Hook for Real-Time Updates
 * Connects to Dell Bocca Boys backend WebSocket for live agent updates
 */

import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useDashboardStore } from '@/store'
import type { WebSocketMessage } from '@/types'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000'

export function useWebSocket() {
  const socket useRef<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)

  const {
    updateAgentStatus,
    updateAgentTask,
    addTask,
    updateTask,
    addEmail,
    addNotification,
    addCollaboration,
    updateEmailService,
  } = useDashboardStore()

  useEffect(() => {
    // Initialize Socket.IO connection
    socket.current = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    })

    // Connection events
    socket.current.on('connect', () => {
      console.log('✓ WebSocket connected')
      setIsConnected(true)

      // Subscribe to agent topics
      socket.current?.emit('subscribe', { topic: 'agent_updates' })
      socket.current?.emit('subscribe', { topic: 'task_updates' })
      socket.current?.emit('subscribe', { topic: 'email_notifications' })
      socket.current?.emit('subscribe', { topic: 'system_alerts' })
    })

    socket.current.on('disconnect', () => {
      console.log('✗ WebSocket disconnected')
      setIsConnected(false)
    })

    socket.current.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      setIsConnected(false)
    })

    // Message handlers
    socket.current.on('agent_update', (data: any) => {
      const message: WebSocketMessage = {
        type: 'agent_update',
        payload: data,
        timestamp: new Date(),
      }
      setLastMessage(message)

      if (data.agentId && data.status) {
        updateAgentStatus(data.agentId, data.status)
      }
      if (data.agentId && data.taskId !== undefined) {
        updateAgentTask(data.agentId, data.taskId)
      }
    })

    socket.current.on('task_update', (data: any) => {
      const message: WebSocketMessage = {
        type: 'task_update',
        payload: data,
        timestamp: new Date(),
      }
      setLastMessage(message)

      if (data.action === 'created' && data.task) {
        addTask(data.task)
        addNotification({
          id: `notif_${Date.now()}`,
          type: 'info',
          title: 'New Task',
          message: `New ${data.task.type} task: ${data.task.title}`,
          timestamp: new Date(),
          read: false,
        })
      } else if (data.action === 'updated' && data.taskId && data.updates) {
        updateTask(data.taskId, data.updates)
      }
    })

    socket.current.on('email_received', (data: any) => {
      const message: WebSocketMessage = {
        type: 'email_received',
        payload: data,
        timestamp: new Date(),
      }
      setLastMessage(message)

      if (data.email) {
        addEmail(data.email)
        addNotification({
          id: `notif_${Date.now()}`,
          type: 'info',
          title: 'New Email',
          message: `From: ${data.email.from}\nSubject: ${data.email.subject}`,
          timestamp: new Date(),
          read: false,
        })
      }

      if (data.serviceStatus) {
        updateEmailService(data.serviceStatus)
      }
    })

    socket.current.on('collaboration_update', (data: any) => {
      const message: WebSocketMessage = {
        type: 'collaboration',
        payload: data,
        timestamp: new Date(),
      }
      setLastMessage(message)

      if (data.action === 'started' && data.collaboration) {
        addCollaboration(data.collaboration)
      }
    })

    socket.current.on('system_alert', (data: any) => {
      const message: WebSocketMessage = {
        type: 'system_alert',
        payload: data,
        timestamp: new Date(),
      }
      setLastMessage(message)

      addNotification({
        id: `notif_${Date.now()}`,
        type: data.severity || 'info',
        title: data.title || 'System Alert',
        message: data.message,
        timestamp: new Date(),
        read: false,
      })
    })

    // Cleanup on unmount
    return () => {
      if (socket.current) {
        socket.current.disconnect()
      }
    }
  }, [
    updateAgentStatus,
    updateAgentTask,
    addTask,
    updateTask,
    addEmail,
    addNotification,
    addCollaboration,
    updateEmailService,
  ])

  // Emit event helper
  const emit = (event: string, data: any) => {
    if (socket.current && isConnected) {
      socket.current.emit(event, data)
    } else {
      console.warn('WebSocket not connected, cannot emit event:', event)
    }
  }

  return {
    isConnected,
    lastMessage,
    emit,
  }
}
