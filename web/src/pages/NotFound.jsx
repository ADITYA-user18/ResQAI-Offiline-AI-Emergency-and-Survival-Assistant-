import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { RiShieldLine, RiArrowLeftLine } from 'react-icons/ri';

const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden" style={{ background: 'var(--bg-page)' }}>
    <div className="absolute w-[400px] h-[400px] rounded-full" style={{ background: '#FF3B3B', filter: 'blur(120px)', opacity: 0.1, top: '20%', left: '30%', pointerEvents: 'none' }} />
    <div className="absolute inset-0 cyber-grid opacity-20 pointer-events-none" />

    <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }} className="text-center relative z-10 max-w-lg">
      <motion.div animate={{ rotate: [0, -10, 10, -10, 0] }} transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        className="w-24 h-24 rounded-3xl glass-emergency flex items-center justify-center mx-auto mb-8">
        <RiShieldLine className="w-12 h-12 text-[#FF3B3B]" />
      </motion.div>
      <div className="font-display font-bold text-8xl gradient-text-warm mb-4">404</div>
      <h1 className="font-display font-bold text-2xl mb-3">Signal Lost</h1>
      <p className="mb-8" style={{ color: 'var(--text-secondary)' }}>
        The emergency channel you're looking for doesn't exist or has been decommissioned.
      </p>
      <Link to="/" className="btn-primary inline-flex items-center gap-2">
        <RiArrowLeftLine className="w-4 h-4" /> Return to Base
      </Link>
    </motion.div>
  </div>
);

export default NotFound;
