import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import {
  LayoutDashboard,
  FileText,
  Workflow,
  Library,
  BarChart3,
  Settings,
  HelpCircle,
} from 'lucide-react';

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    title: 'My Requests',
    href: '/requests',
    icon: FileText,
  },
  {
    title: 'My Workflows',
    href: '/workflows',
    icon: Workflow,
  },
  {
    title: 'Template Library',
    href: '/templates',
    icon: Library,
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
  {
    title: 'Help & Support',
    href: '/support',
    icon: HelpCircle,
  },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-16 z-30 h-[calc(100vh-4rem)] w-64 border-r bg-white">
      <nav className="flex flex-col gap-1 p-4">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;

          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <Icon className="h-4 w-4" />
              {item.title}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
