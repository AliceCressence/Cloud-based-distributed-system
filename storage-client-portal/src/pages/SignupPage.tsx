import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import { api } from '../lib/api';
import { Upload, Mail, Lock, User, Shield } from 'lucide-react';

export default function SignupPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [step, setStep] = useState<'details' | 'otp'>('details');
  const [formData, setFormData] = useState({
    user_id: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      showToast('Passwords do not match', 'error');
      return;
    }

    if (formData.password.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }

    setLoading(true);
    try {
      // Request OTP
      await api.post('/verify/request-otp', { email: formData.email });
      showToast('OTP sent to your email!', 'success');
      setStep('otp');
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to send OTP', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (otpCode.length !== 6) {
      showToast('Please enter 6-digit OTP code', 'error');
      return;
    }

    setLoading(true);
    try {
      // Verify OTP
      await api.post('/verify/verify-otp', {
        email: formData.email,
        otp_code: otpCode
      });

      // Register user
      await api.post('/auth/register', {
        user_id: formData.user_id,
        email: formData.email,
        password: formData.password,
        role: 'USER'
      });

      showToast('Account created successfully! Please login.', 'success');
      navigate('/login');
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to create account', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setLoading(true);
    try {
      await api.post('/verify/resend-otp', { email: formData.email });
      showToast('New OTP sent to your email!', 'success');
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to resend OTP', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <Upload className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">ICTNexus Storage</h1>
          <p className="text-gray-600 mt-2">Create your free account</p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          {step === 'details' ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <User className="w-4 h-4 inline mr-2" />
                  Student ID
                </label>
                <input
                  type="text"
                  required
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., STU001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="you@ictnexus.edu"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Lock className="w-4 h-4 inline mr-2" />
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Min. 6 characters"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Lock className="w-4 h-4 inline mr-2" />
                  Confirm Password
                </label>
                <input
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Re-enter password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Sending OTP...' : 'Continue to Verification'}
              </button>

              <div className="text-center text-sm">
                <span className="text-gray-600">Already have an account? </span>
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Login
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-3">
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Verify Your Email</h2>
                <p className="text-sm text-gray-600 mt-2">
                  We sent a 6-digit code to<br />
                  <span className="font-medium text-gray-900">{formData.email}</span>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-center">
                  Enter OTP Code
                </label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                  className="w-full px-4 py-3 text-center text-2xl font-bold tracking-widest border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="000000"
                />
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Code expires in 10 minutes
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || otpCode.length !== 6}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying...' : 'Create Account'}
              </button>

              <div className="text-center space-y-2">
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={loading}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                >
                  Resend OTP
                </button>
                <br />
                <button
                  type="button"
                  onClick={() => setStep('details')}
                  className="text-sm text-gray-600 hover:text-gray-700"
                >
                  ← Back to details
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>🎁 Get 2GB free cloud storage</p>
          <p className="text-xs mt-1">Secure • Reliable • Always accessible</p>
        </div>
      </div>
    </div>
  );
}
