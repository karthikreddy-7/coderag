import { useState } from 'react';
import { FileText, ExternalLink, Hash, Star, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ProvenanceItem } from '@/types/api';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';

interface ProvenanceListProps {
  provenance: ProvenanceItem[];
  compact?: boolean;
}

export function ProvenanceList({ provenance, compact = false }: ProvenanceListProps) {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const { setSelectedProvenance, activeRepoId } = useAppStore();

  const toggleExpanded = (chunkId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId);
    } else {
      newExpanded.add(chunkId);
    }
    setExpandedItems(newExpanded);
  };

  const handleViewFullFile = async (item: ProvenanceItem) => {
    if (!activeRepoId) return;

    try {
      const fullClass = await apiClient.fetchFullClass({
        repo_id: activeRepoId,
        path: item.path,
        start_line: item.start_line,
        end_line: item.end_line
      });

      setSelectedProvenance({
        originalProvenance: item,
        fullClass: fullClass
      });
    } catch (error) {
      console.error('Failed to fetch full file:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-success';
    if (score >= 0.7) return 'text-warning';
    return 'text-foreground-muted';
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 0.9) return 'bg-success/10 text-success border-success/20';
    if (score >= 0.7) return 'bg-warning/10 text-warning border-warning/20';
    return 'bg-muted text-foreground-muted border-border';
  };

  if (compact) {
    return (
      <div className="space-y-2">
        {provenance.map((item) => (
          <div 
            key={item.chunk_id}
            className="flex items-center justify-between p-2 bg-background rounded-lg border border-border-light"
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <FileText size={14} className="text-foreground-muted shrink-0" />
              <code className="text-xs font-mono text-foreground truncate">
                {item.path}:{item.start_line}-{item.end_line}
              </code>
            </div>
            <Badge variant="outline" className={`text-xs ml-2 ${getScoreBadgeColor(item.score)}`}>
              {Math.round(item.score * 100)}%
            </Badge>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-2">
        <FileText size={16} className="text-foreground-muted" />
        <span className="text-sm font-medium text-foreground">
          Source References ({provenance.length})
        </span>
      </div>

      {provenance.map((item) => {
        const isExpanded = expandedItems.has(item.chunk_id);
        
        return (
          <Card key={item.chunk_id} className="p-3 bg-surface border-border-light shadow-soft">
            <Collapsible>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  {/* File Path and Lines */}
                  <div className="flex items-center gap-2 mb-2">
                    <FileText size={14} className="text-foreground-muted shrink-0" />
                    <code className="text-sm font-mono text-foreground bg-muted px-1.5 py-0.5 rounded truncate">
                      {item.path}
                    </code>
                  </div>

                  {/* Metadata */}
                  <div className="flex items-center gap-3 text-xs text-foreground-muted mb-2">
                    <div className="flex items-center gap-1">
                      <Hash size={10} />
                      <span>Lines {item.start_line}-{item.end_line}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star size={10} className={getScoreColor(item.score)} />
                      <Badge variant="outline" className={`text-xs ${getScoreBadgeColor(item.score)}`}>
                        {Math.round(item.score * 100)}%
                      </Badge>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {item.commit_sha.slice(0, 7)}
                    </Badge>
                  </div>

                  {/* Code Snippet Preview */}
                  <CollapsibleTrigger asChild>
                    <Button 
                      variant="ghost" 
                      className="w-full justify-start p-0 h-auto hover:bg-transparent"
                      onClick={() => toggleExpanded(item.chunk_id)}
                    >
                      <div className="flex items-start gap-2 w-full">
                        <ChevronRight 
                          size={14} 
                          className={`text-foreground-muted shrink-0 mt-0.5 transition-transform ${
                            isExpanded ? 'rotate-90' : ''
                          }`} 
                        />
                        <code className="text-xs font-mono text-foreground-secondary bg-code-bg p-2 rounded border border-code-border flex-1 text-left truncate">
                          {item.snippet.split('\n')[0]}...
                        </code>
                      </div>
                    </Button>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="mt-2">
                    <pre className="text-xs font-mono text-foreground bg-code-bg p-3 rounded border border-code-border overflow-x-auto whitespace-pre-wrap">
                      {item.snippet}
                    </pre>
                  </CollapsibleContent>
                </div>

                {/* Actions */}
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleViewFullFile(item)}
                  className="shrink-0"
                >
                  <ExternalLink size={12} className="mr-1" />
                  View
                </Button>
              </div>
            </Collapsible>
          </Card>
        );
      })}
    </div>
  );
}