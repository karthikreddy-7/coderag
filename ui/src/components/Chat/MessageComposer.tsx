import { useState, useRef, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { Message } from '@/types/api';

interface MessageComposerProps {
  disabled?: boolean;
}

export function MessageComposer({ disabled = false }: MessageComposerProps) {
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { 
    activeRepoId, 
    addMessage, 
    updateMessage,
    setLoading 
  } = useAppStore();

  const handleSubmit = async () => {
    if (!message.trim() || !activeRepoId || isSubmitting) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    };

    const assistantMessageId = `msg_${Date.now()}_assistant`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      streaming: true
    };

    // Add user message immediately
    addMessage(userMessage);
    
    // Add placeholder assistant message
    addMessage(assistantMessage);
    
    // Clear input
    setMessage('');
    setIsSubmitting(true);
    setLoading(true);

    try {
      const response = await apiClient.query({
        repo_id: activeRepoId,
        query: userMessage.content
      });

      // Update assistant message with response
      updateMessage(assistantMessageId, {
        content: response.answer,
        provenance: response.provenance,
        streaming: false
      });

    } catch (error) {
      console.error('Failed to send message:', error);
      
      updateMessage(assistantMessageId, {
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        streaming: false
      });
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  };

  return (
    <div className="p-4">
      <div className="flex gap-3 items-end">
        <div className="flex-1">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              adjustTextareaHeight();
            }}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled 
                ? "Repository is not ready for queries..." 
                : "Ask about the codebase... (press Enter to send)"
            }
            disabled={disabled || isSubmitting}
            className="min-h-[60px] max-h-[150px] resize-none bg-background border-border focus:ring-primary"
            rows={2}
          />
        </div>
        
        <Button 
          onClick={handleSubmit}
          disabled={!message.trim() || disabled || isSubmitting}
          size="lg"
          className="px-4 py-3 bg-primary hover:bg-primary-hover"
        >
          {isSubmitting ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </Button>
      </div>
      
      {disabled && (
        <p className="text-xs text-foreground-muted mt-2">
          Wait for repository indexing to complete before asking questions
        </p>
      )}
    </div>
  );
}