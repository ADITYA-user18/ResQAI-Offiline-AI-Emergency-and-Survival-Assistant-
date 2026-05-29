import React from 'react';
import { motion } from 'framer-motion';
import Navbar from '../components/layout/Navbar';
import useAuth from '../hooks/useAuth';
import {
  RiUserLine, RiShieldCheckLine, RiKeyLine,
  RiDeleteBinLine, RiInformationLine, RiTimeLine, RiCpuLine,
} from 'react-icons/ri';

const Profile = () => {
  const { user } = useAuth();

  const handleClear = () => {
    if (confirm('This will clear your credentials and log you out. Continue?')) {
      localStorage.clear();
      window.location.href = '/';
    }
  };

  const fields = [
    { label: 'Username',   value: user?.username },
    { label: 'Account ID', value: user?.user_id, truncate: true },
    { label: 'Device',     value: user?.device_id || 'web-browser' },
    { label: 'Created',    value: user?.created_at ? new Date(user.created_at).toLocaleString() : 'N/A' },
    { label: 'Last Login', value: user?.last_login ? new Date(user.last_login).toLocaleString() : 'N/A' },
  ];

  return (
    <div className="min-h-screen flex flex-col relative" style={{ background: 'var(--bg-page)' }}>
      <div className="absolute inset-0 cyber-grid opacity-20 pointer-events-none" />
      <div className="absolute top-[20%] right-[10%] w-[350px] h-[350px] rounded-full opacity-10" style={{ background: '#8B5CF6', filter: 'blur(100px)', pointerEvents: 'none' }} />
      <Navbar />

      <main className="flex-1 container-app py-10 relative z-10 max-w-4xl">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="pb-6 mb-8 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <h1 className="font-display font-bold text-3xl">My Profile</h1>
          <p className="text-sm mt-1 font-mono" style={{ color: 'var(--text-muted)' }}>Manage your offline account</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Account Details */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="md:col-span-2 glass rounded-2xl p-6 space-y-4">
            <h3 className="font-display font-semibold flex items-center gap-2">
              <RiUserLine className="w-5 h-5 text-[#00E5FF]" /> Account Details
            </h3>
            <div className="space-y-2">
              {fields.map((f, i) => (
                <div key={i} className="flex items-center justify-between py-2.5 border-b text-sm" style={{ borderColor: 'var(--border-color)' }}>
                  <span className="font-mono text-xs uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>{f.label}</span>
                  <span className={`font-medium ${f.truncate ? 'truncate max-w-[200px]' : ''}`} title={f.truncate ? f.value : undefined}>
                    {f.value}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right Column */}
          <div className="space-y-4">
            {/* Security */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              className="glass-cyan rounded-2xl p-5 space-y-3">
              <h3 className="font-display font-semibold flex items-center gap-2 text-sm">
                <RiKeyLine className="w-4 h-4 text-[#00E5FF]" /> Offline Security
              </h3>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                Your data is encrypted locally. No cloud sync is active.
              </p>
              <div className="flex items-start gap-2 p-3 rounded-xl text-xs font-mono" style={{ background: 'rgba(0,229,255,0.06)', color: 'var(--text-muted)' }}>
                <RiInformationLine className="w-4 h-4 text-[#00E5FF] shrink-0 mt-0.5" />
                No data ever leaves your device.
              </div>
            </motion.div>

            {/* Danger Zone */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="glass-emergency rounded-2xl p-5 space-y-3">
              <h3 className="font-display font-semibold flex items-center gap-2 text-sm text-[#FF3B3B]">
                <RiDeleteBinLine className="w-4 h-4" /> Danger Zone
              </h3>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Permanently erase credentials and log out.
              </p>
              <button onClick={handleClear}
                className="w-full py-2.5 rounded-xl border border-[#FF3B3B]/30 bg-[#FF3B3B]/8 text-[#FF3B3B] hover:bg-[#FF3B3B] hover:text-white text-xs font-mono font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2">
                <RiDeleteBinLine className="w-3.5 h-3.5" /> Delete Account Data
              </button>
            </motion.div>
          </div>
        </div>
      </main>

      <footer className="border-t py-4 text-center font-mono text-[10px] relative z-10" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
        ResQAI Local Assistant
      </footer>
    </div>
  );
};

export default Profile;
