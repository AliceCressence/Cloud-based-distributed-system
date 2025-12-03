import { useState, useEffect } from 'react';
import { Bell, X, AlertTriangle } from 'lucide-react';

export interface Notification {
  id: string;
  type: 'warning' | 'info' | 'success';
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationBellProps {
  storageUsed: number;
  storageQuota: number;
}

export default function NotificationBell({ storageUsed, storageQuota }: NotificationBellProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    checkStorageAlerts();
  }, [storageUsed, storageQuota]);

  useEffect(() => {
    const count = notifications.filter(n => !n.read).length;
    setUnreadCount(count);
  }, [notifications]);

  const checkStorageAlerts = () => {
    const usagePercent = (storageUsed / storageQuota) * 100;
    
    // Clear existing storage alerts
    setNotifications(prev => prev.filter(n => !n.message.includes('storage')));
    
    if (usagePercent >= 90) {
      addNotification({
        type: 'warning',
        message: `⚠️ Storage Critical: ${usagePercent.toFixed(1)}% used! Only ${formatBytes(storageQuota - storageUsed)} remaining.`
      });
    } else if (usagePercent >= 75) {
      addNotification({
        type: 'warning',
        message: `⚡ Storage Alert: ${usagePercent.toFixed(1)}% used. You have ${formatBytes(storageQuota - storageUsed)} remaining.`
      });
    } else if (usagePercent >= 50) {
      addNotification({
        type: 'info',
        message: `📊 Storage Notice: ${usagePercent.toFixed(1)}% used. ${formatBytes(storageQuota - storageUsed)} available.`
      });
    }
  };

  const addNotification = (notif: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notif,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 9)]); // Keep max 10
  };

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'warning': return 'border-l-4 border-yellow-500 bg-yellow-50';
      case 'info': return 'border-l-4 border-blue-500 bg-blue-50';
      case 'success': return 'border-l-4 border-green-500 bg-green-50';
      default: return 'border-l-4 border-gray-500 bg-gray-50';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="relative">
      {/* Bell Icon Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notifications Dropdown */}
      {showDropdown && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowDropdown(false)}
          />
          
          {/* Dropdown Content */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-2xl border z-20 max-h-[600px] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="px-4 py-3 border-b bg-gray-50 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">Notifications</h3>
                <p className="text-xs text-gray-500">
                  {unreadCount} unread
                </p>
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Mark all read
                </button>
              )}
            </div>

            {/* Notifications List */}
            <div className="overflow-y-auto flex-1">
              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500">
                  <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No notifications</p>
                  <p className="text-xs mt-1">You're all caught up!</p>
                </div>
              ) : (
                <div className="divide-y">
                  {notifications.map(notification => (
                    <div
                      key={notification.id}
                      className={`px-4 py-3 hover:bg-gray-50 transition-colors ${
                        !notification.read ? 'bg-blue-50/30' : ''
                      } ${getNotificationColor(notification.type)}`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start gap-3">
                        {notification.type === 'warning' && (
                          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 whitespace-pre-wrap">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatTimeAgo(notification.timestamp)}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                          className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      {!notification.read && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full absolute left-2 top-1/2 -translate-y-1/2" />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
