import { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../stores/authStore';
import api from '../lib/api';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const setAuth = useAuthStore((state) => state.setAuth);
  
  const [role, setRole] = useState<'student' | 'recruiter'>(
    (searchParams.get('role') as 'student' | 'recruiter') || 'student'
  );
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await api.post('/auth/register', { name, email, password, role });
      
      const tokenRes = await api.post('/auth/login', { email, password });
      const token = tokenRes.data.access_token;
      
      localStorage.setItem('auth_token', token);
      
      const userRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const user = userRes.data;
      
      setAuth(user, token);
      
      if (user.role === 'admin' || user.role === 'recruiter') {
        navigate('/admin/candidates');
      } else {
        navigate('/upload');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cream p-4">
      <Link to="/" className="absolute top-8 left-8 text-text-secondary hover:text-text-primary font-semibold flex items-center gap-2">
        &larr; Back to home
      </Link>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-surface p-8 rounded-2xl shadow-xl border border-border"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-display font-bold text-text-primary mb-2">Create Account</h1>
          <p className="text-text-secondary">Join RViewer AI today</p>
        </div>

        {/* Role Selector */}
        <div className="flex p-1 bg-cream rounded-lg mb-8 border border-border">
          <button
            type="button"
            onClick={() => setRole('student')}
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-colors ${
              role === 'student' ? 'bg-white text-text-primary shadow-sm' : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            I'm a Candidate
          </button>
          <button
            type="button"
            onClick={() => setRole('recruiter')}
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-colors ${
              role === 'recruiter' ? 'bg-white text-text-primary shadow-sm' : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            I'm a Recruiter
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger-soft border border-danger text-danger rounded-xl text-sm font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-text-primary mb-1.5">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors bg-white text-text-primary"
              placeholder="John Doe"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-text-primary mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors bg-white text-text-primary"
              placeholder="you@example.com"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-text-primary mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors bg-white text-text-primary"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent hover:bg-accent/90 text-white py-3 rounded-xl font-bold text-lg transition-colors disabled:opacity-70 flex justify-center items-center shadow-md hover:shadow-lg"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="text-center mt-6 text-text-secondary text-sm font-medium">
          Already have an account?{' '}
          <Link to="/login" className="text-accent font-bold hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
