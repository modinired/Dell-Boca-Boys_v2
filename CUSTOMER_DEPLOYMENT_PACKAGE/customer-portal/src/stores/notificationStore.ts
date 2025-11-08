import { create } from 'zustand';
import { Notification } from '@/types';
import { apiService } from '@/services/api';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,

  fetchNotifications: async () => {
    set({ isLoading: true });
    try {
      const notifications = await apiService.getNotifications({ unreadOnly: false });
      const unreadCount = notifications.filter((n) => !n.read).length;
      set({ notifications, unreadCount, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      set({ isLoading: false });
    }
  },

  markAsRead: async (id: string) => {
    try {
      await apiService.markNotificationAsRead(id);
      const { notifications } = get();
      const updatedNotifications = notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      );
      const unreadCount = updatedNotifications.filter((n) => !n.read).length;
      set({ notifications: updatedNotifications, unreadCount });
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  },

  markAllAsRead: async () => {
    try {
      await apiService.markAllNotificationsAsRead();
      const { notifications } = get();
      const updatedNotifications = notifications.map((n) => ({ ...n, read: true }));
      set({ notifications: updatedNotifications, unreadCount: 0 });
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  },
}));
