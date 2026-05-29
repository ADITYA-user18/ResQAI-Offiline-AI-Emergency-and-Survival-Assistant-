import React from 'react';

const Loader = ({ message = 'INITIALIZING SYSTEM SECURE LINK...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-4 border-cyber-blue/20 animate-pulse"></div>
        <div className="absolute inset-0 rounded-full border-4 border-t-cyber-blue animate-spin"></div>
      </div>
      <p className="font-mono text-xs text-cyber-blue text-glow-blue animate-pulse uppercase tracking-widest">
        {message}
      </p>
    </div>
  );
};

export default Loader;
