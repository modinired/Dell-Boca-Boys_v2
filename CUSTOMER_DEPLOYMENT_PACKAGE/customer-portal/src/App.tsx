import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Requests } from './pages/Requests';
import { NewRequest } from './pages/NewRequest';
import { Workflows } from './pages/Workflows';
import { Templates } from './pages/Templates';
import { Analytics } from './pages/Analytics';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { useAuthStore } from './stores/authStore';
import { useNotificationStore } from './stores/notificationStore';
import { useEffect } from 'react';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route component (redirect to dashboard if already authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function AppContent() {
  const { isAuthenticated } = useAuthStore();
  const { fetchNotifications } = useNotificationStore();

  // Fetch notifications when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();

      // Poll for new notifications every 30 seconds
      const interval = setInterval(() => {
        fetchNotifications();
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [isAuthenticated, fetchNotifications]);

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="requests" element={<Requests />} />
        <Route path="requests/new" element={<NewRequest />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="templates" element={<Templates />} />
        <Route path="analytics" element={<Analytics />} />

        {/* Placeholder routes - can be implemented later */}
        <Route path="notifications" element={<div className="p-8">Notifications page coming soon...</div>} />
        <Route path="settings" element={<div className="p-8">Settings page coming soon...</div>} />
        <Route path="support" element={<div className="p-8">Support page coming soon...</div>} />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
