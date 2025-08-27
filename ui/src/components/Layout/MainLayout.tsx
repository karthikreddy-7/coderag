import { useEffect, useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { Sidebar } from './Sidebar';
import { RightPanel } from './RightPanel';
import { Header } from './Header';
import { useIsMobile } from '@/hooks/use-mobile';
import { Drawer, DrawerContent, DrawerTrigger } from '@/components/ui/drawer';
import { Button } from '@/components/ui/button';
import { Menu } from 'lucide-react';

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { 
    sidebarCollapsed, 
    rightPanelCollapsed, 
    setRepositories,
    setLoading
  } = useAppStore();
  const isMobile = useIsMobile();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Load repositories on mount
  useEffect(() => {
    const loadRepositories = async () => {
      setLoading(true);
      try {
        const repos = await apiClient.getRepositories();
        setRepositories(repos);
      } catch (error) {
        console.error('Failed to load repositories:', error);
      } finally {
        setLoading(false);
      }
    };

    loadRepositories();
  }, [setRepositories, setLoading]);

  if (isMobile) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <Header>
          <Drawer open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
            <DrawerTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu />
              </Button>
            </DrawerTrigger>
            <DrawerContent>
              <div className="h-[80vh] overflow-y-auto">
                <Sidebar />
              </div>
            </DrawerContent>
          </Drawer>
        </Header>
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
        <PanelGroup direction="horizontal" className="flex-1">
          {/* Left Sidebar */}
          {!sidebarCollapsed && (
            <>
              <Panel defaultSize={25} minSize={20} maxSize={35}>
                <Sidebar />
              </Panel>
              <PanelResizeHandle className="w-1 bg-border-light hover:bg-border transition-colors" />
            </>
          )}

          {/* Main Chat Area */}
          <Panel defaultSize={sidebarCollapsed ? (rightPanelCollapsed ? 100 : 70) : (rightPanelCollapsed ? 75 : 50)}>
            {children}
          </Panel>

          {/* Right Panel */}
          {!rightPanelCollapsed && (
            <>
              <PanelResizeHandle className="w-1 bg-border-light hover:bg-border transition-colors" />
              <Panel defaultSize={25} minSize={20} maxSize={40}>
                <RightPanel />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
}