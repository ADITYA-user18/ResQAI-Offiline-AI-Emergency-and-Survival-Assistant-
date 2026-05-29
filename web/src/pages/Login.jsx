import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import useAuth from '../hooks/useAuth';
import { RiShieldFill, RiUserLine, RiLockLine, RiArrowRightLine, RiEyeLine, RiEyeOffLine } from 'react-icons/ri';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) { toast.error('Please fill in all fields.'); return; }
    setLoading(true);
    try {
      await login(username.trim(), password.trim());
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Login failed. Check your credentials.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden" style={{ background: 'var(--bg-page)' }}>
      {/* Orbs */}
      <div className="absolute w-[500px] h-[500px] rounded-full top-[-100px] left-[-150px] opacity-20" style={{ background: '#FF3B3B', filter: 'blur(100px)' }} />
      <div className="absolute w-[400px] h-[400px] rounded-full bottom-[-80px] right-[-100px] opacity-15" style={{ background: '#00E5FF', filter: 'blur(100px)' }} />
      <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Brand */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 group mb-5">
            <motion.div whileHover={{ scale: 1.1, rotate: 5 }} className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#00E5FF] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-[#00E5FF]/30">
              <RiShieldFill className="w-6 h-6 text-[#050816]" />
            </motion.div>
            <span className="font-display font-bold text-2xl">ResQ<span className="gradient-text-cyan">AI</span></span>
          </Link>
          <h1 className="font-display font-bold text-2xl mb-1">Welcome back</h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Sign in to your offline assistant</p>
        </div>

        {/* Card */}
        <div className="glass rounded-2xl p-8 shadow-2xl shadow-black/40 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#00E5FF]/40 to-transparent" />

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label className="block font-mono text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>Username</label>
              <div className="relative">
                <RiUserLine className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <input
                  type="text" required placeholder="your_username"
                  value={username} onChange={e => setUsername(e.target.value)} disabled={loading}
                  className="input-field !pl-10"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block font-mono text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>Password</label>
              <div className="relative">
                <RiLockLine className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <input
                  type={showPwd ? 'text' : 'password'} required placeholder="••••••••"
                  value={password} onChange={e => setPassword(e.target.value)} disabled={loading}
                  className="input-field !pl-10 !pr-10"
                />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors" style={{ color: 'var(--text-muted)' }}>
                  {showPwd ? <RiEyeOffLine className="w-4 h-4" /> : <RiEyeLine className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <motion.button
              type="submit" disabled={loading}
              whileTap={{ scale: 0.98 }} whileHover={{ scale: 1.01 }}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <><div className="w-4 h-4 rounded-full border-2 border-[#050816]/20 border-t-[#050816] animate-spin" />Verifying...</>
              ) : (
                <>Sign In <RiArrowRightLine className="w-4 h-4" /></>
              )}
            </motion.button>
          </form>

          <div className="mt-6 pt-6 border-t text-center text-sm" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
            No account?{' '}
            <Link to="/signup" className="text-[#00E5FF] hover:underline font-semibold">Create one free</Link>
          </div>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-xs font-mono transition-colors hover:text-[#00E5FF]" style={{ color: 'var(--text-muted)' }}>
            ← Back to Home
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
