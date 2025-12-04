import { useState, useRef } from 'react';
import { Upload, File, X } from 'lucide-react';

interface DragDropUploadProps {
  onFileSelect: (file: File) => void;
  uploading: boolean;
  selectedFile: File | null;
  onClearFile: () => void;
}

export default function DragDropUpload({ 
  onFileSelect, 
  uploading, 
  selectedFile,
  onClearFile 
}: DragDropUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragging 
            ? 'border-blue-500 bg-blue-50 scale-105' 
            : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileInput}
          className="hidden"
          disabled={uploading}
        />

        <div className="space-y-4">
          {/* Upload Icon */}
          <div className={`
            w-16 h-16 mx-auto rounded-full flex items-center justify-center
            transition-colors duration-200
            ${isDragging ? 'bg-blue-500' : 'bg-blue-100'}
          `}>
            <Upload className={`w-8 h-8 ${isDragging ? 'text-white' : 'text-blue-600'}`} />
          </div>

          {/* Text */}
          <div>
            <p className={`text-lg font-semibold mb-1 ${isDragging ? 'text-blue-600' : 'text-gray-700'}`}>
              {isDragging ? 'Drop file here' : 'Drag & drop your file here'}
            </p>
            <p className="text-sm text-gray-500">
              or click to browse from your computer
            </p>
          </div>

          {/* Supported formats */}
          <div className="text-xs text-gray-400">
            <p>Supported: All file types</p>
            <p>Max size: Based on your storage quota</p>
          </div>
        </div>

        {/* Animated border */}
        {isDragging && (
          <div className="absolute inset-0 border-2 border-blue-500 rounded-lg animate-pulse" />
        )}
      </div>

      {/* Selected File Preview */}
      {selectedFile && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <File className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-gray-500">
                  {formatBytes(selectedFile.size)}
                </p>
              </div>
            </div>
            {!uploading && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onClearFile();
                }}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
                title="Remove file"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Progress indicator when uploading */}
          {uploading && (
            <div className="mt-3 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Uploading...</span>
                <span className="text-blue-600 font-medium">Processing</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse" style={{ width: '100%' }} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
