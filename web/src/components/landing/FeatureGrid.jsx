import React from 'react';
import { WifiOff, ShieldCheck, Database, Key } from 'lucide-react';

const FeatureGrid = () => {
  const points = [
    {
      title: "No Grid Needed",
      desc: "Full local vector index retrieval and LLM response generation on local loop. Zero internet requests.",
      icon: WifiOff
    },
    {
      title: "Encrypted SQLite",
      desc: "All conversation records, logins, and settings are saved completely locally to isolated user files.",
      icon: Database
    },
    {
      title: "Privacy Assured",
      desc: "No analytics or diagnostic telemetry is sent to any remote servers. Complete data security.",
      icon: ShieldCheck
    },
    {
      title: "bcrypt Signatures",
      desc: "Local passwords undergo cryptographic bcrypt hashing to protect local accounts from access.",
      icon: Key
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {points.map((pt, idx) => (
        <div key={idx} className="glass border border-white/5 p-5 rounded-xl space-y-3 hover:border-cyber-blue/20 transition-all">
          <div className="w-10 h-10 rounded-lg bg-cyber-blue/10 border border-cyber-blue/20 flex items-center justify-center">
            <pt.icon className="w-5 h-5 text-cyber-blue" />
          </div>
          <h4 className="font-display font-bold text-sm text-white">{pt.title}</h4>
          <p className="text-xs text-gray-400 leading-relaxed font-sans">{pt.desc}</p>
        </div>
      ))}
    </div>
  );
};

export default React.memo(FeatureGrid);
