import { 
  Repository, 
  QueryResponse, 
  CreateRepoRequest,
  QueryRequest
} from '@/types/api';

// Environment configuration
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// API Client class
export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE;
  }

  // Repository endpoints
  async getRepositories(): Promise<Repository[]> {
    const response = await fetch(`${this.baseUrl}/repos`);
    if (!response.ok) throw new Error('Failed to fetch repositories');
    const data = await response.json();
    return data.repos;
  }

  async createRepository(request: CreateRepoRequest): Promise<Repository> {
    const response = await fetch(`${this.baseUrl}/repos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_path: request.url,
        branch: request.branch
      })
    });
    
    if (!response.ok) throw new Error('Failed to create repository');
    return response.json();
  }

  // Query endpoint
  async query(request: QueryRequest): Promise<QueryResponse> {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) throw new Error('Failed to query repository');
    return response.json();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export individual functions for convenience
export const {
  getRepositories,
  createRepository,
  query,
} = apiClient;