import { MessageSquare, GitBranch, Loader2, Code2 } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon: 'chat' | 'repository' | 'loading' | 'code';
}

export function EmptyState({ title, description, icon }: EmptyStateProps) {
  const getIcon = () => {
    switch (icon) {
      case 'chat':
        return <MessageSquare size={48} className="text-foreground-muted" />;
      case 'repository':
        return <GitBranch size={48} className="text-foreground-muted" />;
      case 'loading':
        return <Loader2 size={48} className="text-foreground-muted animate-spin" />;
      case 'code':
        return <Code2 size={48} className="text-foreground-muted" />;
      default:
        return <MessageSquare size={48} className="text-foreground-muted" />;
    }
  };

  const getSuggestedQuestions = () => {
    if (icon === 'chat') {
      return [
        "What's the overall architecture?",
        "Show me the authentication code",
        "How does the database layer work?",
        "Find the API endpoints",
        "Explain the main business logic"
      ];
    }
    return [];
  };

  const suggestions = getSuggestedQuestions();

  return (
    <div className="text-center max-w-md mx-auto p-8">
      {getIcon()}
      
      <h3 className="text-lg font-semibold text-foreground mt-4 mb-2">
        {title}
      </h3>
      
      <p className="text-foreground-secondary mb-6">
        {description}
      </p>

      {suggestions.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-foreground-secondary mb-3">
            Try asking:
          </p>
          <div className="space-y-2">
            {suggestions.map((question, index) => (
              <div 
                key={index}
                className="text-sm text-foreground-muted bg-surface border border-border-light rounded-lg px-3 py-2 hover:bg-muted cursor-pointer transition-colors"
              >
                "{question}"
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}