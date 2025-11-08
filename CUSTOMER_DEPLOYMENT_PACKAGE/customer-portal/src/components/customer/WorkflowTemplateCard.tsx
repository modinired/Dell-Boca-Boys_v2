import { WorkflowTemplate } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { formatNumber } from '@/utils/format';
import { Download, Star, TrendingUp, Clock } from 'lucide-react';

interface WorkflowTemplateCardProps {
  template: WorkflowTemplate;
  onUseTemplate?: (id: string) => void;
}

export function WorkflowTemplateCard({ template, onUseTemplate }: WorkflowTemplateCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow h-full flex flex-col">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{template.name}</CardTitle>
            <CardDescription className="mt-1">{template.description}</CardDescription>
          </div>
          <Badge variant="secondary">{template.category}</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="flex flex-wrap gap-2 mb-4">
          {template.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10"
            >
              {tag}
            </span>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Star className="h-4 w-4 text-yellow-500" />
            <div>
              <div className="font-semibold">{template.rating.toFixed(1)}</div>
              <div className="text-xs text-muted-foreground">
                {formatNumber(template.reviewCount)} reviews
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Download className="h-4 w-4 text-blue-500" />
            <div>
              <div className="font-semibold">{formatNumber(template.usageCount)}</div>
              <div className="text-xs text-muted-foreground">deployments</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-purple-500" />
            <div>
              <div className="font-semibold">{template.estimatedSetupTime}</div>
              <div className="text-xs text-muted-foreground">setup time</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <div>
              <div className="font-semibold">{template.complexity}</div>
              <div className="text-xs text-muted-foreground">complexity</div>
            </div>
          </div>
        </div>
        {template.integrations && template.integrations.length > 0 && (
          <div className="mt-4">
            <div className="text-xs text-muted-foreground mb-2">Integrations:</div>
            <div className="flex flex-wrap gap-2">
              {template.integrations.slice(0, 4).map((integration) => (
                <Badge key={integration} variant="outline" className="text-xs">
                  {integration}
                </Badge>
              ))}
              {template.integrations.length > 4 && (
                <Badge variant="outline" className="text-xs">
                  +{template.integrations.length - 4} more
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button
          className="w-full"
          onClick={() => onUseTemplate?.(template.id)}
        >
          Use This Template
        </Button>
      </CardFooter>
    </Card>
  );
}
