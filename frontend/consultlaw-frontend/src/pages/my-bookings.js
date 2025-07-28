// pages/my-bookings.js

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import authAPI from '@/utils/authAPI';
import Navbar from '@/components/navbar';

export default function MyBookings() {
  const router = useRouter();
  const [bookings, setBookings] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selectedLawyer, setSelectedLawyer] = useState(null);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await authAPI.get(`/auth/my-bookings/?filter=${filter}`);
      setBookings(response.data);
    } catch (error) {
      console.error('Failed to fetch bookings', error);
      if (error.response?.status === 401) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const cancelBooking = async (bookingId) => {
    try {
      await authAPI.delete(`/auth/cancel-booking/${bookingId}/`);
      setBookings((prev) => prev.filter((b) => b.id !== bookingId));
    } catch (error) {
      alert('Error cancelling booking.');
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [filter]);

  return (
    <>
      <Navbar />
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">My Bookings</h1>

        {/* Filter Buttons */}
        <div className="mb-4 flex gap-2">
          {['all', 'upcoming', 'past'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1 rounded-md text-sm ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Booking List */}
        {loading ? (
          <p>Loading...</p>
        ) : bookings.length === 0 ? (
          <p>No bookings found.</p>
        ) : (
          <ul className="space-y-4">
            {bookings.map((booking) => (
              <li
                key={booking.id}
                className="border p-4 rounded-md shadow-sm bg-white relative"
              >
                <p><strong>Lawyer:</strong> {booking.lawyer_name}</p>
                <p><strong>Date:</strong> {booking.date}</p>
                <p><strong>Time:</strong> {booking.time}</p>
                <p><strong>Status:</strong> {booking.status}</p>

                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => setSelectedLawyer(booking.lawyer_details)}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    View Lawyer Details
                  </button>

                  {booking.status === 'Pending' && (
                    <button
                      onClick={() => cancelBooking(booking.id)}
                      className="text-red-600 hover:underline text-sm"
                    >
                      Cancel Booking
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>

      {/* Lawyer Details Modal */}
      {selectedLawyer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-md p-6 max-w-md w-full relative">
            <button
              onClick={() => setSelectedLawyer(null)}
              className="absolute top-2 right-2 text-gray-500"
            >
              ✕
            </button>
            <h2 className="text-xl font-semibold mb-2">Lawyer Details</h2>
            <p><strong>Name:</strong> {selectedLawyer.name}</p>
            <p><strong>Email:</strong> {selectedLawyer.email}</p>
            <p><strong>Phone:</strong> {selectedLawyer.phone}</p>
            <p><strong>Specialty:</strong> {selectedLawyer.specialty}</p>
            {/* Add more fields if needed */}
          </div>
        </div>
      )}
    </>
  );
}
