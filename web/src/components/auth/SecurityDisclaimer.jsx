import React from 'react';
import { ShieldCheck } from 'lucide-react';

const SecurityDisclaimer = () => {
  return (
    <div className="p-4 rounded-xl border border-white/5 bg-white/2 flex items-start gap-3">
      <ShieldCheck className="w-5 h-5 text-survival-green shrink-0 mt-0.5" />
      <div className="space-y-1">
        <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
          Local Security Protocol
        </h4>
        <p className="text-[11px] text-gray-400 leading-normal">
          All passwords are encrypted on this device using bcrypt hash calculations. No credentials data leaves this node.
        </p>
      </div>
    </div>
  );
};

export default SecurityDisclaimer;
