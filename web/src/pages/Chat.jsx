import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '../components/layout/Navbar';
import useAuth from '../hooks/useAuth';
import useChat from '../hooks/useChat';
import {
  RiSendPlane2Fill, RiAddLine, RiDeleteBinLine, RiMessage3Line,
  RiArrowLeftLine, RiMenuLine, RiCloseLine, RiShieldFill,
  RiUserLine, RiPencilLine,
} from 'react-icons/ri';

/* ── Markdown parser ─────────────────────────────────── */
const parseMarkdown = (text) => {
  if (!text) return '';
  let h = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  h = h.replace(/^### (.+)$/gm, '<p class="text-[11px] font-mono font-bold uppercase tracking-widest mt-3 mb-1" style="color:#00E5FF">$1</p>');
  h = h.replace(/^## (.+)$/gm,  '<p class="text-sm font-display font-bold mt-3 mb-1.5">$1</p>');
  h = h.replace(/^# (.+)$/gm,   '<p class="text-base font-display font-bold mt-4 mb-2 pb-1" style="border-bottom:1px solid var(--border-color)">$1</p>');
  h = h.replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--text-primary);font-weight:700">$1</strong>');
  h = h.replace(/^\s*[-*]\s+(.+)$/gm,
    '<div style="display:flex;gap:8px;margin:4px 0;align-items:flex-start">'
    + '<span style="color:#00E5FF;margin-top:2px;flex-shrink:0">▸</span>'
    + '<span style="color:var(--text-secondary);font-size:0.875rem;line-height:1.6">$1</span></div>'
  );
  h = h.replace(/^\d+\.\s+(.+)$/gm,
    '<div style="display:flex;gap:8px;margin:4px 0;align-items:flex-start">'
    + '<span style="color:#00E5FF;font-size:0.75rem;font-family:monospace;margin-top:3px;flex-shrink:0">●</span>'
    + '<span style="color:var(--text-secondary);font-size:0.875rem;line-height:1.6">$1</span></div>'
  );
  h = h.replace(/\n\n/g, '<div style="height:0.5rem"></div>');
  h = h.replace(/\n/g, '<br/>');
  return h;
};

const Chat = () => {
  const { user } = useAuth();
  const {
    chats, currentChatId, messages, loadingMessages, sendingMessage,
    loadChat, startNewChat, sendQuery, removeChat, renameChatSession
  } = useChat();
  const navigate  = useNavigate();
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  const [input, setInput]       = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [editingId, setEditingId]     = useState(null);
  const [editTitle, setEditTitle]     = useState('');

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, sendingMessage]);
  useEffect(() => {
    if (!currentChatId && chats.length > 0) loadChat(chats[0].chat_id);
  }, [chats, currentChatId, loadChat]);
  useEffect(() => {
    if (!currentChatId) return;
    const k = `prefilled_${currentChatId}`;
    const q = sessionStorage.getItem(k);
    if (q) { sessionStorage.removeItem(k); sendQuery(q); }
  }, [currentChatId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || sendingMessage) return;
    const q = input.trim();
    setInput('');
    await sendQuery(q);
  };

  const activeChat = chats.find(c => c.chat_id === currentChatId);

  const sampleQs = [
    'How to perform CPR on an adult?',
    'What should be in a disaster emergency kit?',
    'How to treat a deep wound in the field?',
  ];

  /* ── Sidebar content (shared for mobile & desktop) ── */
  const SidebarContent = () => (
    <div className="flex flex-col h-full" style={{ background: 'var(--bg-secondary)' }}>
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        <Link to="/dashboard"
          className="flex items-center gap-1.5 text-xs font-mono hover:text-[#00E5FF] transition-colors"
          style={{ color: 'var(--text-muted)' }}>
          <RiArrowLeftLine className="w-3.5 h-3.5" /> Dashboard
        </Link>
        <button onClick={() => setSidebarOpen(false)} className="md:hidden p-1.5 rounded-lg hover:bg-white/5" style={{ color: '#94A3B8' }}>
          <RiCloseLine className="w-4 h-4" />
        </button>
      </div>

      {/* New Chat button */}
      <div className="px-3 py-3">
        <button onClick={() => { startNewChat(); setSidebarOpen(false); }}
          className="w-full py-2.5 px-4 rounded-xl text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all"
          style={{
            background: 'rgba(0,229,255,0.08)',
            border: '1px solid rgba(0,229,255,0.25)',
            color: '#00E5FF',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,229,255,0.14)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(0,229,255,0.08)'}
        >
          <RiAddLine className="w-4 h-4" /> NEW CHAT
        </button>
      </div>

      {/* Chat list */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5 py-1">
        {chats.map(chat => {
          const isActive = chat.chat_id === currentChatId;
          return (
            <div key={chat.chat_id}
              className="group flex items-center gap-1 px-2 py-2.5 rounded-xl transition-all cursor-pointer"
              style={{
                background: isActive ? 'rgba(0,229,255,0.08)' : 'transparent',
                border: `1px solid ${isActive ? 'rgba(0,229,255,0.2)' : 'transparent'}`,
              }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; }}
              onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
            >
              <button onClick={() => { loadChat(chat.chat_id); setSidebarOpen(false); }} className="flex-1 text-left min-w-0">
                <div className="flex items-center gap-2">
                  <RiMessage3Line className="w-3.5 h-3.5 shrink-0" style={{ color: isActive ? '#00E5FF' : '#475569' }} />
                  {editingId === chat.chat_id ? (
                    <input autoFocus value={editTitle}
                      onChange={e => setEditTitle(e.target.value)}
                      onClick={e => e.stopPropagation()}
                      onKeyDown={e => {
                        if (e.key === 'Enter') { if (editTitle.trim()) renameChatSession(chat.chat_id, editTitle.trim()); setEditingId(null); }
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      onBlur={() => { if (editTitle.trim()) renameChatSession(chat.chat_id, editTitle.trim()); setEditingId(null); }}
                      className="w-full text-sm bg-transparent outline-none"
                      style={{ borderBottom: '1px solid rgba(0,229,255,0.4)', color: 'var(--text-primary)' }}
                    />
                  ) : (
                    <span className="text-sm font-medium truncate" style={{ color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                      {chat.title}
                    </span>
                  )}
                </div>
                <span className="block text-[9px] font-mono mt-0.5 ml-5.5" style={{ color: 'var(--text-muted)' }}>
                  {new Date(chat.updated_at).toLocaleDateString()}
                </span>
              </button>
              <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                <button onClick={e => { e.stopPropagation(); setEditingId(chat.chat_id); setEditTitle(chat.title); }}
                  className="p-1 rounded hover:text-[#00E5FF] transition-colors" style={{ color: 'var(--text-muted)' }}>
                  <RiPencilLine className="w-3 h-3" />
                </button>
                <button onClick={e => { e.stopPropagation(); if (confirm('Delete chat?')) removeChat(chat.chat_id); }}
                  className="p-1 rounded hover:text-[#FF3B3B] transition-colors" style={{ color: 'var(--text-muted)' }}>
                  <RiDeleteBinLine className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Sidebar footer */}
      <div className="px-4 py-3 border-t text-[9px] font-mono space-y-0.5"
        style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
        <div>ENCRYPTED SESSION</div>
        <div style={{ color: '#22C55E' }}>● AI ENGINE: READY</div>
      </div>
    </div>
  );

  return (
    <div className="h-screen flex flex-col" style={{ background: 'var(--bg-page)', color: 'var(--text-primary)' }}>
      <Navbar />

      <div className="flex-1 flex overflow-hidden relative">

        {/* Mobile hamburger */}
        <motion.button whileTap={{ scale: 0.9 }}
          onClick={() => setSidebarOpen(true)}
          className="md:hidden absolute top-3 left-3 z-40 p-2.5 rounded-xl"
          style={{ background: 'rgba(0,229,255,0.08)', border: '1px solid rgba(0,229,255,0.2)', color: '#00E5FF' }}>
          <RiMenuLine className="w-5 h-5" />
        </motion.button>

        {/* ── DESKTOP SIDEBAR ── */}
        <aside className="hidden md:flex flex-col w-64 border-r shrink-0" style={{ borderColor: 'var(--border-color)' }}>
          <SidebarContent />
        </aside>

        {/* ── MOBILE DRAWER ── */}
        <AnimatePresence>
          {sidebarOpen && (
            <>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                onClick={() => setSidebarOpen(false)}
                className="fixed inset-0 z-40 md:hidden" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }} />
              <motion.div initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
                transition={{ type: 'spring', stiffness: 300, damping: 35 }}
                className="fixed left-0 top-0 bottom-0 z-50 w-72 md:hidden border-r"
                style={{ borderColor: 'var(--border-color)' }}>
                <SidebarContent />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* ── MAIN CHAT PANEL ── */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

          {/* Chat header */}
          <div className="px-5 py-3.5 border-b flex items-center gap-3 flex-shrink-0"
            style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)', backdropFilter: 'blur(10px)' }}>
            <div className="pl-12 md:pl-0">
              <h2 className="font-display font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                {activeChat?.title || 'Emergency Assistant'}
              </h2>
              <div className="flex items-center gap-1.5 text-[10px] font-mono mt-0.5" style={{ color: 'var(--text-muted)' }}>
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#22C55E' }} />
                SECURE · OFFLINE · PRIVATE
              </div>
            </div>
          </div>

          {/* ── MESSAGES ── */}
          <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6" style={{ scrollbarGutter: 'stable' }}>
            {loadingMessages ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="w-10 h-10 rounded-full animate-spin mx-auto"
                    style={{ border: '2px solid rgba(0,229,255,0.1)', borderTopColor: '#00E5FF' }} />
                  <p className="text-xs font-mono animate-pulse" style={{ color: 'var(--text-muted)' }}>Loading...</p>
                </div>
              </div>

            ) : messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-lg mx-auto gap-6">
                <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: 'spring' }}
                  className="w-20 h-20 rounded-3xl flex items-center justify-center"
                  style={{ background: 'rgba(0,229,255,0.08)', border: '1px solid rgba(0,229,255,0.2)' }}>
                  <RiShieldFill className="w-10 h-10" style={{ color: '#00E5FF' }} />
                </motion.div>
                <div>
                  <h3 className="font-display font-bold text-xl mb-2" style={{ color: 'var(--text-primary)' }}>Offline Emergency Assistant</h3>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                    Ask anything about first aid, wilderness survival, or emergency situations. I respond instantly and entirely offline.
                  </p>
                </div>
                <div className="w-full space-y-2">
                  {sampleQs.map((q, i) => (
                    <button key={i} onClick={() => sendQuery(q)}
                      className="w-full text-left px-4 py-3 rounded-xl text-sm transition-all"
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-secondary)',
                        fontFamily: 'JetBrains Mono, monospace',
                        fontSize: '0.75rem',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'rgba(0,229,255,0.3)';
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-color)';
                        e.currentTarget.style.color = 'var(--text-secondary)';
                      }}
                    >
                      "{q}"
                    </button>
                  ))}
                </div>
              </div>

            ) : (
              <div className="space-y-5 max-w-3xl mx-auto w-full">
                <AnimatePresence initial={false}>
                  {messages.map(msg => (
                    <motion.div key={msg.message_id}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ type: 'spring', stiffness: 350, damping: 35 }}
                      className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {/* AI avatar */}
                      {msg.role !== 'user' && (
                        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-1"
                          style={{ background: 'rgba(255,59,59,0.12)', border: '1px solid rgba(255,59,59,0.25)' }}>
                          <RiShieldFill className="w-4 h-4" style={{ color: '#FF3B3B' }} />
                        </div>
                      )}

                      {/* ── BUBBLE ── */}
                      <div
                        className="text-sm leading-relaxed"
                        style={{
                          maxWidth: '78%',
                          borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                          padding: '12px 16px',
                          background: msg.role === 'user'
                            ? 'var(--glow-cyan)'
                            : 'var(--bg-elevated)',
                          border: msg.role === 'user'
                            ? '1px solid var(--border-accent)'
                            : '1px solid var(--border-color)',
                          color: msg.role === 'user' ? 'var(--text-primary)' : 'var(--text-secondary)',
                          backdropFilter: 'blur(10px)',
                        }}
                      >
                        {msg.role === 'user' ? (
                          <div className="break-words" style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{msg.content}</div>
                        ) : msg.content === '' ? (
                          /* Typing indicator */
                          <div className="flex items-center gap-3 py-1">
                            <div className="w-4 h-4 rounded-full animate-spin shrink-0"
                              style={{ border: '2px solid rgba(0,229,255,0.2)', borderTopColor: '#00E5FF' }} />
                            <div className="flex gap-1.5">
                              {[0, 0.18, 0.36].map((d, i) => (
                                <span key={i} className="w-1.5 h-1.5 rounded-full"
                                  style={{ background: '#00E5FF', animation: `typing-dot 1.4s ease-in-out ${d}s infinite` }} />
                              ))}
                            </div>
                          </div>
                        ) : (
                          /* AI markdown response */
                          <div className="break-words" style={{ overflowWrap: 'anywhere' }} dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
                        )}

                        {/* Timestamp footer */}
                        <div className="flex items-center justify-between gap-4 mt-2.5 pt-2"
                          style={{ borderTop: '1px solid var(--border-color)', fontSize: '9px', fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-muted)' }}>
                          <span>{msg.role === 'user' ? 'YOU' : 'RESQAI'}</span>
                          <span>{new Date(msg.created_at).toLocaleTimeString()}</span>
                        </div>
                      </div>

                      {/* User avatar */}
                      {msg.role === 'user' && (
                        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-1"
                          style={{ background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.2)' }}>
                          <RiUserLine className="w-4 h-4" style={{ color: '#00E5FF' }} />
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          {/* ── INPUT BAR ── */}
          <div className="flex-shrink-0 px-4 sm:px-8 py-4 border-t"
            style={{ borderColor: 'var(--border-color)', background: 'var(--bg-secondary)', backdropFilter: 'blur(20px)' }}>
            <form onSubmit={handleSend} className="max-w-3xl mx-auto">
              <div className="flex items-center gap-3 p-2 rounded-2xl"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-accent)',
                  boxShadow: '0 0 30px rgba(0,229,255,0.05), inset 0 1px 0 rgba(255,255,255,0.04)',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                }}
                onFocusCapture={e => {
                  e.currentTarget.style.borderColor = 'rgba(0,229,255,0.45)';
                  e.currentTarget.style.boxShadow = '0 0 30px rgba(0,229,255,0.12), inset 0 1px 0 rgba(255,255,255,0.04)';
                }}
                onBlurCapture={e => {
                  e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
                  e.currentTarget.style.boxShadow = '0 0 30px rgba(0,229,255,0.05), inset 0 1px 0 rgba(255,255,255,0.04)';
                }}
              >
                <input
                  ref={inputRef} type="text" value={input}
                  onChange={e => setInput(e.target.value)}
                  disabled={sendingMessage || loadingMessages}
                  placeholder="Ask emergency instructions..."
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--text-primary)',
                    fontSize: '0.875rem',
                    fontFamily: 'Inter, sans-serif',
                    padding: '10px 8px',
                  }}
                />
                <motion.button type="submit"
                  disabled={!input.trim() || sendingMessage}
                  whileHover={{ scale: 1.06 }}
                  whileTap={{ scale: 0.93 }}
                  style={{
                    width: '44px', height: '44px',
                    borderRadius: '14px',
                    background: input.trim() && !sendingMessage
                      ? 'linear-gradient(135deg, #00E5FF, #38BDF8)'
                      : 'rgba(0,229,255,0.15)',
                    border: 'none',
                    cursor: input.trim() && !sendingMessage ? 'pointer' : 'not-allowed',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                    boxShadow: input.trim() ? '0 0 20px rgba(0,229,255,0.35)' : 'none',
                    transition: 'all 0.25s ease',
                  }}
                >
                  <RiSendPlane2Fill className="w-4 h-4" style={{ color: input.trim() && !sendingMessage ? '#050816' : '#00E5FF' }} />
                </motion.button>
              </div>
              <p className="text-center font-mono mt-2" style={{ fontSize: '9px', color: '#334155' }}>
                ResQAI · Offline AI · Your data never leaves this device
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
