import { X, ExternalLink, Copy, FileText, Hash } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useAppStore } from '@/lib/store';
import { CodeViewer } from '../Code/CodeViewer';
import { ProvenanceList } from '../Chat/ProvenanceList';
import { useToast } from '@/hooks/use-toast';

export function RightPanel() {
  const { 
    selectedProvenance, 
    setSelectedProvenance,
    setRightPanelCollapsed 
  } = useAppStore();
  const { toast } = useToast();

  const handleClose = () => {
    setSelectedProvenance(null);
    setRightPanelCollapsed(true);
  };

  const handleCopyPath = () => {
    if (selectedProvenance?.fullClass?.path) {
      navigator.clipboard.writeText(selectedProvenance.fullClass.path);
      toast({
        title: "Copied to clipboard",
        description: "File path copied successfully"
      });
    }
  };

  if (!selectedProvenance) {
    return (
      <div className="h-full bg-surface border-l border-border-light flex flex-col">
        <div className="p-4 border-b border-border-light flex items-center justify-between">
          <h3 className="font-medium text-foreground">Code Viewer</h3>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={handleClose}
            className="p-1 h-auto hover:bg-muted"
          >
            <X size={16} />
          </Button>
        </div>
        
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <FileText size={48} className="text-foreground-muted mx-auto mb-4" />
            <h4 className="font-medium text-foreground mb-2">No file selected</h4>
            <p className="text-sm text-foreground-muted">
              Click on a code reference in the chat to view the full file
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-surface border-l border-border-light flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border-light">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-foreground">Code Viewer</h3>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={handleClose}
            className="p-1 h-auto hover:bg-muted"
          >
            <X size={16} />
          </Button>
        </div>

        {/* File Info */}
        {selectedProvenance.fullClass && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <FileText size={16} className="text-foreground-muted" />
              <code className="text-sm font-mono text-foreground bg-muted px-1.5 py-0.5 rounded">
                {selectedProvenance.fullClass.path}
              </code>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleCopyPath}
                className="p-1 h-auto hover:bg-muted"
              >
                <Copy size={12} />
              </Button>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-foreground-muted">
              <div className="flex items-center gap-1">
                <Hash size={12} />
                <span>Lines {selectedProvenance.fullClass.start_line}-{selectedProvenance.fullClass.end_line}</span>
              </div>
              <Badge variant="secondary" className="text-xs">
                {selectedProvenance.fullClass.sha?.slice(0, 7)}
              </Badge>
            </div>
          </div>
        )}
      </div>

      <ScrollArea className="flex-1">
        {/* Provenance Context */}
        {selectedProvenance.originalProvenance && (
          <div className="p-4 border-b border-border-light bg-accent-light">
            <h4 className="text-sm font-medium text-foreground mb-2">Context</h4>
            <ProvenanceList 
              provenance={[selectedProvenance.originalProvenance]} 
              compact 
            />
          </div>
        )}

        {/* Code Content */}
        {selectedProvenance.fullClass ? (
          <div className="p-4">
            <CodeViewer 
              code={selectedProvenance.fullClass.content}
              language="python"
              filename={selectedProvenance.fullClass.path}
              highlightLines={selectedProvenance.originalProvenance ? {
                start: selectedProvenance.originalProvenance.start_line,
                end: selectedProvenance.originalProvenance.end_line
              } : undefined}
            />
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="animate-pulse">
              <div className="h-4 bg-muted rounded mb-2" />
              <div className="h-4 bg-muted rounded mb-2 w-3/4" />
              <div className="h-4 bg-muted rounded mb-2 w-1/2" />
            </div>
            <p className="text-sm text-foreground-muted mt-4">Loading code...</p>
          </div>
        )}
      </ScrollArea>

      {/* Actions */}
      <div className="p-4 border-t border-border-light">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full"
          disabled={!selectedProvenance.fullClass}
        >
          <ExternalLink size={16} className="mr-2" />
          Open in Repository
        </Button>
      </div>
    </div>
  );
}