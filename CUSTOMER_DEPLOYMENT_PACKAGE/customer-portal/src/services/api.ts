/**
 * Dell Boca Boys Customer Portal API Service
 * Comprehensive API client with type safety and error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Customer,
  WorkflowRequest,
  CompletedWorkflow,
  WorkflowTemplate,
  CustomerAnalytics,
  ExecutionLog,
  Notification,
  ApiResponse,
  PaginatedResponse,
  WorkflowRequestForm,
  AuthTokens,
  LoginCredentials,
  RegisterData,
} from '../types';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    this.client = axios.create({
      baseURL: `${this.baseURL}/api/customer`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth tokens
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, attempt refresh
          const refreshToken = localStorage.getItem('refreshToken');
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${this.baseURL}/api/auth/refresh`, {
                refreshToken,
              });
              localStorage.setItem('accessToken', data.accessToken);

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${data.accessToken}`;
                return axios(error.config);
              }
            } catch {
              // Refresh failed, logout
              this.logout();
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthTokens & { customer: Customer }>> {
    const { data } = await this.client.post('/auth/login', credentials);
    if (data.success && data.data) {
      localStorage.setItem('accessToken', data.data.accessToken);
      localStorage.setItem('refreshToken', data.data.refreshToken);
    }
    return data;
  }

  async register(registerData: RegisterData): Promise<ApiResponse<Customer>> {
    const { data } = await this.client.post('/auth/register', registerData);
    return data;
  }

  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  async getCurrentCustomer(): Promise<ApiResponse<Customer>> {
    const { data } = await this.client.get('/me');
    return data;
  }

  async updateProfile(updates: Partial<Customer>): Promise<ApiResponse<Customer>> {
    const { data } = await this.client.patch('/me', updates);
    return data;
  }

  // Workflow Requests
  async getWorkflowRequests(params?: {
    status?: string;
    page?: number;
    pageSize?: number;
  }): Promise<ApiResponse<PaginatedResponse<WorkflowRequest>>> {
    const { data } = await this.client.get('/requests', { params });
    return data;
  }

  async getWorkflowRequest(id: string): Promise<ApiResponse<WorkflowRequest>> {
    const { data } = await this.client.get(`/requests/${id}`);
    return data;
  }

  async createWorkflowRequest(request: WorkflowRequestForm): Promise<ApiResponse<WorkflowRequest>> {
    const { data} = await this.client.post('/requests', request);
    return data;
  }

  async updateWorkflowRequest(
    id: string,
    updates: Partial<WorkflowRequestForm>
  ): Promise<ApiResponse<WorkflowRequest>> {
    const { data } = await this.client.patch(`/requests/${id}`, updates);
    return data;
  }

  async cancelWorkflowRequest(id: string): Promise<ApiResponse<void>> {
    const { data } = await this.client.post(`/requests/${id}/cancel`);
    return data;
  }

  async addComment(requestId: string, content: string): Promise<ApiResponse<void>> {
    const { data } = await this.client.post(`/requests/${requestId}/comments`, { content });
    return data;
  }

  async uploadAttachment(requestId: string, file: File): Promise<ApiResponse<{ attachmentId: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await this.client.post(`/requests/${requestId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  }

  // Completed Workflows
  async getCompletedWorkflows(params?: {
    page?: number;
    pageSize?: number;
  }): Promise<ApiResponse<PaginatedResponse<CompletedWorkflow>>> {
    const { data } = await this.client.get('/workflows', { params });
    return data;
  }

  async getCompletedWorkflow(id: string): Promise<ApiResponse<CompletedWorkflow>> {
    const { data } = await this.client.get(`/workflows/${id}`);
    return data;
  }

  async toggleWorkflowStatus(id: string, isActive: boolean): Promise<ApiResponse<void>> {
    const { data } = await this.client.patch(`/workflows/${id}/status`, { isActive });
    return data;
  }

  async executeWorkflow(id: string, inputData?: Record<string, any>): Promise<ApiResponse<{ executionId: string }>> {
    const { data } = await this.client.post(`/workflows/${id}/execute`, { inputData });
    return data;
  }

  async getWorkflowExecutions(
    workflowId: string,
    params?: { page?: number; pageSize?: number }
  ): Promise<ApiResponse<PaginatedResponse<ExecutionLog>>> {
    const { data } = await this.client.get(`/workflows/${workflowId}/executions`, { params });
    return data;
  }

  // Workflow Templates
  async getWorkflowTemplates(params?: {
    category?: string;
    difficulty?: string;
    page?: number;
    pageSize?: number;
  }): Promise<ApiResponse<PaginatedResponse<WorkflowTemplate>>> {
    const { data } = await this.client.get('/templates', { params });
    return data;
  }

  async getWorkflowTemplate(id: string): Promise<ApiResponse<WorkflowTemplate>> {
    const { data } = await this.client.get(`/templates/${id}`);
    return data;
  }

  async createRequestFromTemplate(
    templateId: string,
    values: Record<string, any>
  ): Promise<ApiResponse<WorkflowRequest>> {
    const { data } = await this.client.post(`/templates/${templateId}/create-request`, { values });
    return data;
  }

  // Analytics
  async getAnalytics(): Promise<ApiResponse<CustomerAnalytics>> {
    const { data } = await this.client.get('/analytics');
    return data;
  }

  // Notifications
  async getNotifications(params?: {
    unreadOnly?: boolean;
    page?: number;
    pageSize?: number;
  }): Promise<ApiResponse<PaginatedResponse<Notification>>> {
    const { data } = await this.client.get('/notifications', { params });
    return data;
  }

  async markNotificationAsRead(id: string): Promise<ApiResponse<void>> {
    const { data } = await this.client.patch(`/notifications/${id}/read`);
    return data;
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse<void>> {
    const { data } = await this.client.post('/notifications/read-all');
    return data;
  }
}

export const apiService = new ApiService();
export default apiService;
