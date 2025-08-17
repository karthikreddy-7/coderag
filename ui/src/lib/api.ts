import { 
  Repository, 
  IngestJob, 
  QueryResponse, 
  FullClassResponse,
  CreateRepoRequest,
  QueryRequest,
  FetchFullClassRequest 
} from '@/types/api';

// Environment configuration
const API_BASE = import.meta.env.VITE_API_BASE || '';
const USE_MOCK = !API_BASE;

// Mock data and functions
let mockRepos: Repository[] = [
  {
    id: 'repo_1',
    name: 'my-awesome-project',
    url: 'https://github.com/user/my-awesome-project',
    status: 'ready',
    last_ingest_sha: 'abc123',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 'repo_2', 
    name: 'backend-service',
    url: 'https://github.com/user/backend-service',
    status: 'ingesting',
    created_at: '2024-01-16T14:20:00Z'
  }
];

let mockJobId = 'job_42';
let mockJobProgress = 0;

// Mock responses
const mockQueryResponse: QueryResponse = {
  answer: "You can find the UserService in `src/services/user_service.py`. It's a core service class that handles user authentication and profile management. The class is instantiated in `main.py` and used throughout the application for user-related operations.",
  provenance: [
    {
      chunk_id: 'c1',
      path: 'src/services/user_service.py',
      start_line: 10,
      end_line: 120,
      commit_sha: 'abc123',
      snippet: 'class UserService:\n    """Core service for user management"""\n    \n    def __init__(self, db_connection):\n        self.db = db_connection\n        self.cache = UserCache()\n    \n    def authenticate_user(self, email, password):\n        """Authenticate user with email and password"""\n        user = self.db.get_user_by_email(email)\n        if user and self.verify_password(password, user.password_hash):\n            return self.generate_session_token(user)',
      score: 0.95
    },
    {
      chunk_id: 'c2', 
      path: 'main.py',
      start_line: 25,
      end_line: 35,
      commit_sha: 'abc123',
      snippet: 'from src.services.user_service import UserService\n\n# Initialize services\ndb = DatabaseConnection()\nuser_service = UserService(db)\nauth_middleware = AuthMiddleware(user_service)\n\napp = FastAPI()\napp.add_middleware(AuthMiddleware)',
      score: 0.87
    },
    {
      chunk_id: 'c3',
      path: 'src/api/routes/users.py', 
      start_line: 1,
      end_line: 20,
      commit_sha: 'abc123',
      snippet: 'from fastapi import APIRouter, Depends\nfrom src.services.user_service import UserService\n\nrouter = APIRouter(prefix="/api/users")\n\n@router.post("/login")\nasync def login(credentials: LoginRequest, user_service: UserService = Depends()):\n    """User login endpoint"""\n    result = user_service.authenticate_user(credentials.email, credentials.password)\n    if result:\n        return {"token": result.token, "user": result.user}\n    raise HTTPException(status_code=401, detail="Invalid credentials")',
      score: 0.82
    }
  ],
  tools_used: ['semantic_search', 'code_parser']
};

// Utility functions
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function mockFetch<T>(data: T, delayMs: number = 300): Promise<T> {
  await delay(delayMs);
  return data;
}

// API Client class
export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE;
  }

  // Repository endpoints
  async getRepositories(): Promise<Repository[]> {
    if (USE_MOCK) {
      return mockFetch(mockRepos);
    }
    
    const response = await fetch(`${this.baseUrl}/repos`);
    if (!response.ok) throw new Error('Failed to fetch repositories');
    return response.json();
  }

  async createRepository(request: CreateRepoRequest): Promise<Repository & { ingest_job_id?: string }> {
    if (USE_MOCK) {
      const newRepo: Repository = {
        id: `repo_${Date.now()}`,
        name: request.url.split('/').pop() || 'new-repo',
        url: request.url,
        status: 'queued',
        created_at: new Date().toISOString()
      };
      
      mockRepos.push(newRepo);
      
      return mockFetch({
        ...newRepo,
        ingest_job_id: mockJobId
      }, 500);
    }

    const response = await fetch(`${this.baseUrl}/repos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) throw new Error('Failed to create repository');
    return response.json();
  }

  async triggerIngest(repoId: string): Promise<IngestJob> {
    if (USE_MOCK) {
      mockJobProgress = 0;
      return mockFetch({
        job_id: mockJobId,
        status: 'running',
        started_at: new Date().toISOString(),
        progress: 0,
        message: 'Starting ingestion...'
      });
    }

    const response = await fetch(`${this.baseUrl}/repos/${repoId}/ingest`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to trigger ingestion');
    return response.json();
  }

  async getIngestStatus(jobId: string): Promise<IngestJob> {
    if (USE_MOCK) {
      // Simulate progress
      mockJobProgress = Math.min(mockJobProgress + Math.random() * 20, 100);
      
      if (mockJobProgress >= 100) {
        return mockFetch({
          job_id: jobId,
          status: 'done',
          progress: 100,
          message: 'Ingestion completed successfully',
          started_at: new Date(Date.now() - 30000).toISOString(),
          completed_at: new Date().toISOString(),
          processed_files: 123,
          indexed_chunks: 456
        });
      }
      
      return mockFetch({
        job_id: jobId,
        status: 'running',
        progress: Math.round(mockJobProgress),
        message: mockJobProgress < 30 ? 'Parsing files...' :
                mockJobProgress < 70 ? 'Analyzing code structure...' :
                'Building search index...',
        started_at: new Date(Date.now() - 15000).toISOString()
      });
    }

    const response = await fetch(`${this.baseUrl}/ingest/${jobId}`);
    if (!response.ok) throw new Error('Failed to get ingestion status');
    return response.json();
  }

  // Query endpoint
  async query(request: QueryRequest): Promise<QueryResponse> {
    if (USE_MOCK) {
      // Simulate different responses based on query content
      const query = request.query.toLowerCase();
      let response = { ...mockQueryResponse };
      
      if (query.includes('auth') || query.includes('login')) {
        response.answer = "Authentication is handled by the AuthService class in `src/auth/auth_service.py`. It integrates with JWT tokens and supports multiple authentication providers.";
        response.provenance = [
          {
            chunk_id: 'c_auth_1',
            path: 'src/auth/auth_service.py',
            start_line: 1,
            end_line: 50,
            commit_sha: 'def456',
            snippet: 'class AuthService:\n    """Authentication service with JWT support"""\n    \n    def __init__(self, secret_key: str):\n        self.secret_key = secret_key\n        self.jwt_algorithm = "HS256"\n    \n    def create_access_token(self, user_id: str, expires_delta: timedelta = None):\n        """Create JWT access token for user"""\n        to_encode = {"sub": user_id, "iat": datetime.utcnow()}\n        if expires_delta:\n            expire = datetime.utcnow() + expires_delta\n            to_encode.update({"exp": expire})\n        return jwt.encode(to_encode, self.secret_key, algorithm=self.jwt_algorithm)',
            score: 0.93
          }
        ];
      } else if (query.includes('database') || query.includes('db')) {
        response.answer = "Database operations are centralized in the DatabaseManager class located in `src/db/database.py`. It provides connection pooling, transaction management, and ORM-like functionality.";
      }
      
      return mockFetch(response, 800);
    }

    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) throw new Error('Failed to query repository');
    return response.json();
  }

  // Tools endpoint  
  async fetchFullClass(request: FetchFullClassRequest): Promise<FullClassResponse> {
    if (USE_MOCK) {
      const mockCode = `class UserService:
    """Core service for user management and authentication"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.cache = UserCache()
        self.logger = logging.getLogger(__name__)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            user = self.db.get_user_by_email(email)
            if user and self.verify_password(password, user.password_hash):
                self.logger.info(f"User {email} authenticated successfully")
                return user
            return None
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user account"""
        password_hash = self.hash_password(password)
        user = User(email=email, password_hash=password_hash, name=name)
        return self.db.save_user(user)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def hash_password(self, password: str) -> str:
        """Hash password for storage"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile data"""
        return self.cache.get_or_fetch(f"profile:{user_id}", 
                                     lambda: self.db.get_user_profile(user_id))
    
    def update_user_profile(self, user_id: str, updates: dict) -> UserProfile:
        """Update user profile"""
        profile = self.db.update_user_profile(user_id, updates)
        self.cache.invalidate(f"profile:{user_id}")
        return profile`;

      return mockFetch({
        path: request.path,
        class_name: request.class_name || 'UserService',
        content: mockCode,
        start_line: 1,
        end_line: 55,
        sha: 'abc123'
      }, 400);
    }

    const response = await fetch(`${this.baseUrl}/tools/fetch_full_class`, {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) throw new Error('Failed to fetch full class');
    return response.json();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export individual functions for convenience
export const {
  getRepositories,
  createRepository,
  triggerIngest,
  getIngestStatus,
  query,
  fetchFullClass
} = apiClient;