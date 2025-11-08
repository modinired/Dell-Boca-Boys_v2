import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { WorkflowTemplateCard } from '@/components/customer/WorkflowTemplateCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, X, TrendingUp, Star } from 'lucide-react';
import { WorkflowCategory } from '@/types';
import { toast } from 'sonner';

const categoryOptions: WorkflowCategory[] = [
  'data_processing',
  'integration',
  'automation',
  'reporting',
  'notification',
  'custom',
];

const complexityOptions = ['simple', 'moderate', 'complex', 'enterprise'];

export function Templates() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<WorkflowCategory | null>(null);
  const [complexityFilter, setComplexityFilter] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'popular' | 'rating'>('popular');
  const [page, setPage] = useState(0);
  const pageSize = 12;

  const { data, isLoading, error } = useQuery({
    queryKey: ['templates', page, searchQuery, categoryFilter, complexityFilter, sortBy],
    queryFn: () =>
      apiService.getWorkflowTemplates({
        limit: pageSize,
        offset: page * pageSize,
        category: categoryFilter || undefined,
        search: searchQuery || undefined,
      }),
  });

  const useTemplateMutation = useMutation({
    mutationFn: (templateId: string) => {
      // This would create a new request based on the template
      // For now, we'll navigate to the new request page with the template ID
      return Promise.resolve(templateId);
    },
    onSuccess: (templateId) => {
      navigate(`/requests/new?templateId=${templateId}`);
      toast.success('Template selected! Fill in the details to create your request.');
    },
  });

  const handleUseTemplate = (id: string) => {
    useTemplateMutation.mutate(id);
  };

  const clearFilters = () => {
    setCategoryFilter(null);
    setComplexityFilter(null);
    setSearchQuery('');
  };

  const filteredAndSortedData = data?.data
    ? (() => {
        let filtered = data.data;

        // Apply complexity filter
        if (complexityFilter) {
          filtered = filtered.filter((t) => t.complexity === complexityFilter);
        }

        // Apply sorting
        if (sortBy === 'popular') {
          filtered = [...filtered].sort((a, b) => b.usageCount - a.usageCount);
        } else if (sortBy === 'rating') {
          filtered = [...filtered].sort((a, b) => b.rating - a.rating);
        }

        return filtered;
      })()
    : [];

  const hasFilters = categoryFilter || complexityFilter;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workflow Template Library</h1>
        <p className="text-muted-foreground mt-2">
          Browse and deploy pre-built workflow automation templates
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter Row */}
        <div className="flex flex-wrap gap-2 items-center">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Filters:</span>

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

          {/* Complexity Filter */}
          <select
            className="text-sm border rounded-md px-3 py-1.5 bg-white"
            value={complexityFilter || ''}
            onChange={(e) => setComplexityFilter(e.target.value || null)}
          >
            <option value="">All Complexity Levels</option>
            {complexityOptions.map((complexity) => (
              <option key={complexity} value={complexity}>
                {complexity.toUpperCase()}
              </option>
            ))}
          </select>

          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear Filters
            </Button>
          )}

          {/* Sort Options */}
          <div className="ml-auto flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <Button
              variant={sortBy === 'popular' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('popular')}
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              Most Popular
            </Button>
            <Button
              variant={sortBy === 'rating' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('rating')}
            >
              <Star className="h-4 w-4 mr-1" />
              Highest Rated
            </Button>
          </div>
        </div>
      </div>

      {/* Results Count */}
      {data && (
        <div className="text-sm text-muted-foreground">
          Showing {filteredAndSortedData.length} templates
        </div>
      )}

      {/* Templates Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground">Loading templates...</div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load templates</p>
        </div>
      ) : filteredAndSortedData && filteredAndSortedData.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredAndSortedData.map((template) => (
            <WorkflowTemplateCard
              key={template.id}
              template={template}
              onUseTemplate={handleUseTemplate}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No templates found</p>
          {hasFilters && (
            <Button variant="outline" onClick={clearFilters}>
              Clear Filters
            </Button>
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
