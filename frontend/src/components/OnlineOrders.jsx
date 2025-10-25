import React, { useState, useEffect } from 'react';
import axios from 'axios';

const OnlineOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showPrescription, setShowPrescription] = useState(false);

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    fetchOrders();
  }, [filter]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const params = {};
      
      if (filter === 'needs_review') {
        params.requires_review = true;
      } else if (filter !== 'all') {
        params.status = filter;
      }

      const response = await axios.get(`${API_URL}/staff/online-orders`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      
      setOrders(response.data.orders);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewPrescription = async (orderId, action) => {
    const notes = action === 'reject' 
      ? prompt('Please provide a reason for rejection:')
      : '';

    if (action === 'reject' && !notes) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/staff/online-orders/${orderId}/review-prescription`,
        { action, notes },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert(`Prescription ${action}d successfully`);
      fetchOrders();
      setSelectedOrder(null);
    } catch (error) {
      alert('Error reviewing prescription');
    }
  };

  const handleUpdateStatus = async (orderId) => {
    const newStatus = prompt('Enter new status (Processing/Out for Delivery/Delivered):');
    if (!newStatus) return;

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/staff/online-orders/${orderId}/update-status`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('Status updated successfully');
      fetchOrders();
    } catch (error) {
      alert('Error updating status');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Pending Review': 'bg-yellow-100 text-yellow-800',
      'Approved': 'bg-blue-100 text-blue-800',
      'Processing': 'bg-indigo-100 text-indigo-800',
      'Out for Delivery': 'bg-purple-100 text-purple-800',
      'Delivered': 'bg-green-100 text-green-800',
      'Rejected': 'bg-red-100 text-red-800',
      'Cancelled': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Online Customer Orders</h2>
        
        {/* Filters */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'all' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Orders
          </button>
          <button
            onClick={() => setFilter('needs_review')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'needs_review' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Needs Review
          </button>
          <button
            onClick={() => setFilter('Processing')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'Processing' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Processing
          </button>
          <button
            onClick={() => setFilter('Delivered')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'Delivered' 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Delivered
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : orders.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600">No orders found</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prescription</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {orders.map((order) => (
                <tr key={order.order_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{order.order_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>
                      <div className="font-medium">{order.customer_name}</div>
                      <div className="text-gray-500">{order.customer_email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(order.order_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ₹{order.total_amount.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {order.requires_prescription ? (
                      <div>
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          order.prescription_status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                          order.prescription_status === 'Approved' ? 'bg-green-100 text-green-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {order.prescription_status}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    {order.needs_review && (
                      <button
                        onClick={() => setSelectedOrder(order)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Review
                      </button>
                    )}
                    <button
                      onClick={() => handleUpdateStatus(order.order_id)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Update Status
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Review Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Review Prescription - Order #{selectedOrder.order_id}</h3>
            
            <div className="mb-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm font-semibold text-gray-700">Customer:</p>
                  <p className="text-sm text-gray-900">{selectedOrder.customer_name}</p>
                  <p className="text-xs text-gray-500">{selectedOrder.customer_email}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-700">Order Total:</p>
                  <p className="text-lg font-bold text-indigo-600">₹{selectedOrder.total_amount.toFixed(2)}</p>
                </div>
              </div>
              
              {selectedOrder.prescription_uploaded && selectedOrder.prescription_file_path && (
                <div className="border-2 border-gray-300 rounded-lg p-4">
                  <p className="text-sm font-semibold text-gray-700 mb-3">Prescription Image:</p>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <img 
                      src={`http://localhost:5000/${selectedOrder.prescription_file_path}`}
                      alt="Prescription"
                      className="w-full h-auto max-h-96 object-contain rounded"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%236b7280" font-family="sans-serif" font-size="16"%3EPrescription Image Not Available%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2 text-center">Click image to view full size</p>
                </div>
              )}
              
              {selectedOrder.prescription_uploaded && !selectedOrder.prescription_file_path && (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-sm text-gray-600 mt-2">Prescription file path not available</p>
                </div>
              )}
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => handleReviewPrescription(selectedOrder.order_id, 'approve')}
                className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition duration-150 font-medium"
              >
                ✓ Approve Prescription
              </button>
              <button
                onClick={() => handleReviewPrescription(selectedOrder.order_id, 'reject')}
                className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-150 font-medium"
              >
                ✗ Reject Prescription
              </button>
              <button
                onClick={() => setSelectedOrder(null)}
                className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition duration-150 font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OnlineOrders;
