'use client'

import { useState } from 'react'
import { Mail, Send, Archive, Trash2, RefreshCw, Clock, CheckCircle2, AlertCircle, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, Badge, ScrollArea, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui'
import { Button } from '@/components/ui/button'
import { useDashboardStore } from '@/store'
import { formatRelativeTime, formatDate } from '@/lib/utils'

export function EmailManagement() {
  const { emails, emailService, tasks } = useDashboardStore()
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<'all' | 'processed' | 'pending'>('all')

  const filteredEmails = emails.filter(email => {
    if (filterStatus === 'all') return true
    if (filterStatus === 'processed') return email.processed
    if (filterStatus === 'pending') return !email.processed
    return true
  })

  const selectedEmailData = emails.find(e => e.id === selectedEmail)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Email Management</h1>
          <p className="text-muted-foreground">
            Monitor and manage communications with Dell Bocca Boys agents
          </p>
        </div>
        <Button>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Email Service Status */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${emailService.isRunning ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                <Mail className={`h-6 w-6 ${emailService.isRunning ? 'text-green-500' : 'text-red-500'}`} />
              </div>
              <div>
                <p className="font-semibold">Email Service: {emailService.isRunning ? 'Active' : 'Inactive'}</p>
                <p className="text-sm text-muted-foreground">
                  {emailService.emailAddress} • Poll interval: {emailService.pollInterval}s
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-2xl font-bold">{emailService.processedMessages}</p>
                <p className="text-xs text-muted-foreground">Emails Processed</p>
              </div>
              {emailService.lastCheck && (
                <div className="text-right">
                  <p className="text-sm">{formatRelativeTime(emailService.lastCheck)}</p>
                  <p className="text-xs text-muted-foreground">Last Check</p>
                </div>
              )}
            </div>
          </div>
          {emailService.error && (
            <div className="mt-4 p-3 rounded-lg bg-red-500/10 text-red-500 text-sm flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {emailService.error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Email List & Detail */}
      <div className="grid gap-4 md:grid-cols-5">
        {/* Email List */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Emails ({filteredEmails.length})</CardTitle>
              <Tabs value={filterStatus} onValueChange={(v) => setFilterStatus(v as any)}>
                <TabsList className="h-8">
                  <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
                  <TabsTrigger value="pending" className="text-xs">Pending</TabsTrigger>
                  <TabsTrigger value="processed" className="text-xs">Processed</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[600px]">
              {filteredEmails.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
                  <Mail className="h-12 w-12 mb-4 opacity-20" />
                  <p>No emails {filterStatus !== 'all' && filterStatus}</p>
                </div>
              ) : (
                <div className="divide-y">
                  {filteredEmails.map((email) => (
                    <button
                      key={email.id}
                      onClick={() => setSelectedEmail(email.id)}
                      className={`w-full text-left p-4 hover:bg-accent transition-colors ${
                        selectedEmail === email.id ? 'bg-accent' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">{email.from}</p>
                          <p className="text-sm text-muted-foreground truncate">{email.subject}</p>
                        </div>
                        {email.processed ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                        ) : (
                          <Clock className="h-4 w-4 text-yellow-500 shrink-0" />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                        {email.bodyText}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge variant={email.processed ? "secondary" : "default"} className="text-[10px]">
                          {email.processed ? 'Processed' : 'Pending'}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(email.receivedAt)}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Email Detail */}
        <Card className="md:col-span-3">
          <CardHeader>
            <CardTitle>Email Details</CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedEmailData ? (
              <div className="flex flex-col items-center justify-center h-[500px] text-muted-foreground">
                <Mail className="h-16 w-16 mb-4 opacity-20" />
                <p>Select an email to view details</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Email Header */}
                <div className="space-y-3 pb-4 border-b">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold mb-1">{selectedEmailData.subject}</h3>
                      <p className="text-sm text-muted-foreground">From: {selectedEmailData.from}</p>
                      <p className="text-sm text-muted-foreground">To: {selectedEmailData.to}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={selectedEmailData.processed ? "secondary" : "default"}>
                        {selectedEmailData.processed ? 'Processed' : 'Pending'}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>{formatDate(selectedEmailData.receivedAt)}</span>
                    {selectedEmailData.inReplyTo && (
                      <span>• Reply to previous message</span>
                    )}
                  </div>
                </div>

                {/* Email Body */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Message</h4>
                  <ScrollArea className="h-[300px] rounded-md border p-4 bg-muted/30">
                    <div className="whitespace-pre-wrap text-sm">
                      {selectedEmailData.bodyText}
                    </div>
                  </ScrollArea>
                </div>

                {/* Associated Task */}
                {selectedEmailData.taskId && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Associated Task</h4>
                    {(() => {
                      const task = tasks.find(t => t.id === selectedEmailData.taskId)
                      return task ? (
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <p className="font-medium">{task.title}</p>
                                <p className="text-sm text-muted-foreground">{task.description}</p>
                              </div>
                              <Badge>{task.status}</Badge>
                            </div>
                            <div className="flex items-center gap-2 mt-3">
                              <Badge variant="outline" className="text-xs">{task.type}</Badge>
                              <Badge variant="outline" className="text-xs">{task.priority}</Badge>
                              <span className="text-xs text-muted-foreground">
                                {task.assignedAgents.length} agent{task.assignedAgents.length > 1 ? 's' : ''}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ) : (
                        <p className="text-sm text-muted-foreground">Task not found</p>
                      )
                    })()}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 pt-4 border-t">
                  <Button size="sm">
                    <Send className="h-4 w-4 mr-2" />
                    Reply
                  </Button>
                  <Button size="sm" variant="outline">
                    <Archive className="h-4 w-4 mr-2" />
                    Archive
                  </Button>
                  <Button size="sm" variant="outline">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
