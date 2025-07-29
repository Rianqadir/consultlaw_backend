'use client';

import { useForm } from 'react-hook-form';
import axios from '@/lib/publicAPI'; // Make sure this path is correct
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/auth/login/', data);
      const token = response.data.token;
      localStorage.setItem('token', token);
      router.push('/dashboard');
    } catch (err) {
      console.error(err);
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="bg-white rounded-xl shadow-xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Login to ConsultLaw</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              {...register('email', { required: true })}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md focus:ring focus:ring-indigo-200"
              placeholder="you@example.com"
            />
            {errors.email && <p className="text-red-500 text-sm">Email is required</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              {...register('password', { required: true })}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md focus:ring focus:ring-indigo-200"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-500 text-sm">Password is required</p>}
          </div>

          {error && <p className="text-red-500 text-sm text-center">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}
