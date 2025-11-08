import { WorkflowRequest } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { StatusBadge } from './StatusBadge';
import { PriorityBadge } from './PriorityBadge';
import { Button } from '../ui/button';
import { formatRelativeTime } from '@/utils/format';
import { MessageCircle, Paperclip, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';

interface WorkflowRequestCardProps {
  request: WorkflowRequest;
}

export function WorkflowRequestCard({ request }: WorkflowRequestCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{request.title}</CardTitle>
            <CardDescription className="mt-1">{request.description}</CardDescription>
          </div>
          <div className="ml-4 flex flex-col gap-2">
            <StatusBadge status={request.status} />
            <PriorityBadge priority={request.priority} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-4">
          {request.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10"
            >
              {tag}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <MessageCircle className="h-4 w-4" />
            <span>{request.comments.length} comments</span>
          </div>
          <div className="flex items-center gap-1">
            <Paperclip className="h-4 w-4" />
            <span>{request.attachments.length} attachments</span>
          </div>
          <div className="ml-auto">Created {formatRelativeTime(request.createdAt)}</div>
        </div>
      </CardContent>
      <CardFooter>
        <Link to={`/requests/${request.id}`} className="w-full">
          <Button variant="outline" className="w-full">
            <Eye className="mr-2 h-4 w-4" />
            View Details
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
