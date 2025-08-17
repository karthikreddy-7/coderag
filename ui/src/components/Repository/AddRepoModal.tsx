import { useState } from 'react';
import { Github, GitlabIcon, Upload, Plus, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface AddRepoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddRepoModal({ open, onOpenChange }: AddRepoModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [activeTab, setActiveTab] = useState('github');
  
  const { addRepository, setActiveRepo } = useAppStore();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoUrl.trim()) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid repository URL",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    
    try {
      const result = await apiClient.createRepository({
        url: repoUrl.trim(),
        type: activeTab as 'github' | 'gitlab'
      });
      
      addRepository(result);
      setActiveRepo(result.id);
      
      toast({
        title: "Repository added successfully",
        description: `${result.name} is now being indexed`
      });
      
      // Reset form and close modal
      setRepoUrl('');
      onOpenChange(false);
      
      // Start polling for ingestion status if job_id is provided
      if (result.ingest_job_id) {
        pollIngestStatus(result.ingest_job_id, result.id);
      }
      
    } catch (error) {
      console.error('Failed to add repository:', error);
      toast({
        title: "Failed to add repository",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const pollIngestStatus = async (jobId: string, repoId: string) => {
    try {
      const status = await apiClient.getIngestStatus(jobId);
      
      if (status.status === 'done') {
        toast({
          title: "Repository indexed successfully",
          description: `Processed ${status.processed_files} files with ${status.indexed_chunks} chunks`
        });
      } else if (status.status === 'error') {
        toast({
          title: "Indexing failed",
          description: status.error_message || "Unknown error during indexing",
          variant: "destructive"
        });
      } else {
        // Continue polling
        setTimeout(() => pollIngestStatus(jobId, repoId), 2000);
      }
    } catch (error) {
      console.error('Failed to poll ingest status:', error);
    }
  };

  const getPlaceholder = () => {
    switch (activeTab) {
      case 'github':
        return 'https://github.com/username/repository';
      case 'gitlab':
        return 'https://gitlab.com/username/repository';
      default:
        return 'Repository URL';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-surface border-border">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus size={20} className="text-accent" />
            Add Repository
          </DialogTitle>
          <DialogDescription>
            Connect a Git repository to start asking questions about your code
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-background">
            <TabsTrigger value="github" className="flex items-center gap-2">
              <Github size={16} />
              GitHub
            </TabsTrigger>
            <TabsTrigger value="gitlab" className="flex items-center gap-2">
              <GitlabIcon size={16} />
              GitLab
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload size={16} />
              Upload
            </TabsTrigger>
          </TabsList>

          <TabsContent value="github" className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="github-url">Repository URL</Label>
                <Input
                  id="github-url"
                  type="url"
                  placeholder={getPlaceholder()}
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => onOpenChange(false)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading || !repoUrl.trim()}>
                  {isLoading ? (
                    <>
                      <Loader2 size={16} className="mr-2 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <Github size={16} className="mr-2" />
                      Add Repository
                    </>
                  )}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="gitlab" className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="gitlab-url">Repository URL</Label>
                <Input
                  id="gitlab-url"
                  type="url"
                  placeholder={getPlaceholder()}
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => onOpenChange(false)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading || !repoUrl.trim()}>
                  {isLoading ? (
                    <>
                      <Loader2 size={16} className="mr-2 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <GitlabIcon size={16} className="mr-2" />
                      Add Repository
                    </>
                  )}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="upload" className="space-y-4">
            <div className="text-center py-8 border-2 border-dashed border-border rounded-lg bg-background">
              <Upload size={32} className="text-foreground-muted mx-auto mb-2" />
              <p className="text-sm text-foreground-muted">Upload functionality coming soon</p>
              <p className="text-xs text-foreground-muted mt-1">
                Drag and drop a zip file or click to browse
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}