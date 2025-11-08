import { Priority } from '@/types';
import { Badge } from '../ui/badge';
import { AlertCircle, ArrowUp, Minus, Zap } from 'lucide-react';

interface PriorityBadgeProps {
  priority: Priority;
  showIcon?: boolean;
}

const priorityConfig: Record<Priority, { variant: 'default' | 'secondary' | 'destructive' | 'warning'; label: string; icon: React.ElementType }> = {
  low: { variant: 'secondary', label: 'Low', icon: Minus },
  medium: { variant: 'default', label: 'Medium', icon: AlertCircle },
  high: { variant: 'warning', label: 'High', icon: ArrowUp },
  urgent: { variant: 'destructive', label: 'Urgent', icon: Zap },
};

export function PriorityBadge({ priority, showIcon = true }: PriorityBadgeProps) {
  const config = priorityConfig[priority];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className="gap-1">
      {showIcon && <Icon className="h-3 w-3" />}
      {config.label}
    </Badge>
  );
}
