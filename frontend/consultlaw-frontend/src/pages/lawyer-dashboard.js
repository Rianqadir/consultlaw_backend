// src/pages/lawyer-dashboard.js
import React, { useEffect, useState } from 'react';
import authAPI from '../utils/authAPI';
import { useRouter } from 'next/router';

export default function LawyerDashboard() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchBookings = async () => {
    try {
      const response = await authAPI.get('/auth/lawyer/dashboard/');
      setBookings(response.data);
    } catch (error) {
      console.error('Failed to fetch bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const cancelBooking = async (bookingId) => {
    try {
      await authAPI.post(`/auth/bookings/${bookingId}/cancel/`);
      setBookings((prev) => prev.filter((b) => b.id !== bookingId));
    } catch (error) {
      console.error('Failed to cancel booking:', error);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  if (loading) return <div className="p-6">Loading dashboard...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Lawyer Dashboard</h1>
      {bookings.length === 0 ? (
        <p>No upcoming bookings.</p>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="border p-4 rounded-md shadow">
              <p><strong>Client:</strong> {booking.client_name}</p>
              <p><strong>Date:</strong> {booking.date}</p>
              <p><strong>Time:</strong> {booking.time}</p>
              <button
                onClick={() => cancelBooking(booking.id)}
                className="mt-2 px-4 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Cancel Booking
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
