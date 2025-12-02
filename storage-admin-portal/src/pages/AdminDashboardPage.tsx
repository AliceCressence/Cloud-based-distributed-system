import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { api, formatBytes } from '../lib/api';
import { 
  LogOut, Server, Users, HardDrive,
  Plus, Trash2, Power, RefreshCw, Database,
  TrendingUp, CheckCircle, XCircle
} from 'lucide-react';

interface User {
  id: number;
  user_id: string;
  email: string;
  role: string;
  storage_quota_bytes: number;
  storage_used_bytes: number;
  is_active: boolean;
}

interface StorageNode {
  id: number;
  node_id: string;
  host: string;
  port: number;
  capacity_bytes: number;
  used_bytes: number;
  status: string;
  last_heartbeat: string;
}

interface SystemStats {
  users: {
    total: number;
    active: number;
    inactive: number;
  };
  nodes: {
    total: number;
    online: number;
    offline: number;
  };
  storage: {
    total_capacity_bytes: number;
    total_used_bytes: number;
    utilization_percent: number;
  };
  files: {
    total_files: number;
    total_size_bytes: number;
  };
  chunks: {
    total_chunks: number;
    avg_chunks_per_file: number;
    chunk_distribution: { [key: string]: number };
    replication_factor: string;
  };
}

export default function AdminDashboardPage() {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  
  const [users, setUsers] = useState<User[]>([]);
  const [nodes, setNodes] = useState<StorageNode[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [showCreateNode, setShowCreateNode] = useState(false);
  const [newNode, setNewNode] = useState({
    node_id: '',
    host: 'localhost',
    port: 50054,
    capacity_bytes: 5368709120 // 5GB
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [usersRes, nodesRes, statsRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/nodes/'),
        api.get('/admin/stats')
      ]);
      
      setUsers(usersRes.data);
      setNodes(nodesRes.data);
      setStats(statsRes.data);
    } catch (error: any) {
      console.error('Dashboard load error:', error);
      showToast(error.response?.data?.detail || error.message || 'Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNode = async () => {
    try {
      await api.post('/nodes/', newNode);
      showToast(`Node ${newNode.node_id} created successfully`, 'success');
      setShowCreateNode(false);
      setNewNode({ node_id: '', host: 'localhost', port: 50054, capacity_bytes: 5368709120 });
      await loadDashboardData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to create node', 'error');
    }
  };

  const handleDeleteNode = async (nodeId: string) => {
    if (!window.confirm(`Are you sure you want to delete node ${nodeId}?`)) return;
    
    try {
      await api.delete(`/nodes/${nodeId}`);
      showToast(`Node ${nodeId} deleted successfully`, 'success');
      await loadDashboardData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to delete node', 'error');
    }
  };

  const handleToggleNodeStatus = async (nodeId: string, currentStatus: string) => {
    const action = currentStatus?.toLowerCase() === 'online' ? 'stop' : 'start';
    try {
      // In a real implementation, you'd have endpoints for this
      showToast(`Node ${nodeId} ${action} requested`, 'info');
      // await api.post(`/nodes/${nodeId}/${action}`);
      // await loadDashboardData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || `Failed to ${action} node`, 'error');
    }
  };

  const getStatusColor = (status: string) => {
    const statusLower = status?.toLowerCase();
    switch (statusLower) {
      case 'online': return 'text-green-600 bg-green-50';
      case 'offline': return 'text-red-600 bg-red-50';
      case 'degraded': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    return status?.toLowerCase() === 'online' ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-purple-600 p-2 rounded-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Users</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.users.total}</p>
                    <p className="text-xs text-green-600">{stats.users.active} active</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <Server className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Storage Nodes</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.nodes.total}</p>
                    <p className="text-xs text-green-600">{stats.nodes.online} online</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <HardDrive className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Storage Used</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatBytes(stats.storage.total_used_bytes)}
                    </p>
                    <p className="text-xs text-gray-600">
                      of {formatBytes(stats.storage.total_capacity_bytes)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-orange-100 p-3 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Capacity</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.storage.utilization_percent.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-600">utilization</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Chunk Distribution Statistics - NEW */}
            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg shadow-lg p-6 mb-8 text-white">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Database className="w-6 h-6" />
                File Chunking & Distribution (Fault Tolerance)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                  <p className="text-sm text-white/80 mb-1">Total Files</p>
                  <p className="text-3xl font-bold">{stats.files.total_files}</p>
                </div>
                <div>
                  <p className="text-sm text-white/80 mb-1">Total Chunks</p>
                  <p className="text-3xl font-bold">{stats.chunks.total_chunks}</p>
                  <p className="text-xs text-white/70 mt-1">Distributed across nodes</p>
                </div>
                <div>
                  <p className="text-sm text-white/80 mb-1">Avg Chunks/File</p>
                  <p className="text-3xl font-bold">{stats.chunks.avg_chunks_per_file}</p>
                  <p className="text-xs text-white/70 mt-1">2MB per chunk</p>
                </div>
                <div>
                  <p className="text-sm text-white/80 mb-1">Distribution</p>
                  <div className="space-y-1 mt-2">
                    {Object.entries(stats.chunks.chunk_distribution).map(([nodeId, count]) => (
                      <div key={nodeId} className="text-sm">
                        <span className="font-medium">{nodeId}:</span> {count} chunks
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-white/20">
                <p className="text-sm text-white/90">
                  ✓ {stats.chunks.replication_factor}
                </p>
              </div>
            </div>
          </>
        )}

        {/* Storage Nodes Section */}
        <div className="bg-white rounded-lg shadow-sm border mb-8">
          <div className="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Server className="w-5 h-5" />
              Storage Nodes
            </h2>
            <button
              onClick={() => setShowCreateNode(!showCreateNode)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Node
            </button>
          </div>

          {/* Create Node Form */}
          {showCreateNode && (
            <div className="p-6 border-b bg-blue-50">
              <h3 className="font-semibold mb-4">Create New Storage Node</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Node ID
                  </label>
                  <input
                    type="text"
                    value={newNode.node_id}
                    onChange={(e) => setNewNode({ ...newNode, node_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., node4"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Host
                  </label>
                  <input
                    type="text"
                    value={newNode.host}
                    onChange={(e) => setNewNode({ ...newNode, host: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port
                  </label>
                  <input
                    type="number"
                    value={newNode.port}
                    onChange={(e) => setNewNode({ ...newNode, port: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Capacity (GB)
                  </label>
                  <input
                    type="number"
                    value={newNode.capacity_bytes / (1024 ** 3)}
                    onChange={(e) => setNewNode({ ...newNode, capacity_bytes: parseInt(e.target.value) * (1024 ** 3) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleCreateNode}
                  disabled={!newNode.node_id}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  Create Node
                </button>
                <button
                  onClick={() => setShowCreateNode(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Nodes List */}
          <div className="divide-y">
            {nodes.map((node) => (
              <div key={node.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`p-2 rounded-lg ${getStatusColor(node.status)}`}>
                      {getStatusIcon(node.status)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-900">{node.node_id}</p>
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(node.status)}`}>
                          {node.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {node.host}:{node.port}
                      </p>
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>{formatBytes(node.used_bytes)} used</span>
                          <span>{formatBytes(node.capacity_bytes)} total</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(node.used_bytes / node.capacity_bytes) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleNodeStatus(node.node_id, node.status)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title={node.status === 'online' ? 'Stop' : 'Start'}
                    >
                      <Power className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => loadDashboardData()}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Refresh"
                    >
                      <RefreshCw className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteNode(node.node_id)}
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
        </div>

        {/* Users Section */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b bg-gray-50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Users className="w-5 h-5" />
              Users ({users.length})
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Storage Used</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quota</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{user.email}</p>
                        <p className="text-sm text-gray-500">{user.user_id}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatBytes(user.storage_used_bytes)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatBytes(user.storage_quota_bytes)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
