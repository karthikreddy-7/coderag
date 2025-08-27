import { useEffect } from 'react';
import { ChatWindow } from '@/components/Chat/ChatWindow';
import { EmptyState } from '@/components/Chat/EmptyState';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const { activeRepoId, setRepositories } = useAppStore();
  const { toast } = useToast();

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const repos = await apiClient.getRepositories();
        setRepositories(repos);
      } catch (error) {
        console.error('Failed to fetch repositories:', error);
        toast({
          title: "Failed to fetch repositories",
          description: error instanceof Error ? error.message : "Unknown error occurred",
          variant: "destructive"
        });
      }
    };

    fetchRepos();
  }, [setRepositories, toast]);

  return (
    <>
      {activeRepoId ? <ChatWindow /> : <EmptyState />}
    </>
  );
};

export default Index;