import { GitBranch } from 'lucide-react';
import { Repository } from '@/types/api';

interface RepoBadgeProps {
  repo: Repository;
  size?: 'sm' | 'md';
  showDetails?: boolean;
}

export function RepoBadge({ repo, showDetails = false }: RepoBadgeProps) {
  if (showDetails) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <GitBranch size={14} className="text-foreground-muted" />
          <span className="text-sm font-medium text-foreground">{repo.name}</span>
        </div>
        
        {repo.branch && (
          <div className="text-xs text-foreground-muted font-mono">
            {repo.branch}
          </div>
        )}
        
        {repo.last_indexed && (
          <div className="text-xs text-foreground-muted">
            Indexed {new Date(repo.last_indexed).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      <GitBranch size={12} className="text-foreground-muted" />
      <span className="text-sm text-foreground-secondary">{repo.name}</span>
    </div>
  );
}