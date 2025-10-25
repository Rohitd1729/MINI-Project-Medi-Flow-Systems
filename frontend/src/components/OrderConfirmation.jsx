import React from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';

const OrderConfirmation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { orderId, total, requiresReview } = location.state || {};

  if (!orderId) {
    navigate('/shop');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-400 via-blue-500 to-purple-600 flex items-center justify-center py-12 px-4">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-8 animate-fade-in">
        {/* Success Icon */}
        <div className="text-center mb-6">
          <div className="mx-auto h-24 w-24 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <svg className="h-16 w-16 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Placed Successfully!</h1>
          <p className="text-gray-600">Thank you for your order</p>
        </div>

        {/* Order Details */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">Order ID</p>
              <p className="text-lg font-bold text-indigo-600">#{orderId}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Amount</p>
              <p className="text-lg font-bold text-gray-900">₹{total?.toFixed(2)}</p>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {requiresReview ? (
          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg mb-6">
            <div className="flex">
              <svg className="h-6 w-6 text-yellow-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-yellow-800 mb-1">Prescription Under Review</h3>
                <p className="text-sm text-yellow-700">
                  Your prescription is being reviewed by our pharmacist. You'll receive an update once it's approved.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg mb-6">
            <div className="flex">
              <svg className="h-6 w-6 text-green-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-green-800 mb-1">Order Confirmed</h3>
                <p className="text-sm text-green-700">
                  Your order is being processed and will be delivered soon.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* What's Next */}
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">What happens next?</h3>
          <div className="space-y-3">
            {requiresReview && (
              <div className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                  <span className="text-xs font-bold text-indigo-600">1</span>
                </div>
                <p className="text-sm text-gray-700">Our pharmacist will review your prescription</p>
              </div>
            )}
            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                <span className="text-xs font-bold text-indigo-600">{requiresReview ? '2' : '1'}</span>
              </div>
              <p className="text-sm text-gray-700">Your order will be packed and prepared for delivery</p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                <span className="text-xs font-bold text-indigo-600">{requiresReview ? '3' : '2'}</span>
              </div>
              <p className="text-sm text-gray-700">You'll receive your order within 3-5 business days</p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                <span className="text-xs font-bold text-indigo-600">{requiresReview ? '4' : '3'}</span>
              </div>
              <p className="text-sm text-gray-700">Pay cash on delivery when you receive your order</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Link
            to={`/customer/orders/${orderId}`}
            className="block w-full text-center bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition duration-150 font-medium"
          >
            View Order Details
          </Link>
          <Link
            to="/customer/orders"
            className="block w-full text-center bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition duration-150 font-medium"
          >
            View All Orders
          </Link>
          <Link
            to="/shop"
            className="block w-full text-center border-2 border-indigo-600 text-indigo-600 py-3 px-4 rounded-lg hover:bg-indigo-50 transition duration-150 font-medium"
          >
            Continue Shopping
          </Link>
        </div>

        {/* Support Info */}
        <div className="mt-6 pt-6 border-t text-center">
          <p className="text-sm text-gray-600">
            Need help? Contact us at{' '}
            <a href="mailto:support@mediflow.com" className="text-indigo-600 hover:text-indigo-800">
              support@mediflow.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;
