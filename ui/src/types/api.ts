// API Types for CodeRAG Frontend

export interface Repository {
  id: number;
  name: string;
  url: string;
  branch: string;
  last_indexed: string;
}

export interface ProvenanceItem {
  chunk_id: string;
  path: string;
  start_line: number;
  end_line: number;
  commit_sha: string;
  snippet: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  provenance: ProvenanceItem[];
  tools_used: string[];
  streaming?: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  provenance?: ProvenanceItem[];
  streaming?: boolean;
}

export interface ChatHistory {
  repo_id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

// API Request types
export interface CreateRepoRequest {
  url: string;
  branch?: string;
}

export interface QueryRequest {
  repo_id: number;
  query: string;
  options?: {
    max_results?: number;
    include_tools?: boolean;
    stream?: boolean;
  };
}
