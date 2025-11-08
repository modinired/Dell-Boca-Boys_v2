import { Bell, User, LogOut } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useAuthStore } from '@/stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore';
import { Link } from 'react-router-dom';

export function Header() {
  const { customer, logout } = useAuthStore();
  const { unreadCount } = useNotificationStore();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎩</span>
              <div>
                <h1 className="text-xl font-bold">Dell Boca Boys</h1>
                <p className="text-xs text-muted-foreground">Workflow Automation</p>
              </div>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <Link to="/notifications">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {unreadCount > 9 ? '9+' : unreadCount}
                </Badge>
              )}
            </Button>
          </Link>

          {/* User Menu */}
          <div className="flex items-center gap-3 pl-3 border-l">
            <div className="text-right">
              <p className="text-sm font-medium">{customer?.name || 'Customer'}</p>
              <p className="text-xs text-muted-foreground">{customer?.email}</p>
            </div>
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
