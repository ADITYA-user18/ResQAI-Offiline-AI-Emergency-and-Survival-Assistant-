import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import useAuth from '../hooks/useAuth';
import {
  RiShieldFill, RiUserLine, RiLockLine, RiArrowRightLine,
  RiEyeLine, RiEyeOffLine, RiCpuLine,
} from 'react-icons/ri';

const Signup = () => {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const deviceId = `web-${Math.random().toString(36).substr(2, 9)}`;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const u = username.trim();
    if (u.length < 3 || u.length > 30) { toast.error('Username must be 3–30 characters.'); return; }
    if (!/^[a-zA-Z0-9_]+$/.test(u)) { toast.error('Only letters, numbers, underscores allowed.'); return; }
    if (password.length < 6) { toast.error('Password must be at least 6 characters.'); return; }
    if (password !== confirm) { toast.error('Passwords do not match.'); return; }
    setLoading(true);
    try {
      await signup(u, password, deviceId);
      toast.success('Account created! Welcome to ResQAI.');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Signup failed. Try again.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden" style={{ background: 'var(--bg-page)' }}>
      <div className="absolute w-[500px] h-[500px] rounded-full top-[-80px] right-[-150px] opacity-15" style={{ background: '#8B5CF6', filter: 'blur(100px)' }} />
      <div className="absolute w-[400px] h-[400px] rounded-full bottom-[-80px] left-[-100px] opacity-15" style={{ background: '#FF3B3B', filter: 'blur(100px)' }} />
      <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md my-8"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 group mb-5">
            <motion.div whileHover={{ scale: 1.1, rotate: 5 }} className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#FF3B3B] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-[#FF3B3B]/30">
              <RiShieldFill className="w-6 h-6 text-white" />
            </motion.div>
            <span className="font-display font-bold text-2xl">ResQ<span className="gradient-text-cyan">AI</span></span>
          </Link>
          <h1 className="font-display font-bold text-2xl mb-1">Create your account</h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Secure, offline, private — always.</p>
        </div>

        <div className="glass rounded-2xl p-8 shadow-2xl shadow-black/40 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#8B5CF6]/40 to-transparent" />

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block font-mono text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>Username</label>
              <div className="relative">
                <RiUserLine className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <input type="text" required placeholder="3-30 chars, a-z 0-9 _"
                  value={username} onChange={e => setUsername(e.target.value)} disabled={loading}
                  className="input-field !pl-10" />
              </div>
            </div>

            <div>
              <label className="block font-mono text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>Password</label>
              <div className="relative">
                <RiLockLine className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <input type={showPwd ? 'text' : 'password'} required placeholder="Min 6 characters"
                  value={password} onChange={e => setPassword(e.target.value)} disabled={loading}
                  className="input-field !pl-10 !pr-10" />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }}>
                  {showPwd ? <RiEyeOffLine className="w-4 h-4" /> : <RiEyeLine className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block font-mono text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>Confirm Password</label>
              <div className="relative">
                <RiLockLine className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <input type={showPwd ? 'text' : 'password'} required placeholder="Repeat password"
                  value={confirm} onChange={e => setConfirm(e.target.value)} disabled={loading}
                  className="input-field !pl-10" />
              </div>
            </div>

            {/* Device info */}
            <div className="px-3 py-2.5 rounded-xl border flex items-center gap-2 text-xs font-mono" style={{ background: 'rgba(0,229,255,0.04)', borderColor: 'rgba(0,229,255,0.15)', color: 'var(--text-muted)' }}>
              <RiCpuLine className="w-3.5 h-3.5 text-[#00E5FF]" />
              {deviceId}
            </div>

            <motion.button
              type="submit" disabled={loading}
              whileTap={{ scale: 0.98 }} whileHover={{ scale: 1.01 }}
              className="btn-emergency w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <><div className="w-4 h-4 rounded-full border-2 border-white/20 border-t-white animate-spin" />Creating account...</>
              ) : (
                <>Create Account <RiArrowRightLine className="w-4 h-4" /></>
              )}
            </motion.button>
          </form>

          <div className="mt-6 pt-6 border-t text-center text-sm" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
            Already have one?{' '}
            <Link to="/login" className="text-[#00E5FF] hover:underline font-semibold">Sign in</Link>
          </div>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-xs font-mono hover:text-[#00E5FF] transition-colors" style={{ color: 'var(--text-muted)' }}>← Back to Home</Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Signup;
