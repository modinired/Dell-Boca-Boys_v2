import { useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { MetricCard } from '@/components/customer/MetricCard';
import { WorkflowRequestCard } from '@/components/customer/WorkflowRequestCard';
import { WorkflowCard } from '@/components/customer/WorkflowCard';
import { NotificationItem } from '@/components/customer/NotificationItem';
import {
  FileText,
  Workflow,
  CheckCircle,
  TrendingUp,
  Clock,
  Activity,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNotificationStore } from '@/stores/notificationStore';

export function Dashboard() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => apiService.getCustomerAnalytics(),
  });

  const { data: recentRequests, isLoading: requestsLoading } = useQuery({
    queryKey: ['requests', 'recent'],
    queryFn: () => apiService.getWorkflowRequests({ limit: 3, offset: 0 }),
  });

  const { data: activeWorkflows, isLoading: workflowsLoading } = useQuery({
    queryKey: ['workflows', 'active'],
    queryFn: () => apiService.getCompletedWorkflows({ status: 'active', limit: 3, offset: 0 }),
  });

  const { notifications } = useNotificationStore();
  const recentNotifications = notifications.slice(0, 5);

  if (analyticsLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="text-center">
          <Activity className="h-12 w-12 animate-spin mx-auto text-blue-600" />
          <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const metrics = [
    {
      title: 'Total Requests',
      value: analytics?.totalRequests || 0,
      subtitle: 'All workflow requests',
      icon: FileText,
      iconColor: 'text-blue-600',
      iconBgColor: 'bg-blue-100',
      trend: {
        value: analytics?.requestsTrend || 0,
        label: 'vs last month',
      },
    },
    {
      title: 'Active Workflows',
      value: analytics?.activeWorkflows || 0,
      subtitle: 'Currently running',
      icon: Workflow,
      iconColor: 'text-green-600',
      iconBgColor: 'bg-green-100',
    },
    {
      title: 'Completed',
      value: analytics?.completedWorkflows || 0,
      subtitle: 'Successfully deployed',
      icon: CheckCircle,
      iconColor: 'text-purple-600',
      iconBgColor: 'bg-purple-100',
      trend: {
        value: analytics?.completionTrend || 0,
        label: 'vs last month',
      },
    },
    {
      title: 'Avg. Completion Time',
      value: analytics?.averageCompletionTime ? `${analytics.averageCompletionTime} days` : 'N/A',
      subtitle: 'From request to deploy',
      icon: Clock,
      iconColor: 'text-orange-600',
      iconBgColor: 'bg-orange-100',
    },
    {
      title: 'Success Rate',
      value: analytics?.successRate ? `${(analytics.successRate * 100).toFixed(1)}%` : 'N/A',
      subtitle: 'Workflow executions',
      icon: TrendingUp,
      iconColor: 'text-teal-600',
      iconBgColor: 'bg-teal-100',
      trend: {
        value: analytics?.successRateTrend || 0,
        label: 'vs last month',
      },
    },
    {
      title: 'Total Executions',
      value: analytics?.totalExecutions || 0,
      subtitle: 'Across all workflows',
      icon: Activity,
      iconColor: 'text-pink-600',
      iconBgColor: 'bg-pink-100',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back! Here's an overview of your workflow automation.
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {/* Activity Chart */}
      {analytics?.executionHistory && (
        <Card>
          <CardHeader>
            <CardTitle>Execution Activity</CardTitle>
            <CardDescription>Daily workflow executions over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.executionHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Two Column Layout */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Requests */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Requests</CardTitle>
              <CardDescription>Your latest workflow requests</CardDescription>
            </div>
            <Link to="/requests">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="space-y-4">
            {requestsLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : recentRequests?.data && recentRequests.data.length > 0 ? (
              recentRequests.data.map((request) => (
                <WorkflowRequestCard key={request.id} request={request} />
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No requests yet</p>
                <Link to="/requests/new">
                  <Button>Create Your First Request</Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Active Workflows */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Active Workflows</CardTitle>
              <CardDescription>Currently running automation</CardDescription>
            </div>
            <Link to="/workflows">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="space-y-4">
            {workflowsLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : activeWorkflows?.data && activeWorkflows.data.length > 0 ? (
              activeWorkflows.data.map((workflow) => (
                <WorkflowCard key={workflow.id} workflow={workflow} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No active workflows
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Notifications */}
      {recentNotifications.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Notifications</CardTitle>
              <CardDescription>Latest updates and alerts</CardDescription>
            </div>
            <Link to="/notifications">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentNotifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
