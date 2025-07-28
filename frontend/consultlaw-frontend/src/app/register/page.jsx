'use client';

import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import publicAPI from '@/lib/publicAPI';

export default function RegisterPage() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const password = watch('password');

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const response = await publicAPI.post('/auth/register/', {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        password: data.password,
        confirm_password: data.confirm_password,
        role: data.role,
      });

      alert('Registration successful!');
      router.push('/login');
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-indigo-700">Create Account</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">First Name</label>
            <input
              type="text"
              {...register('first_name', { required: true })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            />
            {errors.first_name && <p className="text-red-500 text-sm">First name is required</p>}
          </div>
          <div>
            <label className="block text-sm font-medium">Last Name</label>
            <input
              type="text"
              {...register('last_name', { required: true })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            />
            {errors.last_name && <p className="text-red-500 text-sm">Last name is required</p>}
          </div>
          <div>
            <label className="block text-sm font-medium">Email</label>
            <input
              type="email"
              {...register('email', { required: true })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            />
            {errors.email && <p className="text-red-500 text-sm">Email is required</p>}
          </div>
          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              {...register('password', { required: true })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            />
            {errors.password && <p className="text-red-500 text-sm">Password is required</p>}
          </div>
          <div>
            <label className="block text-sm font-medium">Confirm Password</label>
            <input
              type="password"
              {...register('confirm_password', {
                required: true,
                validate: (value) => value === password || 'Passwords do not match',
              })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            />
            {errors.confirm_password && <p className="text-red-500 text-sm">{errors.confirm_password.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium">Role</label>
            <select
              {...register('role', { required: true })}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Role</option>
              <option value="Client">Client</option>
              <option value="Lawyer">Lawyer</option>
            </select>
            {errors.role && <p className="text-red-500 text-sm">Role is required</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-md transition"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm">
          Already have an account?{' '}
          <a href="/login" className="text-indigo-600 hover:underline">
            Login here
          </a>
        </p>
      </div>
    </div>
  );
}
