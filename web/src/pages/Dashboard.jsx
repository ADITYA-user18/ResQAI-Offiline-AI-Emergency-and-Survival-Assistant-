import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from '../components/layout/Navbar';
import useAuth from '../hooks/useAuth';
import useChat from '../hooks/useChat';
import {
  RiShieldFill, RiMessage3Line, RiAddLine, RiDeleteBinLine,
  RiHeartPulseLine, RiCompassDiscoverLine, RiScalesLine,
  RiTimeLine, RiArrowRightLine, RiWifiLine,
} from 'react-icons/ri';

const fadeUp = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };
const stagger = { show: { transition: { staggerChildren: 0.09 } } };

const Dashboard = () => {
  const { user } = useAuth();
  const { chats, loadingChats, systemHealth, startNewChat, removeChat, fetchSystemHealth, loadChat } = useChat();
  const navigate = useNavigate();
  const isOnline = systemHealth?.status === 'healthy';

  useEffect(() => { fetchSystemHealth(); }, [fetchSystemHealth]);

  const handleCreateChat = async (query = null, title = 'Emergency Console') => {
    const id = await startNewChat(title);
    if (id) {
      if (query) sessionStorage.setItem(`prefilled_${id}`, query);
      navigate('/chat');
    }
  };

  const handleOpenChat = async (chatId) => {
    await loadChat(chatId);
    navigate('/chat');
  };

  const quickActions = [
    { title: 'Snake Bite', query: 'Immediate first aid for a venomous snake bite?', icon: <RiHeartPulseLine className="w-6 h-6" />, color: '#FF3B3B' },
    { title: 'Water Filter', query: 'How to build a wilderness water filter?', icon: <RiCompassDiscoverLine className="w-6 h-6" />, color: '#22C55E' },
    { title: 'Good Samaritan', query: 'Legal rights under Good Samaritan laws?', icon: <RiScalesLine className="w-6 h-6" />, color: '#FF8A00' },
  ];

  return (
    <div className="min-h-screen flex flex-col relative" style={{ background: 'var(--bg-page)' }}>
      <div className="absolute inset-0 cyber-grid opacity-20 pointer-events-none" />
      <div className="absolute top-[30%] left-[15%] w-[400px] h-[400px] rounded-full opacity-10" style={{ background: '#00E5FF', filter: 'blur(120px)', pointerEvents: 'none' }} />
      <Navbar />

      <main className="flex-1 w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-12 lg:px-16 py-8 relative z-10 space-y-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <div>
            <h1 className="font-display font-bold text-3xl tracking-tight">
              Welcome, <span className="gradient-text-cyan">{user?.username}</span>
            </h1>
            <p className="text-sm font-mono mt-1" style={{ color: 'var(--text-muted)' }}>
              {isOnline ? '● AI engine online · ready for queries' : '○ AI engine offline · check Ollama'}
            </p>
          </div>
          <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
            onClick={() => handleCreateChat()}
            className="btn-emergency flex items-center gap-2 self-start md:self-auto">
            <RiAddLine className="w-4 h-4" /> New Chat
          </motion.button>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Quick Actions */}
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h2 className="font-display font-semibold text-sm uppercase tracking-widest mb-4" style={{ color: 'var(--text-muted)' }}>Quick Actions</h2>
              <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {quickActions.map((a, i) => (
                  <motion.button key={i} variants={fadeUp}
                    whileHover={{ scale: 1.03, translateY: -4 }} whileTap={{ scale: 0.97 }}
                    onClick={() => handleCreateChat(a.query, a.title)}
                    className="glass text-left p-5 rounded-2xl transition-all duration-300 group h-40 flex flex-col justify-between"
                    style={{ borderColor: `${a.color}25` }}
                  >
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: `${a.color}15`, color: a.color }}>
                      {a.icon}
                    </div>
                    <div>
                      <h4 className="font-display font-semibold text-sm mb-1 group-hover:text-[#00E5FF] transition-colors">{a.title}</h4>
                      <p className="text-[10px] font-mono line-clamp-2" style={{ color: 'var(--text-muted)' }}>{a.query}</p>
                    </div>
                  </motion.button>
                ))}
              </motion.div>
            </div>

            {/* Offline Info Banner */}
            <div className="glass-cyan rounded-2xl p-6 relative overflow-hidden">
              <div className="absolute right-4 top-4 opacity-5">
                <RiShieldFill className="w-20 h-20 text-[#00E5FF]" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <RiWifiLine className="w-4 h-4 text-[#00E5FF]" />
                <h3 className="font-display font-semibold">100% Offline AI</h3>
              </div>
              <p className="text-sm leading-relaxed max-w-md" style={{ color: 'var(--text-secondary)' }}>
                Your questions are processed entirely on this device. No data leaves your computer — ever.
              </p>
            </div>
          </div>

          {/* Recent Chats */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display font-semibold text-sm uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Recent Chats</h2>
              {chats.length > 0 && (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full" style={{ background: 'rgba(0,229,255,0.1)', color: '#00E5FF' }}>
                  {chats.length}
                </span>
              )}
            </div>

            <div className="glass rounded-2xl overflow-hidden p-2 max-h-[420px] overflow-y-auto space-y-1">
              {loadingChats ? (
                <div className="py-12 text-center space-y-3">
                  <div className="w-8 h-8 rounded-full border-2 border-[#00E5FF]/20 border-t-[#00E5FF] animate-spin mx-auto" />
                  <p className="text-xs font-mono animate-pulse" style={{ color: 'var(--text-muted)' }}>Loading chats...</p>
                </div>
              ) : chats.length === 0 ? (
                <div className="py-16 text-center px-4">
                  <RiMessage3Line className="w-10 h-10 mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
                  <p className="font-display font-semibold text-sm mb-1">No chats yet</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Start a session above</p>
                </div>
              ) : (
                chats.map(chat => (
                  <div key={chat.chat_id}
                    className="flex items-center justify-between p-3 rounded-xl transition-all group cursor-pointer hover:bg-white/5"
                    style={{ borderColor: 'transparent' }}
                  >
                    <button onClick={() => handleOpenChat(chat.chat_id)} className="flex-1 text-left min-w-0">
                      <h4 className="font-medium text-sm truncate group-hover:text-[#00E5FF] transition-colors">{chat.title}</h4>
                      <div className="flex items-center gap-1.5 mt-0.5 text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
                        <RiTimeLine className="w-3 h-3" />
                        {new Date(chat.updated_at).toLocaleString()}
                      </div>
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); if (confirm('Delete this chat?')) removeChat(chat.chat_id); }}
                      className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all hover:bg-[#FF3B3B]/10 hover:text-[#FF3B3B]"
                      style={{ color: 'var(--text-muted)' }}>
                      <RiDeleteBinLine className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t py-4 text-center font-mono text-[10px] relative z-10" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
        ResQAI Local Assistant · {isOnline ? '● Connected' : '○ Offline'}
      </footer>
    </div>
  );
};

export default Dashboard;
