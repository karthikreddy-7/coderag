import { User, Bot, Clock, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Message } from '@/types/api';
import { ProvenanceList } from './ProvenanceList';
import ReactMarkdown from 'react-markdown';

interface MessageBubbleProps {
  message: Message;
  isLast: boolean;
}

export function MessageBubble({ message, isLast }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      {/* Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center shrink-0 mt-1">
          <Bot size={16} className="text-accent-foreground" />
        </div>
      )}

      {/* Message Content */}
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        {/* Message Header */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-foreground-muted font-medium">
            {isUser ? 'You' : 'CodeRAG'}
          </span>
          <div className="flex items-center gap-1 text-xs text-foreground-muted">
            <Clock size={10} />
            {timestamp}
          </div>
          {message.streaming && (
            <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
              Streaming...
            </Badge>
          )}
        </div>

        {/* Message Bubble */}
        <div 
          className={`rounded-lg px-4 py-3 ${
            isUser 
              ? 'bg-primary text-primary-foreground ml-8' 
              : 'bg-surface border border-border-light shadow-soft'
          }`}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </div>
          ) : (
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Provenance (only for assistant messages) */}
        {!isUser && message.provenance && message.provenance.length > 0 && (
          <div className="mt-3">
            <ProvenanceList provenance={message.provenance} />
          </div>
        )}

        {/* Actions (only for assistant messages) */}
        {!isUser && isLast && (
          <div className="flex items-center gap-2 mt-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-xs h-7 px-2 hover:bg-muted"
            >
              <RotateCcw size={12} className="mr-1" />
              Regenerate
            </Button>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 mt-1">
          <User size={16} className="text-primary-foreground" />
        </div>
      )}
    </div>
  );
}