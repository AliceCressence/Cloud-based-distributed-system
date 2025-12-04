import { X, HardDrive, Activity, Clock, Database, Zap, CheckCircle, AlertCircle } from 'lucide-react';

interface Chunk {
  chunk_id: string;
  file_name: string;
  chunk_index: number;
  size: number;
  created_at: string;
}

interface NodeDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  node: {
    id: number;
    node_id: string;
    host: string;
    port: number;
    status: string;
    capacity_bytes: number;
    used_bytes: number;
    last_heartbeat: string;
  } | null;
}

export default function NodeDetailsModal({ isOpen, onClose, node }: NodeDetailsModalProps) {
  if (!isOpen || !node) return null;

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const usagePercent = node.capacity_bytes > 0 
    ? Math.round((node.used_bytes / node.capacity_bytes) * 100) 
    : 0;

  const freeBytes = node.capacity_bytes - node.used_bytes;

  // Simulated data (in real app, fetch from API)
  const performanceMetrics = {
    uptime: '6 hours 23 minutes',
    filesStored: 47,
    chunksStored: 142,
    readRequests: 1234,
    writeRequests: 567,
    avgResponseTime: 45
  };

  const recentChunks: Chunk[] = [
    {
      chunk_id: 'chunk_001_0',
      file_name: 'document.pdf',
      chunk_index: 0,
      size: 2097152,
      created_at: new Date().toISOString()
    },
    {
      chunk_id: 'chunk_002_1',
      file_name: 'image.jpg',
      chunk_index: 1,
      size: 1048576,
      created_at: new Date(Date.now() - 3600000).toISOString()
    },
    {
      chunk_id: 'chunk_003_0',
      file_name: 'video.mp4',
      chunk_index: 0,
      size: 3145728,
      created_at: new Date(Date.now() - 7200000).toISOString()
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'online': return 'text-green-600 bg-green-100';
      case 'offline': return 'text-red-600 bg-red-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'online': return <CheckCircle className="w-5 h-5" />;
      case 'offline': return <AlertCircle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full my-8">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <HardDrive className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Storage Node {node.id}
                </h3>
                <p className="text-sm text-gray-600">
                  {node.host}:{node.port}
                </p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center space-x-2 ${getStatusColor(node.status)}`}>
                {getStatusIcon(node.status)}
                <span>{node.status.toUpperCase()}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Storage Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Database className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-gray-900">Capacity</h4>
                </div>
                <p className="text-2xl font-bold text-blue-600">{formatBytes(node.capacity_bytes)}</p>
                <p className="text-sm text-gray-600 mt-1">Total storage</p>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Activity className="w-5 h-5 text-purple-600" />
                  <h4 className="font-semibold text-gray-900">Used</h4>
                </div>
                <p className="text-2xl font-bold text-purple-600">{formatBytes(node.used_bytes)}</p>
                <p className="text-sm text-gray-600 mt-1">{usagePercent}% utilized</p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Zap className="w-5 h-5 text-green-600" />
                  <h4 className="font-semibold text-gray-900">Available</h4>
                </div>
                <p className="text-2xl font-bold text-green-600">{formatBytes(freeBytes)}</p>
                <p className="text-sm text-gray-600 mt-1">Free space</p>
              </div>
            </div>

            {/* Storage Usage Bar */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium text-gray-700">Storage Usage</span>
                <span className="text-gray-600">{usagePercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full transition-all ${
                    usagePercent > 90 ? 'bg-red-500' :
                    usagePercent > 70 ? 'bg-yellow-500' :
                    'bg-blue-500'
                  }`}
                  style={{ width: `${usagePercent}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>{formatBytes(node.used_bytes)} used</span>
                <span>{formatBytes(freeBytes)} free</span>
              </div>
            </div>

            {/* Performance Metrics */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Activity className="w-5 h-5" />
                <span>Performance Metrics</span>
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Uptime</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.uptime}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Files Stored</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.filesStored}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Chunks Stored</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.chunksStored}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Read Requests</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.readRequests.toLocaleString()}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Write Requests</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.writeRequests.toLocaleString()}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Avg Response</p>
                  <p className="text-lg font-bold text-gray-900">{performanceMetrics.avgResponseTime}ms</p>
                </div>
              </div>
            </div>

            {/* Recent Chunks */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Database className="w-5 h-5" />
                <span>Recent Chunks</span>
              </h4>
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunk ID</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Index</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recentChunks.map((chunk) => (
                      <tr key={chunk.chunk_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-mono text-gray-900">{chunk.chunk_id}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{chunk.file_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{chunk.chunk_index}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{formatBytes(chunk.size)}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {new Date(chunk.created_at).toLocaleTimeString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Last Heartbeat */}
            {node.last_heartbeat && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
                <Clock className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Last Heartbeat</p>
                  <p className="text-sm text-gray-600">
                    {new Date(node.last_heartbeat).toLocaleString()}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
