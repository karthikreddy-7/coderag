// API Types for CodeRAG Frontend

export interface Repository {
  id: string;
  name: string;
  url: string;
  status: 'queued' | 'ingesting' | 'ready' | 'error';
  last_ingest_sha?: string;
  created_at?: string;
  updated_at?: string;
}

export interface IngestJob {
  job_id: string;
  status: 'queued' | 'running' | 'done' | 'error';
  progress?: number;
  message?: string;
  started_at?: string;
  completed_at?: string;
  processed_files?: number;
  indexed_chunks?: number;
  error_message?: string;
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

export interface FullClassResponse {
  path: string;
  class_name: string;
  content: string;
  start_line: number;
  end_line: number;
  sha: string;
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
  type?: 'github' | 'gitlab' | 'upload';
}

export interface QueryRequest {
  repo_id: string;
  query: string;
  options?: {
    max_results?: number;
    include_tools?: boolean;
    stream?: boolean;
  };
}

export interface FetchFullClassRequest {
  repo_id: string;
  path: string;
  class_name?: string;
  start_line?: number;
  end_line?: number;
}