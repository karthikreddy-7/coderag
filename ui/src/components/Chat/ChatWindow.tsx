import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAppStore } from '@/lib/store';
import { MessageList } from './MessageList';
import { MessageComposer } from './MessageComposer';
import { EmptyState } from './EmptyState';

export function ChatWindow() {
  const { 
    activeRepoId, 
    currentMessages, 
    repositories 
  } = useAppStore();
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [currentMessages]);

  const activeRepo = repositories.find(repo => repo.id === activeRepoId);
  const hasMessages = currentMessages.length > 0;

  if (!activeRepoId) {
    return (
      <div className="h-full bg-background flex items-center justify-center">
        <EmptyState 
          title="Select a repository"
          description="Choose a repository from the sidebar to start asking questions about your code"
          icon="repository"
        />
      </div>
    );
  }

  return (
    <div className="h-full bg-background flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 min-h-0 relative">
        <ScrollArea className="h-full" ref={scrollRef}>
          {hasMessages ? (
            <MessageList messages={currentMessages} />
          ) : (
            <div className="h-full flex items-center justify-center">
              <EmptyState 
                title="Start a conversation"
                description={`Ask questions about ${activeRepo?.name}. Try "What's the architecture?" or "Show me the authentication code"`}
                icon="chat"
              />
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Message Composer */}
      <div className="border-t border-border-light bg-surface">
        <MessageComposer />
      </div>
    </div>
  );
}