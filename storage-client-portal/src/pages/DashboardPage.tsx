import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { filesAPI, FileMetadata, formatBytes } from '../lib/api';
import { Upload, Download, Trash2, File, LogOut, HardDrive, FolderOpen, Gift } from 'lucide-react';
import NotificationBell from '../components/NotificationBell';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [storageUsed, setStorageUsed] = useState(0);
  const [storageQuota, setStorageQuota] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const data = await filesAPI.list();
      setFiles(data.files);
      setStorageUsed(data.storage_used);
      setStorageQuota(data.storage_quota);
    } catch (error: any) {
      console.error('Error loading files:', error);
      showToast(error.response?.data?.detail || 'Failed to load files', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      await filesAPI.upload(selectedFile);
      showToast(`Successfully uploaded ${selectedFile.name}`, 'success');
      setSelectedFile(null);
      await loadFiles();
      
      // Reset file input
      const fileInput = document.getElementById('fileInput') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (file: FileMetadata) => {
    try {
      await filesAPI.download(file.file_id, file.filename);
      showToast(`Downloading ${file.filename}...`, 'success');
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Download failed', 'error');
    }
  };

  const handleDelete = async (fileId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;

    try {
      await filesAPI.delete(fileId);
      showToast('File deleted successfully', 'success');
      await loadFiles();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Delete failed', 'error');
    }
  };

  const utilizationPercent = storageQuota > 0 ? (storageUsed / storageQuota) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <HardDrive className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ICTNexus Storage</h1>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <NotificationBell storageUsed={storageUsed} storageQuota={storageQuota} />
              <button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        {showWelcome && (
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 mb-6 text-white relative">
            <button
              onClick={() => setShowWelcome(false)}
              className="absolute top-4 right-4 text-white/80 hover:text-white"
            >
              ×
            </button>
            <div className="flex items-center gap-4">
              <div className="bg-white/20 p-3 rounded-full">
                <Gift className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold mb-1">Welcome to ICTNexus Storage!</h2>
                <p className="text-white/90 text-lg">
                  You are entitled to <strong>{formatBytes(storageQuota)}</strong> of free cloud storage
                </p>
                <p className="text-sm text-white/75 mt-1">
                  Upload, share, and access your files from anywhere, anytime
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Storage Quota Card */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Storage Usage</h2>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">
                {formatBytes(storageUsed)} of {formatBytes(storageQuota)} used
              </span>
              <span className="font-medium">{utilizationPercent.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  utilizationPercent > 90
                    ? 'bg-red-600'
                    : utilizationPercent > 70
                    ? 'bg-yellow-600'
                    : 'bg-blue-600'
                }`}
                style={{ width: `${Math.min(utilizationPercent, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>{files.length} files</span>
              <span>{formatBytes(storageQuota - storageUsed)} available</span>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload File
          </h2>
          <div className="flex gap-3">
            <input
              id="fileInput"
              type="file"
              onChange={handleFileSelect}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-600">
              Selected: {selectedFile.name} ({formatBytes(selectedFile.size)})
            </p>
          )}
        </div>

        {/* Files List */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="px-6 py-4 border-b bg-gray-50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <FolderOpen className="w-5 h-5" />
              My Files
            </h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading files...</div>
          ) : files.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <File className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No files uploaded yet</p>
            </div>
          ) : (
            <div className="divide-y">
              {files.map((file) => (
                <div
                  key={file.file_id}
                  className="px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <File className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 truncate">
                          {file.filename}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatBytes(file.original_size)} • Uploaded{' '}
                          {new Date(file.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownload(file)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Download"
                      >
                        <Download className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(file.file_id, file.filename)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
