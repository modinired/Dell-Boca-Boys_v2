import { CompletedWorkflow } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { formatDate, formatNumber, formatPercentage } from '@/utils/format';
import { Play, Pause, BarChart3, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

interface WorkflowCardProps {
  workflow: CompletedWorkflow;
  onToggleStatus?: (id: string, isActive: boolean) => void;
  onExecute?: (id: string) => void;
}

export function WorkflowCard({ workflow, onToggleStatus, onExecute }: WorkflowCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{workflow.name}</CardTitle>
            <CardDescription className="mt-1">{workflow.description}</CardDescription>
          </div>
          <Badge variant={workflow.isActive ? 'success' : 'secondary'}>
            {workflow.isActive ? 'Active' : 'Inactive'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Executions</div>
            <div className="font-semibold">{formatNumber(workflow.executionCount)}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Success Rate</div>
            <div className="font-semibold text-green-600">
              {formatPercentage(workflow.successRate)}
            </div>
          </div>
          <div>
            <div className="text-muted-foreground">Deployed</div>
            <div className="font-semibold">{formatDate(workflow.deployedAt)}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Avg Duration</div>
            <div className="font-semibold">{workflow.averageExecutionTime}ms</div>
          </div>
        </div>
        {workflow.schedule && workflow.schedule.enabled && (
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Next run: {workflow.schedule.nextRun ? formatDate(workflow.schedule.nextRun) : 'N/A'}</span>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onToggleStatus?.(workflow.id, !workflow.isActive)}
        >
          {workflow.isActive ? (
            <>
              <Pause className="mr-2 h-4 w-4" />
              Pause
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Activate
            </>
          )}
        </Button>
        <Button variant="outline" size="sm" onClick={() => onExecute?.(workflow.id)}>
          <Play className="mr-2 h-4 w-4" />
          Execute
        </Button>
        <Link to={`/workflows/${workflow.id}`} className="ml-auto">
          <Button variant="outline" size="sm">
            <BarChart3 className="mr-2 h-4 w-4" />
            View Details
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
