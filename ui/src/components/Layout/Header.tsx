import { Menu, X, Code2, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/lib/store';

export function Header() {
  const { 
    sidebarCollapsed, 
    setSidebarCollapsed,
    activeRepoId,
    repositories 
  } = useAppStore();

  const activeRepo = repositories.find(repo => repo.id === activeRepoId);

  return (
    <header className="h-14 border-b border-border-light bg-surface flex items-center px-4 shadow-soft">
      <div className="flex items-center gap-4">
        {/* Sidebar Toggle */}
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="p-2 hover:bg-muted"
        >
          {sidebarCollapsed ? <Menu size={18} /> : <X size={18} />}
        </Button>

        {/* App Title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Code2 size={20} className="text-accent" />
            <h1 className="text-lg font-semibold text-foreground">CodeRAG</h1>
          </div>
          
          <div className="h-4 w-px bg-border" />
          
          <span className="text-sm text-foreground-secondary">
            Ask your repository
          </span>
        </div>
      </div>

      <div className="flex-1" />

      {/* Active Repository Indicator */}
      {activeRepo && (
        <div className="flex items-center gap-2 mr-4">
          <div className={`w-2 h-2 rounded-full ${
            activeRepo.status === 'ready' ? 'bg-success' :
            activeRepo.status === 'ingesting' ? 'bg-warning animate-pulse-soft' :
            activeRepo.status === 'error' ? 'bg-destructive' :
            'bg-foreground-muted'
          }`} />
          <span className="text-sm text-foreground-secondary font-medium">
            {activeRepo.name}
          </span>
        </div>
      )}

      {/* Settings */}
      <Button variant="ghost" size="sm" className="p-2 hover:bg-muted">
        <Settings size={18} />
      </Button>
    </header>
  );
}