'use client';

import { useEffect, useState } from 'react';
import publicAPI from '@/lib/publicAPI';

export default function ProfessionalListPage() {
  const [professionals, setProfessionals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProfessionals() {
      try {
        const response = await publicAPI.get('/auth/professionals/');
        setProfessionals(response.data);
      } catch (error) {
        console.error('Error fetching professionals:', error);
        alert('Failed to load professionals.');
      } finally {
        setLoading(false);
      }
    }

    fetchProfessionals();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center text-indigo-700">Available Lawyers</h1>

        {loading ? (
          <p className="text-center text-gray-500">Loading...</p>
        ) : professionals.length === 0 ? (
          <p className="text-center text-gray-500">No professionals found.</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {professionals.map((lawyer) => (
              <div key={lawyer.id} className="bg-white p-5 rounded-xl shadow hover:shadow-md transition">
                <h2 className="text-xl font-semibold text-gray-800">
                  {lawyer.first_name} {lawyer.last_name}
                </h2>
                <p className="text-sm text-gray-600 mt-1">Email: {lawyer.email}</p>
                <p className="text-sm text-gray-600 mt-1">Specialty: {lawyer.specialty || 'General Law'}</p>

                <button
                className="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm font-medium"
                onClick={() => setSelectedLawyer(lawyer)}
                >
                Book Consultation
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

{selectedLawyer && (
  <div className="fixed inset-0 bg-black bg-opacity-40 z-50 flex justify-center items-center">
    <div className="bg-white rounded-lg p-6 w-full max-w-md">
      <h2 className="text-xl font-semibold mb-2">Book Consultation with {selectedLawyer.first_name}</h2>

      <label className="block mt-4 text-sm font-medium">Date</label>
      <input
        type="date"
        value={bookingDate}
        onChange={(e) => setBookingDate(e.target.value)}
        className="w-full border px-3 py-2 rounded mt-1"
      />

      <label className="block mt-4 text-sm font-medium">Time</label>
      <input
        type="time"
        value={bookingTime}
        onChange={(e) => setBookingTime(e.target.value)}
        className="w-full border px-3 py-2 rounded mt-1"
      />

      <label className="block mt-4 text-sm font-medium">Message</label>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={3}
        className="w-full border px-3 py-2 rounded mt-1"
      ></textarea>

      <div className="mt-6 flex justify-between">
        <button
          onClick={() => setSelectedLawyer(null)}
          className="text-sm text-gray-600 hover:underline"
        >
          Cancel
        </button>
        <button
          onClick={handleBooking}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm font-medium"
        >
          Confirm Booking
        </button>
      </div>
    </div>
  </div>
)}


import protectedAPI from '@/lib/protectedAPI';

async function handleBooking() {
  if (!bookingDate || !bookingTime) {
    alert('Please provide date and time.');
    return;
  }

  try {
    await protectedAPI.post('/bookings/', {
      lawyer: selectedLawyer.id,
      date: bookingDate,
      time: bookingTime,
      message: notes,
    });

    alert('Booking successful! Lawyer will be notified.');
    setSelectedLawyer(null);
    setBookingDate('');
    setBookingTime('');
    setNotes('');
  } catch (error) {
    console.error('Booking failed:', error);
    alert('Booking failed. Please try again.');
  }
}

