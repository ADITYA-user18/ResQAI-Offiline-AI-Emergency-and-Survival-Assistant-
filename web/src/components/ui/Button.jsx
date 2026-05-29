import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  type = 'button', 
  variant = 'primary', 
  disabled = false, 
  className = '' 
}) => {
  const baseStyle = "relative overflow-hidden font-mono text-xs font-bold uppercase tracking-wider transition-all duration-300 rounded-xl px-6 py-3 select-none flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:pointer-events-none";
  
  const variants = {
    primary: "bg-emergency-red text-white hover:bg-emergency-red-hover hover:shadow-lg hover:shadow-emergency-red/20",
    secondary: "border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-cyber-blue/30 hover:bg-cyber-blue/5",
    cyber: "bg-cyber-blue text-black hover:bg-cyber-blue/90 hover:shadow-lg hover:shadow-cyber-blue/30",
    danger: "bg-red-600/10 text-red-500 border border-red-500/20 hover:bg-red-600 hover:text-white hover:border-red-600",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></span>
      {children}
    </button>
  );
};

export default Button;
