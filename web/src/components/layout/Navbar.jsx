import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import useAuth from '../../hooks/useAuth';
import useChat from '../../hooks/useChat';
import useTheme from '../../hooks/useTheme';
import {
  RiShieldFill,
  RiDashboardLine,
  RiMessage3Line,
  RiUserLine,
  RiLogoutBoxLine,
  RiSunLine,
  RiMoonLine,
  RiMenuLine,
  RiCloseLine,
  RiWifiLine,
  RiWifiOffLine,
} from 'react-icons/ri';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const { systemHealth } = useChat();
  const { theme, toggleTheme, isDark } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [scrolled, setScrolled]   = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const isOnline = systemHealth?.status === 'healthy';
  const isActive = (path) => location.pathname === path;

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navLinks = isAuthenticated
    ? [
        { to: '/dashboard', label: 'Dashboard', icon: <RiDashboardLine /> },
        { to: '/chat',      label: 'Chat',       icon: <RiMessage3Line /> },
      ]
    : [{ to: '/#features', label: 'Features', icon: null }];

  return (
    <>
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 inset-x-0 z-50 transition-all duration-500 ${
          scrolled
            ? 'glass border-b border-white/5 shadow-2xl shadow-black/30'
            : 'bg-transparent border-b border-transparent'
        }`}
      >
        <div className="w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-10 lg:px-14">
          <div className="flex items-center justify-between h-16">

            {/* LOGO */}
            <Link to="/" className="flex items-center gap-2.5 group flex-shrink-0">
              <div className="relative">
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: 'spring', stiffness: 300 }}
                  className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#00E5FF] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-[#00E5FF]/30"
                >
                  <RiShieldFill className="w-4 h-4 text-[#050816]" />
                </motion.div>
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#22C55E] border-2 border-[#050816] animate-pulse" />
              </div>
              <span className="font-display font-bold text-xl tracking-tight">
                ResQ<span className="gradient-text-cyan">AI</span>
              </span>
            </Link>

            {/* DESKTOP NAV */}
            <div className="hidden md:flex items-center gap-1">
              <Link
                to="/"
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive('/') ? 'text-[#00E5FF] bg-[#00E5FF]/10' : 'text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] hover:bg-white/5'
                }`}
              >
                Home
              </Link>
              {navLinks.map(link => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive(link.to) ? 'text-[#00E5FF] bg-[#00E5FF]/10' : 'text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] hover:bg-white/5'
                  }`}
                >
                  {link.icon}
                  {link.label}
                </Link>
              ))}
            </div>

            {/* RIGHT CONTROLS */}
            <div className="flex items-center gap-2 md:gap-3">

              {/* AI Status Badge */}
              <div className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono font-semibold border transition-all ${
                isOnline
                  ? 'border-[#22C55E]/30 bg-[#22C55E]/10 text-[#22C55E]'
                  : 'border-[#FF8A00]/30 bg-[#FF8A00]/10 text-[#FF8A00]'
              }`}>
                {isOnline
                  ? <RiWifiLine className="w-3.5 h-3.5" />
                  : <RiWifiOffLine className="w-3.5 h-3.5 animate-pulse" />
                }
                <span>{isOnline ? 'AI ONLINE' : 'OFFLINE'}</span>
              </div>

              {/* Theme Toggle */}
              <button
                type="button"
                onClick={toggleTheme}
                aria-label="Toggle theme"
                style={{
                  position: 'relative',
                  width: '52px',
                  height: '28px',
                  borderRadius: '999px',
                  border: '1px solid rgba(0,229,255,0.3)',
                  background: 'rgba(0,229,255,0.08)',
                  cursor: 'pointer',
                  flexShrink: 0,
                  outline: 'none',
                  padding: 0,
                  transition: 'border-color 0.3s',
                }}
              >
                <motion.div
                  animate={{ x: isDark ? 3 : 25 }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                  style={{
                    position: 'absolute',
                    top: '4px',
                    left: 0,
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: isDark
                      ? 'linear-gradient(135deg, #00E5FF, #38BDF8)'
                      : 'linear-gradient(135deg, #FF8A00, #FF3B3B)',
                    boxShadow: isDark
                      ? '0 0 10px rgba(0,229,255,0.6)'
                      : '0 0 10px rgba(255,138,0,0.6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    pointerEvents: 'none',
                  }}
                >
                  {isDark
                    ? <RiMoonLine style={{ width: '10px', height: '10px', color: '#050816' }} />
                    : <RiSunLine  style={{ width: '10px', height: '10px', color: '#fff' }} />
                  }
                </motion.div>
              </button>

              {/* User Actions */}
              {isAuthenticated ? (
                <div className="hidden md:flex items-center gap-2">
                  <Link
                    to="/profile"
                    className={`p-2 rounded-xl border transition-all duration-200 ${
                      isActive('/profile')
                        ? 'border-[#00E5FF]/40 bg-[#00E5FF]/10 text-[#00E5FF]'
                        : 'border-white/5 text-[color:var(--text-secondary)] hover:border-[#00E5FF]/30 hover:text-[#00E5FF] hover:bg-[#00E5FF]/5'
                    }`}
                    title="Profile"
                  >
                    <RiUserLine className="w-4 h-4" />
                  </Link>
                  <motion.button
                    whileTap={{ scale: 0.9 }}
                    onClick={handleLogout}
                    className="p-2 rounded-xl border border-white/5 text-[color:var(--text-secondary)] hover:border-[#FF3B3B]/40 hover:text-[#FF3B3B] hover:bg-[#FF3B3B]/5 transition-all duration-200"
                    title="Sign Out"
                  >
                    <RiLogoutBoxLine className="w-4 h-4" />
                  </motion.button>
                </div>
              ) : (
                <div className="hidden md:flex items-center gap-2">
                  <Link to="/login" className="btn-ghost text-sm px-4 py-2">Login</Link>
                  <Link to="/signup" className="btn-emergency text-xs px-4 py-2">Get Started</Link>
                </div>
              )}

              {/* Mobile Hamburger */}
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => setMobileOpen(o => !o)}
                className="md:hidden p-2 rounded-xl border border-white/5 text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] hover:bg-white/5 transition-all"
              >
                {mobileOpen ? <RiCloseLine className="w-5 h-5" /> : <RiMenuLine className="w-5 h-5" />}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* MOBILE DRAWER */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
            />
            <motion.div
              initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 280, damping: 30 }}
              className="fixed right-0 top-0 bottom-0 z-50 w-72 glass border-l border-white/5 flex flex-col md:hidden overflow-y-auto"
            >
              {/* Drawer header */}
              <div className="flex items-center justify-between p-5 border-b border-white/5">
                <span className="font-display font-bold text-lg">ResQ<span className="gradient-text-cyan">AI</span></span>
                <button onClick={() => setMobileOpen(false)} className="p-2 rounded-xl hover:bg-white/5">
                  <RiCloseLine className="w-5 h-5" />
                </button>
              </div>

              {/* Links */}
              <div className="flex-1 p-4 space-y-1">
                {[{ to: '/', label: 'Home' }, ...navLinks].map(link => (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      isActive(link.to) ? 'bg-[#00E5FF]/10 text-[#00E5FF]' : 'text-[color:var(--text-secondary)] hover:bg-white/5 hover:text-[color:var(--text-primary)]'
                    }`}
                  >
                    {link.icon}
                    {link.label}
                  </Link>
                ))}

                {isAuthenticated && (
                  <>
                    <Link to="/profile" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-[color:var(--text-secondary)] hover:bg-white/5 hover:text-[color:var(--text-primary)] transition-all">
                      <RiUserLine /> Profile
                    </Link>
                    <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-[#FF3B3B] hover:bg-[#FF3B3B]/5 transition-all">
                      <RiLogoutBoxLine /> Sign Out
                    </button>
                  </>
                )}
              </div>

              {/* Bottom section */}
              {!isAuthenticated && (
                <div className="p-4 border-t border-white/5 space-y-2">
                  <Link to="/login" className="block text-center btn-ghost text-sm py-2.5 w-full">Login</Link>
                  <Link to="/signup" className="block text-center btn-emergency text-sm py-2.5 w-full">Get Started</Link>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Spacer for fixed navbar */}
      <div className="h-16 md:h-18" />
    </>
  );
};

export default Navbar;
