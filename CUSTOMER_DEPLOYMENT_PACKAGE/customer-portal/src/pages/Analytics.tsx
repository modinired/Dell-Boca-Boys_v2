import { useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MetricCard } from '@/components/customer/MetricCard';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
} from 'lucide-react';
import { formatNumber, formatPercentage, formatDuration } from '@/utils/format';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', 'detailed'],
    queryFn: () => apiService.getCustomerAnalytics(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="text-center">
          <Activity className="h-12 w-12 animate-spin mx-auto text-blue-600" />
          <p className="mt-4 text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No analytics data available</p>
      </div>
    );
  }

  const metrics = [
    {
      title: 'Total Executions',
      value: formatNumber(analytics.totalExecutions),
      subtitle: 'Across all workflows',
      icon: Activity,
      iconColor: 'text-blue-600',
      iconBgColor: 'bg-blue-100',
      trend: {
        value: analytics.executionsTrend || 0,
        label: 'vs last month',
      },
    },
    {
      title: 'Success Rate',
      value: formatPercentage(analytics.successRate),
      subtitle: 'Overall performance',
      icon: CheckCircle,
      iconColor: 'text-green-600',
      iconBgColor: 'bg-green-100',
      trend: {
        value: analytics.successRateTrend || 0,
        label: 'vs last month',
      },
    },
    {
      title: 'Avg. Execution Time',
      value: `${analytics.averageExecutionTime || 0}ms`,
      subtitle: 'Per workflow run',
      icon: Clock,
      iconColor: 'text-purple-600',
      iconBgColor: 'bg-purple-100',
    },
    {
      title: 'Error Rate',
      value: formatPercentage(1 - (analytics.successRate || 0)),
      subtitle: 'Failed executions',
      icon: AlertCircle,
      iconColor: 'text-red-600',
      iconBgColor: 'bg-red-100',
      trend: {
        value: -(analytics.successRateTrend || 0),
        label: 'vs last month',
      },
    },
    {
      title: 'Active Workflows',
      value: analytics.activeWorkflows || 0,
      subtitle: 'Currently running',
      icon: Zap,
      iconColor: 'text-yellow-600',
      iconBgColor: 'bg-yellow-100',
    },
    {
      title: 'Total Saved Time',
      value: formatDuration((analytics.totalSavedTime || 0) * 1000),
      subtitle: 'Through automation',
      icon: TrendingUp,
      iconColor: 'text-teal-600',
      iconBgColor: 'bg-teal-100',
    },
  ];

  // Category distribution data
  const categoryData = analytics.categoryDistribution
    ? Object.entries(analytics.categoryDistribution).map(([name, value]) => ({
        name: name.replace('_', ' ').toUpperCase(),
        value,
      }))
    : [];

  // Status distribution data
  const statusData = analytics.statusDistribution
    ? Object.entries(analytics.statusDistribution).map(([name, value]) => ({
        name: name.replace('_', ' ').toUpperCase(),
        value,
      }))
    : [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics & Insights</h1>
        <p className="text-muted-foreground mt-2">
          Detailed performance metrics and trends for your workflow automation
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Execution History */}
        {analytics.executionHistory && analytics.executionHistory.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
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

        {/* Success Rate Trend */}
        {analytics.successRateHistory && analytics.successRateHistory.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Success Rate Trend</CardTitle>
              <CardDescription>Workflow success rate over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.successRateHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Category Distribution */}
        {categoryData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Workflows by Category</CardTitle>
              <CardDescription>Distribution of workflows across categories</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Status Distribution */}
        {statusData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Requests by Status</CardTitle>
              <CardDescription>Current status of all workflow requests</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Top Performing Workflows */}
      {analytics.topWorkflows && analytics.topWorkflows.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Workflows</CardTitle>
            <CardDescription>Most frequently executed workflows</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.topWorkflows.map((workflow, index) => (
                <div key={workflow.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{workflow.name}</p>
                      <p className="text-sm text-muted-foreground">{workflow.category}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{formatNumber(workflow.executionCount)} executions</p>
                    <p className="text-sm text-green-600">{formatPercentage(workflow.successRate)} success</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
