import { X, Download, FileText, Image, Film, Music, File } from 'lucide-react';

interface FilePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: {
    file_id: string;
    filename: string;
    original_size: number;
    created_at: string;
  } | null;
  onDownload: () => void;
}

export default function FilePreviewModal({ isOpen, onClose, file, onDownload }: FilePreviewModalProps) {
  if (!isOpen || !file) return null;

  const getFileType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return 'image';
    if (['mp4', 'webm', 'ogg'].includes(ext)) return 'video';
    if (['mp3', 'wav', 'ogg'].includes(ext)) return 'audio';
    if (['pdf'].includes(ext)) return 'pdf';
    if (['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts'].includes(ext)) return 'text';
    return 'unknown';
  };

  const fileType = getFileType(file.filename);

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = () => {
    switch (fileType) {
      case 'image': return <Image className="w-8 h-8" />;
      case 'video': return <Film className="w-8 h-8" />;
      case 'audio': return <Music className="w-8 h-8" />;
      case 'pdf':
      case 'text': return <FileText className="w-8 h-8" />;
      default: return <File className="w-8 h-8" />;
    }
  };

  const renderPreview = () => {
    // In a real implementation, you would fetch the file URL from your API
    // const fileUrl = `http://localhost:8085/api/v1/files/${file.file_id}/download`;

    switch (fileType) {
      case 'image':
        return (
          <div className="flex items-center justify-center bg-gray-900 rounded-lg p-8">
            <div className="text-center">
              <Image className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-300 mb-4">Image Preview</p>
              <p className="text-sm text-gray-400 mb-4">
                In production, image would be displayed here
              </p>
              {/* Uncomment for real preview: */}
              {/* <img src={demoUrl} alt={file.filename} className="max-w-full max-h-96 rounded" /> */}
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download to View
              </button>
            </div>
          </div>
        );

      case 'video':
        return (
          <div className="flex items-center justify-center bg-gray-900 rounded-lg p-8">
            <div className="text-center">
              <Film className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-300 mb-4">Video Preview</p>
              <p className="text-sm text-gray-400 mb-4">
                In production, video player would be here
              </p>
              {/* Uncomment for real preview: */}
              {/* <video controls className="max-w-full max-h-96 rounded">
                <source src={demoUrl} />
              </video> */}
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download to View
              </button>
            </div>
          </div>
        );

      case 'audio':
        return (
          <div className="flex items-center justify-center bg-gray-900 rounded-lg p-8">
            <div className="text-center">
              <Music className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-300 mb-4">Audio Preview</p>
              <p className="text-sm text-gray-400 mb-4">
                In production, audio player would be here
              </p>
              {/* Uncomment for real preview: */}
              {/* <audio controls className="w-full">
                <source src={demoUrl} />
              </audio> */}
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download to View
              </button>
            </div>
          </div>
        );

      case 'pdf':
        return (
          <div className="flex items-center justify-center bg-gray-50 rounded-lg p-8">
            <div className="text-center">
              <FileText className="w-24 h-24 text-red-500 mx-auto mb-4" />
              <p className="text-gray-700 mb-4">PDF Document</p>
              <p className="text-sm text-gray-500 mb-4">
                In production, PDF viewer would be here
              </p>
              {/* Uncomment for real preview: */}
              {/* <iframe src={demoUrl} className="w-full h-96 rounded" /> */}
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download to View
              </button>
            </div>
          </div>
        );

      case 'text':
        return (
          <div className="bg-gray-900 rounded-lg p-6">
            <div className="text-center mb-4">
              <FileText className="w-12 h-12 text-green-400 mx-auto mb-2" />
              <p className="text-gray-300">Text File Preview</p>
              <p className="text-sm text-gray-400 mt-2">
                In production, file contents would be displayed here
              </p>
            </div>
            <button
              onClick={onDownload}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Download to View
            </button>
          </div>
        );

      default:
        return (
          <div className="flex items-center justify-center bg-gray-50 rounded-lg p-8">
            <div className="text-center">
              <File className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-700 mb-2">Preview not available</p>
              <p className="text-sm text-gray-500 mb-4">
                This file type cannot be previewed in the browser
              </p>
              <button
                onClick={onDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download File
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-75 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 text-blue-600">
                {getFileIcon()}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {file.filename}
                </h3>
                <div className="flex items-center space-x-3 text-sm text-gray-500">
                  <span>{formatBytes(file.original_size)}</span>
                  <span>•</span>
                  <span>{new Date(file.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={onDownload}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Download"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Preview Content */}
          <div className="flex-1 overflow-auto p-6">
            {renderPreview()}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t bg-gray-50">
            <div className="text-sm text-gray-600">
              <span className="font-medium">File ID:</span> {file.file_id}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
