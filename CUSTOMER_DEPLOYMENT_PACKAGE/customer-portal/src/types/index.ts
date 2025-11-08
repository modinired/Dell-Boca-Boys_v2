/**
 * Dell Boca Boys Customer Portal - TypeScript Type Definitions
 * PhD-level type safety for customer workflow automation
 */

export interface Customer {
  id: string;
  email: string;
  companyName: string;
  firstName: string;
  lastName: string;
  role: 'customer' | 'admin';
  createdAt: string;
  lastLogin?: string;
  avatarUrl?: string;
}

export interface WorkflowRequest {
  id: string;
  customerId: string;
  title: string;
  description: string;
  category: WorkflowCategory;
  priority: Priority;
  status: WorkflowStatus;
  createdAt: string;
  updatedAt: string;
  estimatedCompletionDate?: string;
  actualCompletionDate?: string;
  assignedAgents: string[];
  tags: string[];
  attachments: Attachment[];
  comments: Comment[];
}

export type WorkflowCategory =
  | 'data_integration'
  | 'automation'
  | 'reporting'
  | 'notification'
  | 'api_integration'
  | 'data_transformation'
  | 'scheduled_task'
  | 'event_driven'
  | 'custom';

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export type WorkflowStatus =
  | 'draft'
  | 'submitted'
  | 'in_review'
  | 'in_progress'
  | 'testing'
  | 'deployed'
  | 'completed'
  | 'on_hold'
  | 'cancelled'
  | 'failed';

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  mimeType: string;
  url: string;
  uploadedAt: string;
}

export interface Comment {
  id: string;
  authorId: string;
  authorName: string;
  authorRole: 'customer' | 'agent' | 'admin';
  content: string;
  createdAt: string;
  isInternal: boolean;
}

export interface CompletedWorkflow {
  id: string;
  requestId: string;
  customerId: string;
  name: string;
  description: string;
  n8nWorkflowId?: string;
  jsonDefinition: Record<string, any>;
  deployedAt: string;
  lastExecuted?: string;
  executionCount: number;
  successRate: number;
  averageExecutionTime: number;
  isActive: boolean;
  endpoints: WorkflowEndpoint[];
  schedule?: WorkflowSchedule;
}

export interface WorkflowEndpoint {
  type: 'webhook' | 'api' | 'manual';
  url?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  authentication?: 'none' | 'api_key' | 'oauth' | 'basic';
}

export interface WorkflowSchedule {
  enabled: boolean;
  type: 'cron' | 'interval';
  expression: string;
  timezone: string;
  nextRun?: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: WorkflowCategory;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  usageCount: number;
  rating: number;
  tags: string[];
  previewImage?: string;
  requiredFields: TemplateField[];
}

export interface TemplateField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'url' | 'select' | 'textarea';
  required: boolean;
  placeholder?: string;
  options?: string[];
  validation?: Record<string, any>;
}

export interface CustomerAnalytics {
  totalRequests: number;
  completedWorkflows: number;
  activeWorkflows: number;
  pendingRequests: number;
  averageCompletionTime: number;
  successRate: number;
  requestsByCategory: Record<WorkflowCategory, number>;
  requestsByMonth: MonthlyStats[];
  topWorkflows: WorkflowUsage[];
}

export interface MonthlyStats {
  month: string;
  requests: number;
  completed: number;
  successRate: number;
}

export interface WorkflowUsage {
  workflowId: string;
  workflowName: string;
  executionCount: number;
  successRate: number;
  avgExecutionTime: number;
}

export interface ExecutionLog {
  id: string;
  workflowId: string;
  workflowName: string;
  startedAt: string;
  completedAt?: string;
  status: 'running' | 'success' | 'failed' | 'cancelled';
  duration?: number;
  errorMessage?: string;
  inputData?: Record<string, any>;
  outputData?: Record<string, any>;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
  actionUrl?: string;
  actionLabel?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface WorkflowRequestForm {
  title: string;
  description: string;
  category: WorkflowCategory;
  priority: Priority;
  tags: string[];
  desiredCompletionDate?: string;
  additionalRequirements?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  firstName: string;
  lastName: string;
  companyName: string;
}
