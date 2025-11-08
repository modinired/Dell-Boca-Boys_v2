import { Notification } from '@/types';
import { formatRelativeTime } from '@/utils/format';
import { Bell, CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead?: (id: string) => void;
}

const notificationConfig = {
  info: {
    icon: Info,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
  },
  success: {
    icon: CheckCircle,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
  },
  warning: {
    icon: AlertCircle,
    iconColor: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
  },
  error: {
    icon: XCircle,
    iconColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  },
};

export function NotificationItem({ notification, onMarkAsRead }: NotificationItemProps) {
  const config = notificationConfig[notification.type];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'p-4 rounded-lg border transition-all cursor-pointer',
        notification.read
          ? 'bg-white border-gray-200 opacity-70'
          : cn(config.bgColor, config.borderColor)
      )}
      onClick={() => !notification.read && onMarkAsRead?.(notification.id)}
    >
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-full', notification.read ? 'bg-gray-100' : config.bgColor)}>
          <Icon className={cn('h-4 w-4', notification.read ? 'text-gray-600' : config.iconColor)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className={cn('text-sm font-medium', notification.read && 'text-gray-600')}>
              {notification.title}
            </p>
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {formatRelativeTime(notification.createdAt)}
            </span>
          </div>
          <p className={cn('text-sm mt-1', notification.read ? 'text-gray-500' : 'text-gray-700')}>
            {notification.message}
          </p>
          {notification.actionUrl && !notification.read && (
            <a
              href={notification.actionUrl}
              className="text-xs font-medium text-blue-600 hover:underline mt-2 inline-block"
              onClick={(e) => e.stopPropagation()}
            >
              View Details →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
