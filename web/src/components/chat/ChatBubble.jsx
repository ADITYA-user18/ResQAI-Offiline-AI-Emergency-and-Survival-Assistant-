import React from 'react';
import { Shield, Cpu } from 'lucide-react';

const ChatBubble = ({ role, content, time, onParse }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-emergency-red/10 border border-emergency-red/20 flex items-center justify-center shrink-0">
          <Shield className="w-4 h-4 text-emergency-red" />
        </div>
      )}

      <div className={`
        max-w-[85%] rounded-xl p-4 border leading-relaxed font-sans text-sm
        ${isUser 
          ? 'bg-cyber-blue/5 border-cyber-blue/20 text-gray-100 rounded-tr-none' 
          : 'bg-terminal-bg border-white/5 text-gray-300 rounded-tl-none'
        }
      `}>
        {isUser ? (
          <div className="whitespace-pre-wrap">{content}</div>
        ) : (
          <div 
            className="space-y-2 prose prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: onParse(content) }}
          />
        )}
        
        <div className="flex items-center justify-between gap-4 mt-2 border-t border-white/5 pt-2 font-mono text-[9px] text-gray-500">
          <span>{isUser ? 'YOU' : 'RESQAI'}</span>
          <span>{time}</span>
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-cyber-blue/10 border border-cyber-blue/20 flex items-center justify-center shrink-0">
          <Cpu className="w-4 h-4 text-cyber-blue" />
        </div>
      )}
    </div>
  );
};

export default ChatBubble;
