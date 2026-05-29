import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { gsap } from 'gsap';
import Navbar from '../components/layout/Navbar';
import {
  RiShieldFill, RiHeartPulseLine, RiCompassDiscoverLine,
  RiScalesLine, RiWifiOffLine, RiCheckboxCircleLine,
  RiArrowRightLine, RiFlashlightLine, RiLockLine,
} from 'react-icons/ri';

const fadeUp = { hidden: { opacity: 0, y: 30 }, show: { opacity: 1, y: 0 } };
const stagger = { show: { transition: { staggerChildren: 0.12 } } };

const Orb = ({ className, color, delay = 0 }) => (
  <div
    className={`glow-orb absolute ${className}`}
    style={{
      background: color,
      animationDelay: `${delay}s`,
      animationDuration: `${8 + delay}s`,
    }}
  />
);

const Home = () => {
  const heroRef  = useRef(null);
  const titleRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current, { opacity: 0, y: 60 }, {
        opacity: 1, y: 0, duration: 1.1, ease: 'power3.out', delay: 0.2,
      });
    }, heroRef);
    return () => ctx.revert();
  }, []);

  const features = [
    {
      icon: <RiHeartPulseLine className="w-7 h-7" />, color: '#FF3B3B',
      title: 'Trauma & First Aid',
      desc: 'Instant life-saving directives for cardiac arrest, severe bleeding, burns, fracture, and poison response.',
    },
    {
      icon: <RiCompassDiscoverLine className="w-7 h-7" />, color: '#22C55E',
      title: 'Wilderness Survival',
      desc: 'Critical guidance on water purification, shelter, wild foraging, signaling, and disaster kit construction.',
    },
    {
      icon: <RiScalesLine className="w-7 h-7" />, color: '#FF8A00',
      title: 'Legal Awareness',
      desc: 'Good Samaritan laws, evacuation rights, self-defense scope, and emergency legal requirements.',
    },
  ];

  const stats = [
    { val: '100%', label: 'Offline Capable', color: '#00E5FF' },
    { val: '<2s',  label: 'Response Time',   color: '#8B5CF6' },
    { val: 'Zero', label: 'Cloud Needed',    color: '#22C55E' },
    { val: 'AES',  label: 'Local Encrypted', color: '#FF8A00' },
  ];

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden" style={{ background: 'var(--bg-page)' }}>
      {/* Background Orbs */}
      <Orb className="w-[600px] h-[600px] top-[-100px] left-[-150px] opacity-30" color="#00E5FF" delay={0} />
      <Orb className="w-[500px] h-[500px] top-[20%] right-[-100px] opacity-20" color="#8B5CF6" delay={3} />
      <Orb className="w-[400px] h-[400px] bottom-[10%] left-[20%] opacity-15" color="#FF3B3B" delay={5} />
      <div className="absolute inset-0 cyber-grid opacity-40 pointer-events-none" />

      <Navbar />

      {/* ── HERO ─────────────────────────────────────── */}
      <section ref={heroRef} className="relative z-10 w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-12 lg:px-16 pt-12 pb-24 md:pt-20 md:pb-32 flex flex-col items-center text-center">

        {/* Status Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, type: 'spring' }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-emergency border mb-8 text-xs font-mono font-bold tracking-widest uppercase text-[#FF3B3B]"
        >
          <span className="w-2 h-2 rounded-full bg-[#FF3B3B] animate-pulse" />
          Emergency AI System — Offline Ready
        </motion.div>

        {/* Title */}
        <div ref={titleRef} className="opacity-0">
          <h1 className="font-display font-bold text-5xl sm:text-7xl md:text-8xl leading-[1.05] tracking-tight mb-6 max-w-5xl">
            Save Lives With{' '}
            <span className="gradient-text-hero">AI</span>
            {' '}When Grid{' '}
            <span className="gradient-text-warm">Fails.</span>
          </h1>
        </div>

        <motion.p
          variants={fadeUp} initial="hidden" animate="show"
          transition={{ delay: 0.6 }}
          className="font-sans text-lg sm:text-xl max-w-2xl mb-10 leading-relaxed"
          style={{ color: 'var(--text-secondary)' }}
        >
          ResQAI is a fully offline AI emergency assistant. First aid, survival, legal guidance — all powered locally. No internet. No cloud. No compromise.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={stagger} initial="hidden" animate="show"
          transition={{ delay: 0.8 }}
          className="flex flex-col sm:flex-row items-center gap-4 mb-20"
        >
          <motion.div variants={fadeUp}>
            <Link to="/signup" className="btn-emergency flex items-center gap-2 text-sm">
              <RiFlashlightLine className="w-4 h-4" />
              Start Emergency Assistant
            </Link>
          </motion.div>
          <motion.div variants={fadeUp}>
            <Link to="/login" className="btn-ghost flex items-center gap-2 text-sm">
              Sign In <RiArrowRightLine className="w-4 h-4" />
            </Link>
          </motion.div>
        </motion.div>

        {/* Terminal Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ delay: 1, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-3xl glass rounded-2xl overflow-hidden shadow-2xl shadow-black/50 terminal-scanlines border border-white/5"
        >
          <div className="bg-[#0B1120] px-5 py-3 border-b border-white/5 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#FF3B3B]" />
            <span className="w-3 h-3 rounded-full bg-[#FF8A00]" />
            <span className="w-3 h-3 rounded-full bg-[#22C55E]" />
            <span className="font-mono text-[10px] text-[color:var(--text-muted)] ml-2">resqai-core ~ offline-engine</span>
            <span className="ml-auto flex items-center gap-1 text-[10px] font-mono text-[#22C55E]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E] animate-pulse" />LIVE
            </span>
          </div>
          <div className="p-5 font-mono text-xs sm:text-sm space-y-2 text-left bg-gradient-to-b from-[#0B1120] to-[#050816]">
            <p style={{ color: 'var(--text-muted)' }}>// Semantic index loaded — 14,242 emergency vectors</p>
            <p className="text-[#00E5FF]">▲ [OK] FAISS index ready · phi3 model loaded · JWT auth active</p>
            <p style={{ color: 'var(--text-secondary)' }} className="mt-3">&gt; "What to do if someone is having a cardiac arrest?"</p>
            <div className="border-l-2 border-[#FF3B3B]/60 pl-3 py-1 space-y-1 text-[#F8FAFC]/90">
              <p className="text-[#FF3B3B] font-bold">ResQAI:</p>
              <p>1. Call emergency services immediately (112/911).</p>
              <p>2. Begin CPR — 30 chest compressions at 2 inches depth.</p>
              <p>3. Give 2 rescue breaths. Repeat until help arrives.</p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ── STATS ───────────────────────────────────── */}
      <section className="relative z-10 border-y py-12" style={{ borderColor: 'var(--border-color)', background: 'rgba(255,255,255,0.01)' }}>
        <div className="w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-12 lg:px-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {stats.map((s, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="font-display font-bold text-3xl sm:text-4xl mb-1" style={{ color: s.color, textShadow: `0 0 20px ${s.color}60` }}>
                  {s.val}
                </div>
                <div className="font-mono text-[11px] uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURE CARDS ───────────────────────────── */}
      <section id="features" className="relative z-10 w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-12 lg:px-16 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} className="text-center mb-16 w-full max-w-7xl mx-auto px-5 sm:px-8 md:px-12 lg:px-16"
        >
          <h2 className="font-display font-bold text-3xl sm:text-5xl mb-4">
            Three Emergency Cores
          </h2>
          <p className="max-w-xl mx-auto" style={{ color: 'var(--text-secondary)' }}>
            Our embedded RAG pipeline indexes peer-verified emergency knowledge across three critical domains.
          </p>
        </motion.div>

        <motion.div
          variants={stagger} initial="hidden" whileInView="show"
          viewport={{ once: true }} className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {features.map((f, i) => (
            <motion.div key={i} variants={fadeUp} className="feature-card group cursor-pointer">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-transform duration-300 group-hover:scale-110"
                style={{ background: `${f.color}18`, border: `1px solid ${f.color}35`, color: f.color }}
              >
                {f.icon}
              </div>
              <h3 className="font-display font-semibold text-xl mb-3">{f.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{f.desc}</p>
              <div className="mt-6 flex items-center gap-1.5 text-xs font-mono font-bold uppercase" style={{ color: f.color }}>
                View protocols <RiArrowRightLine className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ── WHY OFFLINE ─────────────────────────────── */}
      <section className="relative z-10 py-24 border-t" style={{ borderColor: 'var(--border-color)' }}>
        <div className="container-app grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#00E5FF] mb-4">
              <RiWifiOffLine /> Offline-First Principle
            </div>
            <h2 className="font-display font-bold text-3xl sm:text-5xl mb-6 leading-tight">
              Works when the grid goes dark.
            </h2>
            <p className="mb-8 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              Earthquakes, cellular blackouts, wilderness missions — when cloud AI fails, ResQAI keeps running. Semantic reasoning runs entirely on your local CPU/GPU.
            </p>
            <ul className="space-y-4">
              {['Local RAG Embedding — runs directly on your CPU', 'Zero telemetry — no data ever leaves your device', 'Deterministic retrieval — peer-verified emergency data'].map((t, i) => (
                <li key={i} className="flex items-start gap-3">
                  <RiCheckboxCircleLine className="w-5 h-5 text-[#22C55E] shrink-0 mt-0.5" />
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{t}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
            className="glass rounded-2xl p-6 space-y-4"
          >
            <h4 className="font-display font-semibold text-lg mb-2">Architecture Comparison</h4>
            {[
              { label: 'Cloud AI', sub: 'Needs internet · sends telemetry · fails in blackouts', bad: true },
              { label: 'ResQAI Local', sub: 'Embedded SQLite · FAISS vectors · local LLM · always on', bad: false },
            ].map((c, i) => (
              <div key={i} className={`p-4 rounded-xl flex items-center justify-between ${c.bad ? 'border border-[#FF3B3B]/20 bg-[#FF3B3B]/5' : 'glass-cyan'}`}>
                <div>
                  <h5 className={`font-semibold text-sm mb-1 ${c.bad ? 'text-[#FF3B3B]' : 'text-[#00E5FF]'}`}>{c.label}</h5>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{c.sub}</p>
                </div>
                <span className={`text-xs font-mono font-bold px-2 py-1 rounded border ${c.bad ? 'text-[#FF3B3B] border-[#FF3B3B]/30 bg-[#FF3B3B]/10' : 'text-[#22C55E] border-[#22C55E]/30 bg-[#22C55E]/10'}`}>
                  {c.bad ? 'FAILS' : '100% UP'}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────── */}
      <section className="relative z-10 py-24 border-t" style={{ borderColor: 'var(--border-color)' }}>
        <div className="w-full max-w-3xl mx-auto px-5 sm:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }} whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="w-20 h-20 rounded-3xl glass-emergency flex items-center justify-center mx-auto mb-8 animate-float"
          >
            <RiShieldFill className="w-10 h-10 text-[#FF3B3B]" />
          </motion.div>
          <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="font-display font-bold text-3xl sm:text-5xl mb-6"
          >
            Ready for Any Emergency.
          </motion.h2>
          <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
            className="mb-10 text-lg" style={{ color: 'var(--text-secondary)' }}
          >
            Set up your offline account in seconds. Your data stays on your device forever.
          </motion.p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-emergency flex items-center gap-2 w-full sm:w-auto justify-center">
              <RiLockLine /> Create Offline Account
            </Link>
            <Link to="/login" className="btn-ghost flex items-center gap-2 w-full sm:w-auto justify-center">
              Already have one? Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────── */}
      <footer className="relative z-10 border-t py-8" style={{ borderColor: 'var(--border-color)', background: 'rgba(0,0,0,0.3)' }}>
        <div className="container-app flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <RiShieldFill className="w-4 h-4 text-[#FF3B3B]" />
            <span className="font-display font-semibold text-sm">ResQ<span className="gradient-text-cyan">AI</span></span>
            <span className="text-xs font-mono ml-2" style={{ color: 'var(--text-muted)' }}>© 2026 · Local deployment</span>
          </div>
          <div className="flex gap-6 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            <Link to="/login" className="hover:text-[#00E5FF] transition-colors">Portal</Link>
            <Link to="/signup" className="hover:text-[#00E5FF] transition-colors">Register</Link>
            <a href="#features" className="hover:text-[#00E5FF] transition-colors">Features</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
