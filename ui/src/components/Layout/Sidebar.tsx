import { useState } from 'react';
import { Plus, Clock, MessageSquare, Trash2, Loader2, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAppStore } from '@/lib/store';
import { AddRepoModal } from '../Repository/AddRepoModal';
import { RepoBadge } from '../Repository/RepoBadge';

export function Sidebar() {
  const [showAddRepo, setShowAddRepo] = useState(false);
  const { 
    repositories, 
    activeRepoId, 
    setActiveRepo,
    chatHistory,
    clearMessages,
    currentMessages,
    isLoading
  } = useAppStore();

  const activeRepo = repositories.find(repo => repo.id === activeRepoId);
  const recentChats = chatHistory[activeRepoId || ''] || [];
  
  // Get unique conversation sessions based on first message timestamp
  const conversationSessions = recentChats.reduce((sessions: any[], message) => {
    if (message.role === 'user') {
      const sessionDate = new Date(message.timestamp).toDateString();
      const existingSession = sessions.find(s => s.date === sessionDate);
      
      if (existingSession) {
        existingSession.messages.push(message);
      } else {
        sessions.push({
          date: sessionDate,
          messages: [message],
          preview: message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
        });
      }
    }
    return sessions;
  }, []).slice(-5); // Keep last 5 sessions

  const renderRepoSelector = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center p-4">
          <Loader2 size={20} className="animate-spin text-foreground-muted" />
        </div>
      );
    }

    if (repositories.length === 0) {
      return (
        <div className="text-center p-4 border border-dashed border-border rounded-lg">
          <Github size={32} className="text-foreground-muted mx-auto mb-2" />
          <p className="text-sm font-medium">No repositories found</p>
          <p className="text-xs text-foreground-muted mb-3">Add a repository to get started</p>
          <Button size="sm" onClick={() => setShowAddRepo(true)}>
            <Plus size={16} className="mr-2" />
            Add Repository
          </Button>
        </div>
      );
    }

    return (
      <Select 
        value={activeRepoId?.toString() || ''} 
        onValueChange={(value) => setActiveRepo(parseInt(value, 10))}
      >
        <SelectTrigger className="w-full bg-background">
          <SelectValue placeholder="Select a repository..." />
        </SelectTrigger>
        <SelectContent className="bg-surface border border-border">
          {repositories.filter(repo => repo.id).map((repo) => (
            <SelectItem key={repo.id} value={repo.id.toString()} className="hover:bg-muted">
              <div className="flex items-center gap-2 w-full">
                <RepoBadge repo={repo} size="sm" />
                <span className="truncate">{repo.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  }

  return (
    <div className="h-full bg-surface border-r border-border-light flex flex-col">
      {/* Repository Selection */}
      <div className="p-4 border-b border-border-light">
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-foreground">Repository</label>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setShowAddRepo(true)}
              className="p-1 h-auto hover:bg-muted"
            >
              <Plus size={16} />
            </Button>
          </div>
          
          {renderRepoSelector()}
          
          {activeRepo && (
            <div className="pt-2">
              <RepoBadge repo={activeRepo} showDetails />
            </div>
          )}
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-4 border-b border-border-light">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Clock size={16} />
              Recent Conversations
            </h3>
            {currentMessages.length > 0 && (
              <Button 
                variant="ghost" 
                size="sm"
                onClick={clearMessages}
                className="p-1 h-auto hover:bg-muted text-foreground-muted hover:text-destructive"
              >
                <Trash2 size={14} />
              </Button>
            )}
          </div>
        </div>

        <ScrollArea className="flex-1 p-2">
          {activeRepoId ? (
            <div className="space-y-2">
              {conversationSessions.length > 0 ? (
                conversationSessions.map((session, index) => (
                  <div 
                    key={index}
                    className="p-3 rounded-lg bg-background hover:bg-muted cursor-pointer transition-colors border border-border-light"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare size={14} className="text-foreground-muted mt-0.5 shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-foreground truncate">
                          {session.preview}
                        </p>
                        <p className="text-xs text-foreground-muted mt-1">
                          {session.date}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <MessageSquare size={32} className="text-foreground-muted mx-auto mb-2" />
                  <p className="text-sm text-foreground-muted">No conversations yet</p>
                  <p className="text-xs text-foreground-muted mt-1">
                    Start asking questions about your code
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Clock size={32} className="text-foreground-muted mx-auto mb-2" />
              <p className="text-sm text-foreground-muted">Select a repository</p>
              <p className="text-xs text-foreground-muted mt-1">
                to view conversation history
              </p>
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Add Repository Modal */}
      <AddRepoModal 
        open={showAddRepo} 
        onOpenChange={setShowAddRepo} 
      />
    </div>
  );
}