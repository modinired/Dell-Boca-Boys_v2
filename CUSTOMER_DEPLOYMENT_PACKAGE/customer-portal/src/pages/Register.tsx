import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

interface RegisterForm {
  companyName: string;
  contactName: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone?: string;
  industry?: string;
}

export function Register() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterForm>();

  const password = watch('password');

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      // TODO: Implement actual registration API call
      await new Promise((resolve) => setTimeout(resolve, 1500));
      toast.success('Account created successfully! Please check your email for verification.');
      navigate('/login');
    } catch (err) {
      toast.error('Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="flex items-center gap-2">
              <span className="text-4xl">🎩</span>
              <div className="text-left">
                <h1 className="text-2xl font-bold">Dell Boca Boys</h1>
                <p className="text-sm text-muted-foreground">Workflow Automation</p>
              </div>
            </div>
          </div>
          <CardTitle className="text-2xl">Create Your Account</CardTitle>
          <CardDescription>
            Get started with workflow automation for your business
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Company Name */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Company Name <span className="text-red-600">*</span>
              </label>
              <Input
                {...register('companyName', { required: 'Company name is required' })}
                placeholder="Acme Corporation"
              />
              {errors.companyName && (
                <p className="text-sm text-red-600 mt-1">{errors.companyName.message}</p>
              )}
            </div>

            {/* Contact Name */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Your Name <span className="text-red-600">*</span>
              </label>
              <Input
                {...register('contactName', { required: 'Name is required' })}
                placeholder="John Smith"
              />
              {errors.contactName && (
                <p className="text-sm text-red-600 mt-1">{errors.contactName.message}</p>
              )}
            </div>

            {/* Email and Phone */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Email <span className="text-red-600">*</span>
                </label>
                <Input
                  type="email"
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  placeholder="john@acme.com"
                />
                {errors.email && (
                  <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Phone (Optional)</label>
                <Input {...register('phone')} placeholder="+1 (555) 123-4567" />
              </div>
            </div>

            {/* Industry */}
            <div>
              <label className="text-sm font-medium mb-2 block">Industry (Optional)</label>
              <select
                {...register('industry')}
                className="w-full border rounded-md px-3 py-2 bg-white"
              >
                <option value="">Select your industry</option>
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="retail">Retail</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="education">Education</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Password */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Password <span className="text-red-600">*</span>
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-blue-600 hover:underline"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              {errors.password && (
                <p className="text-sm text-red-600 mt-1">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Confirm Password <span className="text-red-600">*</span>
              </label>
              <Input
                type={showPassword ? 'text' : 'password'}
                {...register('confirmPassword', {
                  required: 'Please confirm your password',
                  validate: (value) => value === password || 'Passwords do not match',
                })}
                placeholder="••••••••"
              />
              {errors.confirmPassword && (
                <p className="text-sm text-red-600 mt-1">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Terms & Conditions */}
            <div className="flex items-start gap-2">
              <input type="checkbox" required className="mt-1" />
              <p className="text-sm text-muted-foreground">
                I agree to the{' '}
                <a href="#" className="text-blue-600 hover:underline">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="#" className="text-blue-600 hover:underline">
                  Privacy Policy
                </a>
              </p>
            </div>

            {/* Submit Button */}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Create Account'}
            </Button>

            {/* Sign In Link */}
            <div className="text-center text-sm mt-4">
              <span className="text-muted-foreground">Already have an account? </span>
              <Link to="/login" className="text-blue-600 hover:underline font-medium">
                Sign in
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
