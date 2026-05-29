import React from 'react';

const GlowEffect = ({ color = 'blue', size = 'md', className = '' }) => {
  const colors = {
    blue: 'bg-cyber-blue/10 blur-[100px]',
    red: 'bg-emergency-red/5 blur-[120px]',
    green: 'bg-survival-green/5 blur-[100px]',
    gold: 'bg-legal-gold/5 blur-[80px]',
  };

  const sizes = {
    sm: 'w-64 h-64',
    md: 'w-96 h-96',
    lg: 'w-[500px] h-[500px]',
  };

  return (
    <div 
      className={`absolute rounded-full pointer-events-none ${colors[color]} ${sizes[size]} ${className}`}
    />
  );
};

export default GlowEffect;
