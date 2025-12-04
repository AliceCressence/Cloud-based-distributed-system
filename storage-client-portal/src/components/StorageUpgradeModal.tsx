import { useState } from 'react';
import { X, Check, Zap, Clock, Mail, CreditCard, Sparkles } from 'lucide-react';

interface StorageUpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentQuota: number; // in GB
  onUpgradeSuccess: (newQuota: number) => void;
}

interface PricingPlan {
  id: string;
  name: string;
  storage: number; // in GB
  price: number; // per month
  popular?: boolean;
  features: string[];
}

const plans: PricingPlan[] = [
  {
    id: 'basic',
    name: 'Basic',
    storage: 10,
    price: 0,
    features: [
      '10GB storage space',
      'Basic upload speed',
      'Standard support',
      'Email notifications'
    ]
  },
  {
    id: 'premium',
    name: 'Premium',
    storage: 50,
    price: 4.99,
    popular: true,
    features: [
      '50GB storage space',
      'Priority upload speed',
      'Extended file history',
      'Email support',
      'File sharing links'
    ]
  },
  {
    id: 'pro',
    name: 'Pro',
    storage: 100,
    price: 9.99,
    features: [
      '100GB storage space',
      'Ultra-fast upload speed',
      'Unlimited file history',
      'Priority support 24/7',
      'Advanced sharing options',
      'API access'
    ]
  }
];

export default function StorageUpgradeModal({
  isOpen,
  onClose,
  currentQuota,
  onUpgradeSuccess
}: StorageUpgradeModalProps) {
  const [step, setStep] = useState<'plans' | 'payment' | 'success'>('plans');
  const [selectedPlan, setSelectedPlan] = useState<PricingPlan | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSelectPlan = (plan: PricingPlan) => {
    if (plan.storage <= currentQuota) return; // Can't downgrade
    setSelectedPlan(plan);
    setStep('payment');
  };

  const handlePayment = async () => {
    setLoading(true);
    
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setLoading(false);
    setStep('success');
    
    // Update user quota after 1 second on success screen
    setTimeout(() => {
      if (selectedPlan) {
        onUpgradeSuccess(selectedPlan.storage);
      }
    }, 1000);
  };

  const handleClose = () => {
    setStep('plans');
    setSelectedPlan(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full my-8">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {step === 'plans' && 'Upgrade Your Storage'}
                  {step === 'payment' && 'Payment Details'}
                  {step === 'success' && 'Upgrade Successful!'}
                </h3>
                <p className="text-sm text-gray-500">
                  {step === 'plans' && 'Choose the perfect plan for your needs'}
                  {step === 'payment' && 'Secure payment processing (Demo Mode)'}
                  {step === 'success' && 'Your storage has been upgraded'}
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {step === 'plans' && (
              <div className="space-y-6">
                {/* Current Storage */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Current Plan:</strong> {currentQuota}GB Storage
                  </p>
                </div>

                {/* Pricing Plans */}
                <div className="grid md:grid-cols-3 gap-6">
                  {plans.map((plan) => {
                    const isCurrent = plan.storage === currentQuota;
                    const isDowngrade = plan.storage < currentQuota;
                    
                    return (
                      <div
                        key={plan.id}
                        className={`relative border-2 rounded-lg p-6 transition-all ${
                          plan.popular
                            ? 'border-blue-500 shadow-lg scale-105'
                            : 'border-gray-200 hover:border-blue-300'
                        } ${isCurrent || isDowngrade ? 'opacity-60' : ''}`}
                      >
                        {plan.popular && (
                          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                            <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                              POPULAR
                            </span>
                          </div>
                        )}

                        <div className="text-center mb-4">
                          <h4 className="text-lg font-bold text-gray-900">{plan.name}</h4>
                          <div className="mt-2">
                            <span className="text-4xl font-bold text-gray-900">
                              {plan.price === 0 ? 'Free' : `$${plan.price}`}
                            </span>
                            {plan.price > 0 && (
                              <span className="text-gray-500 text-sm">/month</span>
                            )}
                          </div>
                          <p className="text-gray-600 mt-2 font-semibold">{plan.storage}GB Storage</p>
                        </div>

                        <ul className="space-y-3 mb-6">
                          {plan.features.map((feature, idx) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                              <span className="text-sm text-gray-600">{feature}</span>
                            </li>
                          ))}
                        </ul>

                        <button
                          onClick={() => handleSelectPlan(plan)}
                          disabled={isCurrent || isDowngrade}
                          className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
                            isCurrent
                              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                              : isDowngrade
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : plan.popular
                              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {isCurrent ? 'Current Plan' : isDowngrade ? 'Not Available' : 'Select Plan'}
                        </button>
                      </div>
                    );
                  })}
                </div>

                {/* Benefits Section */}
                <div className="grid md:grid-cols-3 gap-4 mt-8">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <Zap className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-900">Instant Upgrade</h5>
                      <p className="text-sm text-gray-600">Storage available immediately after payment</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <Clock className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-900">Cancel Anytime</h5>
                      <p className="text-sm text-gray-600">No long-term commitment required</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <Mail className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-900">24/7 Support</h5>
                      <p className="text-sm text-gray-600">Get help whenever you need it</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 'payment' && selectedPlan && (
              <div className="max-w-md mx-auto space-y-6">
                {/* Selected Plan Summary */}
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-2">Selected Plan</h4>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-bold text-gray-900">{selectedPlan.name}</p>
                      <p className="text-sm text-gray-600">{selectedPlan.storage}GB Storage</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">${selectedPlan.price}</p>
                      <p className="text-sm text-gray-600">per month</p>
                    </div>
                  </div>
                </div>

                {/* Demo Mode Notice */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>ℹ️ Demo Mode:</strong> This is a demonstration. No real payment will be processed. 
                    Use any test card details.
                  </p>
                </div>

                {/* Payment Form */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <CreditCard className="w-4 h-4 inline mr-1" />
                      Card Number
                    </label>
                    <input
                      type="text"
                      defaultValue="4242 4242 4242 4242"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      readOnly
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expiry Date
                      </label>
                      <input
                        type="text"
                        defaultValue="12/25"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        readOnly
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CVV
                      </label>
                      <input
                        type="text"
                        defaultValue="123"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        readOnly
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cardholder Name
                    </label>
                    <input
                      type="text"
                      defaultValue="John Doe"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      readOnly
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={() => setStep('plans')}
                    disabled={loading}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Back
                  </button>
                  <button
                    onClick={handlePayment}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span>Processing...</span>
                      </>
                    ) : (
                      <span>Complete Purchase</span>
                    )}
                  </button>
                </div>
              </div>
            )}

            {step === 'success' && selectedPlan && (
              <div className="text-center py-8 space-y-6">
                {/* Success Icon */}
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <Check className="w-10 h-10 text-green-600" />
                </div>

                <div>
                  <h4 className="text-2xl font-bold text-gray-900 mb-2">
                    Upgrade Successful!
                  </h4>
                  <p className="text-gray-600">
                    Your storage has been upgraded to <strong>{selectedPlan.name}</strong>
                  </p>
                </div>

                {/* New Quota Info */}
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6 max-w-md mx-auto">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <p className="text-sm text-gray-600">Previous Quota</p>
                      <p className="text-2xl font-bold text-gray-900">{currentQuota}GB</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">New Quota</p>
                      <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        {selectedPlan.storage}GB
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-blue-200">
                    <p className="text-sm text-gray-700">
                      <strong>New Free Space:</strong> {selectedPlan.storage - currentQuota}GB additional storage
                    </p>
                  </div>
                </div>

                <button
                  onClick={handleClose}
                  className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors"
                >
                  Continue
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
