import { useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useAppStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import { Sidebar } from './Sidebar';
import { ChatWindow } from '../Chat/ChatWindow';
import { RightPanel } from './RightPanel';
import { Header } from './Header';

export function MainLayout() {
  const { 
    sidebarCollapsed, 
    rightPanelCollapsed, 
    setRepositories,
    repositories 
  } = useAppStore();

  // Load repositories on mount
  useEffect(() => {
    const loadRepositories = async () => {
      try {
        const repos = await apiClient.getRepositories();
        setRepositories(repos);
      } catch (error) {
        console.error('Failed to load repositories:', error);
      }
    };

    loadRepositories();
  }, [setRepositories]);

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
            <ChatWindow />
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