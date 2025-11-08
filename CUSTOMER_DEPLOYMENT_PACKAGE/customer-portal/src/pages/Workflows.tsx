import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { WorkflowCard } from '@/components/customer/WorkflowCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, X } from 'lucide-react';
import { toast } from 'sonner';

export function Workflows() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'active' | 'inactive' | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 12;
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['workflows', page, searchQuery, statusFilter],
    queryFn: () =>
      apiService.getCompletedWorkflows({
        limit: pageSize,
        offset: page * pageSize,
        status: statusFilter || undefined,
        search: searchQuery || undefined,
      }),
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      apiService.toggleWorkflowStatus(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      toast.success('Workflow status updated successfully');
    },
    onError: () => {
      toast.error('Failed to update workflow status');
    },
  });

  const executeMutation = useMutation({
    mutationFn: (id: string) => apiService.executeWorkflow(id),
    onSuccess: () => {
      toast.success('Workflow execution started');
    },
    onError: () => {
      toast.error('Failed to execute workflow');
    },
  });

  const handleToggleStatus = (id: string, isActive: boolean) => {
    toggleStatusMutation.mutate({ id, isActive });
  };

  const handleExecute = (id: string) => {
    executeMutation.mutate(id);
  };

  const clearFilters = () => {
    setStatusFilter(null);
    setSearchQuery('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Workflows</h1>
        <p className="text-muted-foreground mt-2">
          View and manage your deployed workflow automations
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search workflows..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-2 items-center">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Status:</span>

          <Button
            variant={statusFilter === null ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter(null)}
          >
            All
          </Button>
          <Button
            variant={statusFilter === 'active' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('active')}
          >
            Active
          </Button>
          <Button
            variant={statusFilter === 'inactive' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('inactive')}
          >
            Inactive
          </Button>

          {(statusFilter || searchQuery) && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear Filters
            </Button>
          )}
        </div>
      </div>

      {/* Results Count */}
      {data && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {data.data.length} of {data.total} workflows
          </div>
          {data.data.length > 0 && (
            <div className="flex items-center gap-4 text-sm">
              <Badge variant="success">
                {data.data.filter((w) => w.isActive).length} Active
              </Badge>
              <Badge variant="secondary">
                {data.data.filter((w) => !w.isActive).length} Inactive
              </Badge>
            </div>
          )}
        </div>
      )}

      {/* Workflows Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground">Loading workflows...</div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load workflows</p>
        </div>
      ) : data?.data && data.data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.data.map((workflow) => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onToggleStatus={handleToggleStatus}
              onExecute={handleExecute}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No workflows found</p>
          {statusFilter || searchQuery ? (
            <Button variant="outline" onClick={clearFilters}>
              Clear Filters
            </Button>
          ) : (
            <p className="text-sm text-muted-foreground">
              Workflows will appear here once your requests are deployed
            </p>
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
