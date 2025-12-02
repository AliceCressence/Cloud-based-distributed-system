import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8085/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: number;
  user_id: string;
  email: string;
  role: string;
  storage_quota_bytes: number;
  storage_used_bytes: number;
  is_active: boolean;
  created_at: string;
}

export interface FileMetadata {
  id: number;
  file_id: string;
  filename: string;
  original_size: number;
  content_type: string;
  status: string;
  course_id?: string;
  folder_path: string;
  is_shared: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  files: FileMetadata[];
  total: number;
  storage_used: number;
  storage_quota: number;
}

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  register: async (userData: { user_id: string; email: string; password: string; role: string }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Files API
export const filesAPI = {
  upload: async (file: File, courseId?: string, folderPath: string = '/') => {
    const formData = new FormData();
    formData.append('file', file);
    if (courseId) formData.append('course_id', courseId);
    formData.append('folder_path', folderPath);
    
    const response = await api.post<FileMetadata>('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  list: async (courseId?: string, folderPath?: string, skip = 0, limit = 100) => {
    const params = new URLSearchParams();
    if (courseId) params.append('course_id', courseId);
    if (folderPath) params.append('folder_path', folderPath);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    const response = await api.get<FileListResponse>(`/files?${params.toString()}`);
    return response.data;
  },
  
  getInfo: async (fileId: string) => {
    const response = await api.get<FileMetadata>(`/files/${fileId}`);
    return response.data;
  },
  
  download: async (fileId: string, filename: string) => {
    const response = await api.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  
  delete: async (fileId: string) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },
};

export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};
