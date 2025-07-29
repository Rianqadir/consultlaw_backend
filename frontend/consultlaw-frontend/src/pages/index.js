import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-gray-800">
      <h1 className="text-4xl font-bold mb-6">Welcome to ConsultLaw</h1>
      <div className="space-x-4">
        <Link href="/login" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Login</Link>
        <Link href="/register" className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900">Register</Link>
      </div>
    </main>
  );
}
