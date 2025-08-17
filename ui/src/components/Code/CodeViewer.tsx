import { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-bash';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

interface CodeViewerProps {
  code: string;
  language: string;
  filename?: string;
  highlightLines?: {
    start: number;
    end: number;
  };
}

export function CodeViewer({ code, language, filename, highlightLines }: CodeViewerProps) {
  const codeRef = useRef<HTMLElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code, language]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  const getLanguageDisplayName = (lang: string) => {
    const langMap: Record<string, string> = {
      python: 'Python',
      javascript: 'JavaScript',
      typescript: 'TypeScript',
      jsx: 'JSX',
      tsx: 'TSX',
      java: 'Java',
      csharp: 'C#',
      go: 'Go',
      rust: 'Rust',
      json: 'JSON',
      yaml: 'YAML',
      bash: 'Bash'
    };
    return langMap[lang] || lang.toUpperCase();
  };

  const normalizedLanguage = language.toLowerCase();
  const prismLanguage = normalizedLanguage === 'py' ? 'python' : 
                       normalizedLanguage === 'js' ? 'javascript' :
                       normalizedLanguage === 'ts' ? 'typescript' :
                       normalizedLanguage;

  // Split code into lines for highlighting
  const lines = code.split('\n');
  const shouldHighlight = highlightLines && highlightLines.start && highlightLines.end;

  return (
    <div className="bg-code-bg border border-code-border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-code-border bg-surface">
        <div className="flex items-center gap-2">
          {filename && (
            <span className="text-sm font-mono text-foreground">{filename}</span>
          )}
          <span className="text-xs text-foreground-muted bg-muted px-2 py-1 rounded">
            {getLanguageDisplayName(prismLanguage)}
          </span>
          {shouldHighlight && (
            <span className="text-xs text-accent bg-accent-light px-2 py-1 rounded">
              Lines {highlightLines.start}-{highlightLines.end}
            </span>
          )}
        </div>
        
        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleCopy}
          className="p-2 h-auto hover:bg-muted"
        >
          {copied ? (
            <Check size={14} className="text-success" />
          ) : (
            <Copy size={14} />
          )}
        </Button>
      </div>

      {/* Code Content */}
      <div className="relative">
        <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
          <code 
            ref={codeRef}
            className={`language-${prismLanguage}`}
            style={{
              background: 'transparent',
              fontFamily: 'JetBrains Mono, Fira Code, Monaco, monospace'
            }}
          >
            {shouldHighlight ? (
              lines.map((line, index) => {
                const lineNumber = index + 1;
                const isHighlighted = lineNumber >= highlightLines.start && lineNumber <= highlightLines.end;
                
                return (
                  <div 
                    key={index}
                    className={`${isHighlighted ? 'bg-accent-light border-l-2 border-accent -ml-4 pl-4' : ''}`}
                    style={{ position: 'relative' }}
                  >
                    {line}
                    {index < lines.length - 1 && '\n'}
                  </div>
                );
              })
            ) : (
              code
            )}
          </code>
        </pre>

        {/* Line numbers */}
        <div className="absolute left-0 top-0 p-4 text-xs text-foreground-muted font-mono select-none pointer-events-none">
          {lines.map((_, index) => (
            <div key={index} className="leading-relaxed">
              {index + 1}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}