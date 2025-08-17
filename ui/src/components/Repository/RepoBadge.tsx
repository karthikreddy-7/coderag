import { GitBranch, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Repository } from '@/types/api';

interface RepoBadgeProps {
  repo: Repository;
  size?: 'sm' | 'md';
  showDetails?: boolean;
}

export function RepoBadge({ repo, size = 'md', showDetails = false }: RepoBadgeProps) {
  const getStatusIcon = () => {
    switch (repo.status) {
      case 'ready':
        return <CheckCircle size={12} className="text-success" />;
      case 'ingesting':
        return <Loader2 size={12} className="text-warning animate-spin" />;
      case 'error':
        return <AlertCircle size={12} className="text-destructive" />;
      default:
        return <Clock size={12} className="text-foreground-muted" />;
    }
  };

  const getStatusText = () => {
    switch (repo.status) {
      case 'ready':
        return 'Ready';
      case 'ingesting':
        return 'Indexing...';
      case 'error':
        return 'Error';
      case 'queued':
        return 'Queued';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = () => {
    switch (repo.status) {
      case 'ready':
        return 'bg-success/10 text-success border-success/20';
      case 'ingesting':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'error':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      default:
        return 'bg-muted text-foreground-muted border-border';
    }
  };

  if (showDetails) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <GitBranch size={14} className="text-foreground-muted" />
          <span className="text-sm font-medium text-foreground">{repo.name}</span>
        </div>
        
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <Badge 
            variant="outline" 
            className={`text-xs ${getStatusColor()}`}
          >
            {getStatusText()}
          </Badge>
        </div>
        
        {repo.last_ingest_sha && (
          <div className="text-xs text-foreground-muted font-mono">
            {repo.last_ingest_sha.slice(0, 7)}
          </div>
        )}
        
        {repo.updated_at && (
          <div className="text-xs text-foreground-muted">
            Updated {new Date(repo.updated_at).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      {getStatusIcon()}
      {size === 'md' && (
        <span className="text-sm text-foreground-secondary">{getStatusText()}</span>
      )}
    </div>
  );
}