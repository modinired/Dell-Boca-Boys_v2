import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { WorkflowRequestForm, WorkflowCategory, Priority } from '@/types';
import { ArrowLeft, Upload, X } from 'lucide-react';
import { toast } from 'sonner';

const categoryOptions: WorkflowCategory[] = [
  'data_processing',
  'integration',
  'automation',
  'reporting',
  'notification',
  'custom',
];

const priorityOptions: Priority[] = ['low', 'medium', 'high', 'urgent'];

export function NewRequest() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const templateId = searchParams.get('templateId');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<WorkflowRequestForm>();

  // Load template data if templateId is provided
  const { data: template } = useQuery({
    queryKey: ['template', templateId],
    queryFn: () => (templateId ? apiService.getWorkflowTemplates({ limit: 1, offset: 0 }) : null),
    enabled: !!templateId,
  });

  // Pre-fill form with template data
  if (template && template.data.length > 0) {
    const templateData = template.data[0];
    setValue('title', `Based on: ${templateData.name}`);
    setValue('description', templateData.description);
    setValue('category', templateData.category);
    if (templateData.tags) {
      setSelectedTags(templateData.tags);
    }
  }

  const createRequestMutation = useMutation({
    mutationFn: async (data: WorkflowRequestForm) => {
      // First create the request
      const request = await apiService.createWorkflowRequest({
        ...data,
        tags: selectedTags,
      });

      // Then upload attachments if any
      if (attachments.length > 0) {
        await Promise.all(
          attachments.map((file) => apiService.uploadAttachment(request.id, file))
        );
      }

      return request;
    },
    onSuccess: (data) => {
      toast.success('Workflow request created successfully!');
      navigate(`/requests/${data.id}`);
    },
    onError: () => {
      toast.error('Failed to create workflow request');
    },
  });

  const onSubmit = (data: WorkflowRequestForm) => {
    createRequestMutation.mutate(data);
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !selectedTags.includes(tagInput.trim())) {
      setSelectedTags([...selectedTags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== tag));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments([...attachments, ...Array.from(e.target.files)]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  return (
    <div className="max-w-3xl space-y-6">
      {/* Back Button */}
      <Button variant="ghost" onClick={() => navigate('/requests')}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Requests
      </Button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create Workflow Request</h1>
        <p className="text-muted-foreground mt-2">
          Describe the workflow automation you need and our team will build it for you
        </p>
      </div>

      {/* Template Info */}
      {template && template.data.length > 0 && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              Using Template: {template.data[0].name}
            </CardTitle>
            <CardDescription>
              This form has been pre-filled based on the selected template. Feel free to modify as needed.
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Request Details</CardTitle>
            <CardDescription>Provide information about your workflow needs</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Title */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Title <span className="text-red-600">*</span>
              </label>
              <Input
                {...register('title', { required: 'Title is required' })}
                placeholder="e.g., Automated Invoice Processing"
              />
              {errors.title && (
                <p className="text-sm text-red-600 mt-1">{errors.title.message}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Description <span className="text-red-600">*</span>
              </label>
              <Textarea
                {...register('description', { required: 'Description is required' })}
                placeholder="Describe what you want this workflow to do, what data it should process, and what the expected outcome is..."
                rows={6}
              />
              {errors.description && (
                <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
              )}
            </div>

            {/* Category and Priority */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Category <span className="text-red-600">*</span>
                </label>
                <select
                  {...register('category', { required: 'Category is required' })}
                  className="w-full border rounded-md px-3 py-2 bg-white"
                >
                  <option value="">Select a category</option>
                  {categoryOptions.map((category) => (
                    <option key={category} value={category}>
                      {category.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="text-sm text-red-600 mt-1">{errors.category.message}</p>
                )}
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Priority <span className="text-red-600">*</span>
                </label>
                <select
                  {...register('priority', { required: 'Priority is required' })}
                  className="w-full border rounded-md px-3 py-2 bg-white"
                >
                  <option value="">Select priority</option>
                  {priorityOptions.map((priority) => (
                    <option key={priority} value={priority}>
                      {priority.toUpperCase()}
                    </option>
                  ))}
                </select>
                {errors.priority && (
                  <p className="text-sm text-red-600 mt-1">{errors.priority.message}</p>
                )}
              </div>
            </div>

            {/* Business Value */}
            <div>
              <label className="text-sm font-medium mb-2 block">Business Value</label>
              <Textarea
                {...register('businessValue')}
                placeholder="Explain how this workflow will benefit your business (e.g., time saved, cost reduction, error prevention)..."
                rows={3}
              />
            </div>

            {/* Technical Requirements */}
            <div>
              <label className="text-sm font-medium mb-2 block">Technical Requirements</label>
              <Textarea
                {...register('technicalRequirements')}
                placeholder="List any specific technical requirements, integrations needed, data formats, APIs, etc..."
                rows={4}
              />
            </div>

            {/* Tags */}
            <div>
              <label className="text-sm font-medium mb-2 block">Tags</label>
              <div className="flex gap-2 mb-2">
                <Input
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  placeholder="Add tags (press Enter)"
                />
                <Button type="button" onClick={handleAddTag}>
                  Add
                </Button>
              </div>
              {selectedTags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {selectedTags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="gap-1">
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 hover:text-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* File Attachments */}
            <div>
              <label className="text-sm font-medium mb-2 block">Attachments</label>
              <div className="border-2 border-dashed rounded-lg p-6 text-center">
                <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-2">
                  Upload relevant files (screenshots, documents, data samples)
                </p>
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button type="button" variant="outline" asChild>
                    <span>Choose Files</span>
                  </Button>
                </label>
              </div>
              {attachments.length > 0 && (
                <div className="mt-4 space-y-2">
                  {attachments.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 border rounded"
                    >
                      <span className="text-sm">{file.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveFile(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="flex gap-4">
          <Button
            type="submit"
            className="flex-1"
            disabled={createRequestMutation.isPending}
          >
            {createRequestMutation.isPending ? 'Creating...' : 'Submit Request'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/requests')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
