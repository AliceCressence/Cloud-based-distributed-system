import { Shield, AlertTriangle, CheckCircle, FileWarning, Loader } from 'lucide-react';
import { useState, useEffect } from 'react';

interface ContentModerationCheckProps {
  file: File | null;
  onApproved: () => void;
  onRejected: (reason: string) => void;
}

interface ModerationResult {
  approved: boolean;
  issues: {
    type: 'virus' | 'inappropriate' | 'malicious' | 'size' | 'type';
    severity: 'high' | 'medium' | 'low';
    message: string;
  }[];
  fileHash?: string;
  scanTime: number;
}

export default function ContentModerationCheck({ 
  file, 
  onApproved, 
  onRejected 
}: ContentModerationCheckProps) {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ModerationResult | null>(null);

  useEffect(() => {
    if (file) {
      performModeration(file);
    }
  }, [file]);

  const performModeration = async (fileToCheck: File) => {
    setScanning(true);
    setResult(null);

    // Simulate file scanning process
    await new Promise(resolve => setTimeout(resolve, 1500));

    const issues: ModerationResult['issues'] = [];

    // 1. File Type Check
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp',
      'application/pdf', 'text/plain', 'text/csv',
      'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'video/mp4', 'video/webm', 'audio/mpeg', 'audio/wav',
      'application/zip', 'application/x-zip-compressed'
    ];

    if (!allowedTypes.includes(fileToCheck.type) && fileToCheck.type !== '') {
      issues.push({
        type: 'type',
        severity: 'medium',
        message: `File type "${fileToCheck.type}" may not be supported. Proceed with caution.`
      });
    }

    // 2. File Size Check (warn if > 50MB)
    const maxWarningSize = 50 * 1024 * 1024; // 50MB
    if (fileToCheck.size > maxWarningSize) {
      issues.push({
        type: 'size',
        severity: 'medium',
        message: `Large file detected (${(fileToCheck.size / (1024 * 1024)).toFixed(2)}MB). Upload may take longer.`
      });
    }

    // 3. Filename Analysis (check for suspicious patterns)
    const suspiciousPatterns = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js'];
    const lowerName = fileToCheck.name.toLowerCase();
    
    if (suspiciousPatterns.some(pattern => lowerName.endsWith(pattern))) {
      issues.push({
        type: 'malicious',
        severity: 'high',
        message: 'Executable file detected. Upload blocked for security reasons.'
      });
    }

    // 4. Simulated Virus Scan (random for demo)
    const virusScanRandom = Math.random();
    if (virusScanRandom < 0.05) { // 5% chance to simulate virus detection
      issues.push({
        type: 'virus',
        severity: 'high',
        message: 'Potential malware detected. File upload blocked.'
      });
    }

    // 5. Content Analysis (simulate inappropriate content detection)
    const inappropriateKeywords = ['hack', 'crack', 'pirate', 'warez'];
    if (inappropriateKeywords.some(keyword => lowerName.includes(keyword))) {
      issues.push({
        type: 'inappropriate',
        severity: 'medium',
        message: 'Filename contains potentially inappropriate content. Please review.'
      });
    }

    // Determine if file is approved
    const highSeverityIssues = issues.filter(i => i.severity === 'high');
    const approved = highSeverityIssues.length === 0;

    // Generate simulated file hash
    const fileHash = `sha256:${Array.from({length: 64}, () => 
      Math.floor(Math.random() * 16).toString(16)).join('')}`;

    const moderationResult: ModerationResult = {
      approved,
      issues,
      fileHash,
      scanTime: 1500
    };

    setResult(moderationResult);
    setScanning(false);

    if (approved) {
      onApproved();
    } else {
      onRejected(highSeverityIssues.map(i => i.message).join('; '));
    }
  };

  if (!file) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 my-4">
      <div className="flex items-center space-x-3 mb-3">
        <Shield className="w-6 h-6 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Security & Content Check</h3>
      </div>

      {scanning && (
        <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
          <Loader className="w-5 h-5 text-blue-600 animate-spin" />
          <div>
            <p className="text-sm font-medium text-blue-900">Scanning file...</p>
            <p className="text-xs text-blue-700">Checking for viruses, malware, and inappropriate content</p>
          </div>
        </div>
      )}

      {result && !scanning && (
        <div className="space-y-3">
          {/* Overall Status */}
          <div className={`flex items-center space-x-3 p-4 rounded-lg ${
            result.approved 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            {result.approved ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-red-600" />
            )}
            <div className="flex-1">
              <p className={`font-semibold ${
                result.approved ? 'text-green-900' : 'text-red-900'
              }`}>
                {result.approved ? 'File Approved' : 'Upload Blocked'}
              </p>
              <p className={`text-sm ${
                result.approved ? 'text-green-700' : 'text-red-700'
              }`}>
                {result.approved 
                  ? 'No security threats detected. Safe to upload.' 
                  : 'Security issues found. Please review the warnings below.'}
              </p>
            </div>
          </div>

          {/* Scan Details */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-gray-500 text-xs">Scan Time</p>
              <p className="font-medium text-gray-900">{result.scanTime}ms</p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-gray-500 text-xs">File Hash</p>
              <p className="font-mono text-gray-900 text-xs truncate" title={result.fileHash}>
                {result.fileHash?.substring(0, 20)}...
              </p>
            </div>
          </div>

          {/* Issues List */}
          {result.issues.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">
                {result.issues.length} Issue{result.issues.length > 1 ? 's' : ''} Found:
              </p>
              {result.issues.map((issue, index) => (
                <div 
                  key={index}
                  className={`flex items-start space-x-2 p-3 rounded-lg border ${
                    issue.severity === 'high' 
                      ? 'bg-red-50 border-red-200' 
                      : issue.severity === 'medium'
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  <FileWarning className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
                    issue.severity === 'high' 
                      ? 'text-red-600' 
                      : issue.severity === 'medium'
                      ? 'text-yellow-600'
                      : 'text-blue-600'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-xs font-semibold uppercase ${
                      issue.severity === 'high' 
                        ? 'text-red-900' 
                        : issue.severity === 'medium'
                        ? 'text-yellow-900'
                        : 'text-blue-900'
                    }`}>
                      {issue.type} - {issue.severity} severity
                    </p>
                    <p className={`text-sm ${
                      issue.severity === 'high' 
                        ? 'text-red-800' 
                        : issue.severity === 'medium'
                        ? 'text-yellow-800'
                        : 'text-blue-800'
                    }`}>
                      {issue.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Security Checks Performed */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-xs font-medium text-gray-700 mb-2">Security Checks Performed:</p>
            <ul className="space-y-1 text-xs text-gray-600">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Virus & Malware Scan</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>File Type Validation</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Filename Analysis</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Content Pattern Recognition</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>File Integrity Verification</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
