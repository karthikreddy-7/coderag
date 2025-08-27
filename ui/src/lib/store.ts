import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Repository, Message, ChatHistory } from '@/types/api';

interface AppState {
  // Repository state
  repositories: Repository[];
  activeRepoId: number | null;
  isLoading: boolean;
  
  // Chat state
  chatHistory: Record<string, Message[]>;
  currentMessages: Message[];
  
  // UI state
  sidebarCollapsed: boolean;
  rightPanelCollapsed: boolean;
  selectedProvenance: any | null;
  
  // Actions
  setRepositories: (repos: Repository[]) => void;
  addRepository: (repo: Repository) => void;
  updateRepository: (id: number, updates: Partial<Repository>) => void;
  setActiveRepo: (id: number | null) => void;
  setLoading: (loading: boolean) => void;
  
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  loadChatHistory: (repoId: number) => void;
  
  setSidebarCollapsed: (collapsed: boolean) => void;
  setRightPanelCollapsed: (collapsed: boolean) => void;
  setSelectedProvenance: (provenance: any | null) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      repositories: [],
      activeRepoId: null,
      chatHistory: {},
      currentMessages: [],
      isLoading: false,
      sidebarCollapsed: false,
      rightPanelCollapsed: true,
      selectedProvenance: null,

      // Repository actions
      setRepositories: (repos) => set({ repositories: repos }),
      
      addRepository: (repo) => set((state) => ({
        repositories: [...state.repositories, repo]
      })),
      
      updateRepository: (id, updates) => set((state) => ({
        repositories: state.repositories.map(repo =>
          repo.id === id ? { ...repo, ...updates } : repo
        )
      })),
      
      setActiveRepo: (id) => {
        set({ activeRepoId: id });
        if (id) {
          get().loadChatHistory(id);
        } else {
          set({ currentMessages: [] });
        }
      },

      // Chat actions
      addMessage: (message) => set((state) => {
        const newMessages = [...state.currentMessages, message];
        const newHistory = {
          ...state.chatHistory,
          [state.activeRepoId || 'default']: newMessages
        };
        
        return {
          currentMessages: newMessages,
          chatHistory: newHistory
        };
      }),
      
      updateMessage: (id, updates) => set((state) => {
        const newMessages = state.currentMessages.map(msg =>
          msg.id === id ? { ...msg, ...updates } : msg
        );
        const newHistory = {
          ...state.chatHistory,
          [state.activeRepoId || 'default']: newMessages
        };
        
        return {
          currentMessages: newMessages,
          chatHistory: newHistory
        };
      }),
      
      clearMessages: () => set((state) => {
        const newHistory = {
          ...state.chatHistory,
          [state.activeRepoId || 'default']: []
        };
        
        return {
          currentMessages: [],
          chatHistory: newHistory
        };
      }),
      
      loadChatHistory: (repoId) => set((state) => ({
        currentMessages: state.chatHistory[repoId] || []
      })),

      // UI actions
      setLoading: (loading) => set({ isLoading: loading }),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setRightPanelCollapsed: (collapsed) => set({ rightPanelCollapsed: collapsed }),
      setSelectedProvenance: (provenance) => set({ 
        selectedProvenance: provenance,
        rightPanelCollapsed: provenance ? false : true
      }),
    }),
    {
      name: 'coderag-app-store',
      partialize: (state) => ({
        repositories: state.repositories,
        chatHistory: state.chatHistory,
        activeRepoId: state.activeRepoId,
        sidebarCollapsed: state.sidebarCollapsed,
        rightPanelCollapsed: state.rightPanelCollapsed,
      }),
    }
  )
);