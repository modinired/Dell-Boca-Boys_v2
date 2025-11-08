import { WorkflowStatus } from '@/types';
import { Badge } from '../ui/badge';

interface StatusBadgeProps {
  status: WorkflowStatus;
}

const statusConfig: Record<WorkflowStatus, { variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'; label: string }> = {
  draft: { variant: 'outline', label: 'Draft' },
  submitted: { variant: 'secondary', label: 'Submitted' },
  in_review: { variant: 'default', label: 'In Review' },
  in_progress: { variant: 'default', label: 'In Progress' },
  testing: { variant: 'warning', label: 'Testing' },
  deployed: { variant: 'success', label: 'Deployed' },
  completed: { variant: 'success', label: 'Completed' },
  on_hold: { variant: 'warning', label: 'On Hold' },
  cancelled: { variant: 'destructive', label: 'Cancelled' },
  failed: { variant: 'destructive', label: 'Failed' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
