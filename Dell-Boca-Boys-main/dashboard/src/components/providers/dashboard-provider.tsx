'use client'

import { useEffect } from 'react'
import { useDashboardStore } from '@/store'
import { useWebSocket } from '@/hooks/useWebSocket'

export function DashboardProvider({ children }: { children: React.ReactNode }) {
  const { initializeAgents } = useDashboardStore()
  const { isConnected } = useWebSocket()

  useEffect(() => {
    // Initialize agents on mount
    initializeAgents()
  }, [initializeAgents])

  return (
    <>
      {children}
      {/* WebSocket connection indicator */}
      <div className="fixed bottom-4 right-4 z-50">
        <div
          className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium shadow-lg ${
            isConnected
              ? 'bg-green-500 text-white'
              : 'bg-red-500 text-white'
          }`}
        >
          <div
            className={`h-2 w-2 rounded-full ${
              isConnected ? 'bg-white animate-pulse' : 'bg-white/50'
            }`}
          />
          {isConnected ? 'Live' : 'Disconnected'}
        </div>
      </div>
    </>
  )
}
