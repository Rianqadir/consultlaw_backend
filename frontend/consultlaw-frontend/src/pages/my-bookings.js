// frontend/src/pages/my-bookings.js
import { useEffect, useState } from 'react';
import authAPI from '../utils/authAPI';
import { format } from 'date-fns';

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const [lawyerDetails, setLawyerDetails] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchBookings();
  }, [filter]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await authAPI.get(`/auth/my-bookings/?filter=${filter}`);
      setBookings(response.data);
    } catch (error) {
      console.error('Failed to fetch bookings', error);
    } finally {
      setLoading(false);
    }
  };

  const cancelBooking = async (id) => {
    try {
      await authAPI.delete(`/auth/bookings/${id}/`);
      fetchBookings(); // Refresh list
    } catch (error) {
      console.error('Failed to cancel booking', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-semibold mb-6 text-center">My Bookings</h1>

      <div className="flex justify-center gap-4 mb-6">
        {['all', 'upcoming', 'past'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-md border ${
              filter === f ? 'bg-blue-600 text-white' : 'bg-white text-blue-600'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-center">Loading...</p>
      ) : bookings.length === 0 ? (
        <p className="text-center text-gray-500">No bookings found.</p>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="bg-white p-4 shadow rounded-md border">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold">{booking.lawyer_name}</h2>
                  <p className="text-gray-500">{booking.specialization}</p>
                  <p className="mt-1">
                    <strong>Date:</strong> {format(new Date(booking.date), 'dd MMM yyyy')} <br />
                    <strong>Time:</strong> {booking.time}
                  </p>
                </div>
                <div className="flex flex-col gap-2">
                  {booking.status !== 'completed' && (
                    <button
                      onClick={() => cancelBooking(booking.id)}
                      className="text-red-600 border border-red-600 px-3 py-1 rounded-md hover:bg-red-50"
                    >
                      Cancel
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setLawyerDetails(booking);
                      setShowModal(true);
                    }}
                    className="text-blue-600 border border-blue-600 px-3 py-1 rounded-md hover:bg-blue-50"
                  >
                    View Lawyer
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Lawyer Details Modal */}
      {showModal && lawyerDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-md p-6 rounded-md relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-2 right-2 text-gray-500"
            >
              ✕
            </button>
            <h2 className="text-xl font-semibold mb-2">{lawyerDetails.lawyer_name}</h2>
            <p className="text-gray-600 mb-2">{lawyerDetails.specialization}</p>
            <p className="text-gray-600">
              <strong>Email:</strong> {lawyerDetails.lawyer_email} <br />
              <strong>Phone:</strong> {lawyerDetails.lawyer_phone}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
