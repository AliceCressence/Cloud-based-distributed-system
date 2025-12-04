import { Server, HardDrive, Database, Activity, Zap, AlertTriangle } from 'lucide-react';

interface Node {
  id: number;
  node_id: string;
  host: string;
  port: number;
  status: string;
  capacity_bytes: number;
  used_bytes: number;
  last_heartbeat: string;
}

interface SystemTopologyProps {
  nodes: Node[];
  onNodeClick?: (node: Node) => void;
}

export default function SystemTopology({ nodes, onNodeClick }: SystemTopologyProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'online': return { bg: 'bg-green-500', border: 'border-green-500', text: 'text-green-500', glow: 'shadow-green-500/50' };
      case 'offline': return { bg: 'bg-red-500', border: 'border-red-500', text: 'text-red-500', glow: 'shadow-red-500/50' };
      case 'degraded': return { bg: 'bg-yellow-500', border: 'border-yellow-500', text: 'text-yellow-500', glow: 'shadow-yellow-500/50' };
      default: return { bg: 'bg-gray-500', border: 'border-gray-500', text: 'text-gray-500', glow: 'shadow-gray-500/50' };
    }
  };

  const formatBytes = (bytes: number): string => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  const getUsagePercent = (node: Node) => {
    return node.capacity_bytes > 0 
      ? Math.round((node.used_bytes / node.capacity_bytes) * 100) 
      : 0;
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 rounded-lg p-8 text-white">
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2 flex items-center space-x-2">
          <Activity className="w-6 h-6" />
          <span>Distributed Storage Topology</span>
        </h3>
        <p className="text-blue-200 text-sm">Live visualization of your storage network</p>
      </div>

      {/* Topology Diagram */}
      <div className="space-y-8">
        {/* Client Layer */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="bg-white/10 backdrop-blur-sm border-2 border-blue-400 rounded-lg p-4 w-48">
              <div className="flex items-center justify-center space-x-2">
                <Server className="w-6 h-6 text-blue-400" />
                <div>
                  <p className="font-semibold text-blue-100">API Gateway</p>
                  <p className="text-xs text-blue-300">Port 8085</p>
                </div>
              </div>
            </div>
            {/* Pulse animation */}
            <div className="absolute inset-0 border-2 border-blue-400 rounded-lg animate-ping opacity-20" />
          </div>
        </div>

        {/* Connection Lines */}
        <div className="flex justify-center">
          <div className="relative h-16 w-full max-w-3xl">
            {/* Vertical line from gateway */}
            <div className="absolute left-1/2 top-0 w-0.5 h-8 bg-gradient-to-b from-blue-400 to-purple-500 transform -translate-x-1/2" />
            
            {/* Horizontal distribution line */}
            <div className="absolute top-8 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-purple-500 to-transparent" />
            
            {/* Vertical lines to nodes */}
            {nodes.map((node, index) => {
              const positions = ['25%', '50%', '75%'];
              return (
                <div 
                  key={node.id}
                  className="absolute top-8 w-0.5 h-8 bg-gradient-to-b from-purple-500 to-green-400"
                  style={{ left: positions[index] || '50%', transform: 'translateX(-50%)' }}
                />
              );
            })}
          </div>
        </div>

        {/* Storage Nodes Layer */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {nodes.map((node) => {
            const status = getStatusColor(node.status);
            const usagePercent = getUsagePercent(node);
            const isOnline = node.status.toLowerCase() === 'online';

            return (
              <div
                key={node.id}
                onClick={() => onNodeClick?.(node)}
                className={`
                  relative bg-white/10 backdrop-blur-sm border-2 rounded-lg p-4 
                  transition-all duration-300 cursor-pointer group
                  ${status.border}
                  ${isOnline ? 'hover:scale-105 hover:shadow-2xl' : ''}
                  ${isOnline ? status.glow : ''}
                `}
              >
                {/* Status indicator pulse */}
                {isOnline && (
                  <div className={`absolute -top-1 -right-1 w-3 h-3 ${status.bg} rounded-full animate-pulse`}>
                    <div className={`absolute inset-0 ${status.bg} rounded-full animate-ping opacity-75`} />
                  </div>
                )}

                {/* Node Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className={`p-2 ${status.bg} rounded-lg`}>
                      <HardDrive className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-bold text-white">Node {node.id}</p>
                      <p className="text-xs text-gray-300">{node.host}</p>
                    </div>
                  </div>
                  <div className={`px-2 py-1 ${status.bg} rounded-full text-xs font-semibold flex items-center space-x-1`}>
                    {node.status.toLowerCase() === 'online' && <Zap className="w-3 h-3" />}
                    {node.status.toLowerCase() === 'offline' && <AlertTriangle className="w-3 h-3" />}
                    <span>{node.status.toUpperCase()}</span>
                  </div>
                </div>

                {/* Storage Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300">Storage</span>
                    <span className={status.text}>{usagePercent}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        usagePercent > 90 ? 'bg-red-500' :
                        usagePercent > 70 ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${usagePercent}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>{formatBytes(node.used_bytes)} used</span>
                    <span>{formatBytes(node.capacity_bytes)} total</span>
                  </div>
                </div>

                {/* Node Metrics */}
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white/5 rounded p-2">
                    <p className="text-gray-400">Files</p>
                    <p className="font-bold text-white">{Math.floor(Math.random() * 50) + 10}</p>
                  </div>
                  <div className="bg-white/5 rounded p-2">
                    <p className="text-gray-400">Chunks</p>
                    <p className="font-bold text-white">{Math.floor(Math.random() * 150) + 50}</p>
                  </div>
                </div>

                {/* Hover effect */}
                <div className="absolute inset-0 border-2 border-white rounded-lg opacity-0 group-hover:opacity-20 transition-opacity" />
              </div>
            );
          })}
        </div>

        {/* Data Flow Visualization */}
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="w-5 h-5 text-blue-400" />
              <div>
                <p className="text-sm font-semibold">Data Replication</p>
                <p className="text-xs text-gray-400">Each file chunk is replicated across multiple nodes</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex -space-x-2">
                {nodes.filter(n => n.status.toLowerCase() === 'online').map((node) => (
                  <div
                    key={node.id}
                    className="w-8 h-8 rounded-full bg-green-500 border-2 border-gray-900 flex items-center justify-center text-xs font-bold"
                    title={`Node ${node.id}`}
                  >
                    {node.id}
                  </div>
                ))}
              </div>
              <span className="text-sm text-green-400 font-semibold">
                {nodes.filter(n => n.status.toLowerCase() === 'online').length} Online
              </span>
            </div>
          </div>
        </div>

        {/* System Health Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-green-500/30">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <p className="text-xs text-gray-400">Online Nodes</p>
            </div>
            <p className="text-2xl font-bold text-green-400">
              {nodes.filter(n => n.status.toLowerCase() === 'online').length}
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-blue-500/30">
            <div className="flex items-center space-x-2 mb-2">
              <Database className="w-4 h-4 text-blue-400" />
              <p className="text-xs text-gray-400">Total Capacity</p>
            </div>
            <p className="text-2xl font-bold text-blue-400">
              {formatBytes(nodes.reduce((sum, n) => sum + n.capacity_bytes, 0))}
            </p>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-purple-500/30">
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="w-4 h-4 text-purple-400" />
              <p className="text-xs text-gray-400">Avg Usage</p>
            </div>
            <p className="text-2xl font-bold text-purple-400">
              {Math.round(nodes.reduce((sum, n) => sum + getUsagePercent(n), 0) / nodes.length)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
