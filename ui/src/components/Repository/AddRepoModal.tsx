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
  const [branch, setBranch] = useState('');
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
        branch: branch.trim() || undefined
      });
      
      addRepository(result);
      setActiveRepo(result.id);
      
      toast({
        title: "Repository added successfully",
        description: `${result.name} is now being indexed`
      });
      
      // Reset form and close modal
      setRepoUrl('');
      setBranch('');
      onOpenChange(false);
      
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

  const getPlaceholder = () => {
    switch (activeTab) {
      case 'github':
        return 'e.g., https://github.com/facebook/react';
      case 'gitlab':
        return 'e.g., https://gitlab.com/gitlab-org/gitlab';
      default:
        return 'Repository URL';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg bg-surface border-border">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus size={20} className="text-accent" />
            Add Repository
          </DialogTitle>
          <DialogDescription>
            Connect a Git repository to start asking questions about your code.
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
            <TabsTrigger value="upload" className="flex items-center gap-2" disabled>
              <Upload size={16} />
              Upload
            </TabsTrigger>
          </TabsList>

          <TabsContent value="github" className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="github-url">Repository URL</Label>
                <Input
                  id="github-url"
                  type="text"
                  placeholder={getPlaceholder()}
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="github-branch">Branch (optional)</Label>
                <Input
                  id="github-branch"
                  type="text"
                  placeholder="main"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              
              <div className="flex justify-end gap-2 pt-2">
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

          <TabsContent value="gitlab" className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="gitlab-url">Repository URL</Label>
                <Input
                  id="gitlab-url"
                  type="text"
                  placeholder={getPlaceholder()}
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gitlab-branch">Branch (optional)</Label>
                <Input
                  id="gitlab-branch"
                  type="text"
                  placeholder="main"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  disabled={isLoading}
                  className="bg-background"
                />
              </div>
              
              <div className="flex justify-end gap-2 pt-2">
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

          <TabsContent value="upload" className="pt-4">
            <div className="text-center py-12 border-2 border-dashed border-border rounded-lg bg-background">
              <Upload size={32} className="text-foreground-muted mx-auto mb-3" />
              <h3 className="text-base font-medium text-foreground-muted">Upload functionality coming soon</h3>
              <p className="text-sm text-foreground-muted mt-1">
                Drag and drop a zip file or click to browse
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}