import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { WorkflowRequestCard } from '@/components/customer/WorkflowRequestCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, X } from 'lucide-react';
import { WorkflowStatus, Priority, WorkflowCategory } from '@/types';

const statusOptions: WorkflowStatus[] = [
  'draft',
  'submitted',
  'in_review',
  'in_progress',
  'testing',
  'deployed',
  'completed',
  'on_hold',
  'cancelled',
  'failed',
];

const priorityOptions: Priority[] = ['low', 'medium', 'high', 'urgent'];

const categoryOptions: WorkflowCategory[] = [
  'data_processing',
  'integration',
  'automation',
  'reporting',
  'notification',
  'custom',
];

export function Requests() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<Priority | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<WorkflowCategory | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 12;

  const { data, isLoading, error } = useQuery({
    queryKey: ['requests', page, searchQuery, statusFilter, priorityFilter, categoryFilter],
    queryFn: () =>
      apiService.getWorkflowRequests({
        limit: pageSize,
        offset: page * pageSize,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        category: categoryFilter || undefined,
        search: searchQuery || undefined,
      }),
  });

  const hasFilters = statusFilter || priorityFilter || categoryFilter;

  const clearFilters = () => {
    setStatusFilter(null);
    setPriorityFilter(null);
    setCategoryFilter(null);
    setSearchQuery('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Requests</h1>
          <p className="text-muted-foreground mt-2">
            Manage and track your workflow automation requests
          </p>
        </div>
        <Link to="/requests/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Request
          </Button>
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search requests..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-2 items-center">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Filters:</span>

          {/* Status Filter */}
          <select
            className="text-sm border rounded-md px-3 py-1.5 bg-white"
            value={statusFilter || ''}
            onChange={(e) => setStatusFilter((e.target.value as WorkflowStatus) || null)}
          >
            <option value="">All Statuses</option>
            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>

          {/* Priority Filter */}
          <select
            className="text-sm border rounded-md px-3 py-1.5 bg-white"
            value={priorityFilter || ''}
            onChange={(e) => setPriorityFilter((e.target.value as Priority) || null)}
          >
            <option value="">All Priorities</option>
            {priorityOptions.map((priority) => (
              <option key={priority} value={priority}>
                {priority.toUpperCase()}
              </option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            className="text-sm border rounded-md px-3 py-1.5 bg-white"
            value={categoryFilter || ''}
            onChange={(e) => setCategoryFilter((e.target.value as WorkflowCategory) || null)}
          >
            <option value="">All Categories</option>
            {categoryOptions.map((category) => (
              <option key={category} value={category}>
                {category.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>

          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear Filters
            </Button>
          )}
        </div>
      </div>

      {/* Results Count */}
      {data && (
        <div className="text-sm text-muted-foreground">
          Showing {data.data.length} of {data.total} requests
        </div>
      )}

      {/* Requests Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground">Loading requests...</div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load requests</p>
        </div>
      ) : data?.data && data.data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.data.map((request) => (
            <WorkflowRequestCard key={request.id} request={request} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No requests found</p>
          {hasFilters ? (
            <Button variant="outline" onClick={clearFilters}>
              Clear Filters
            </Button>
          ) : (
            <Link to="/requests/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Request
              </Button>
            </Link>
          )}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > pageSize && (
        <div className="flex items-center justify-center gap-2 mt-6">
          <Button
            variant="outline"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            Previous
          </Button>
          <div className="text-sm text-muted-foreground">
            Page {page + 1} of {Math.ceil(data.total / pageSize)}
          </div>
          <Button
            variant="outline"
            onClick={() => setPage((p) => p + 1)}
            disabled={(page + 1) * pageSize >= data.total}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
