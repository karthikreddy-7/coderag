import { Message } from '@/types/api';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4 p-4">
      {messages.map((message, index) => (
        <MessageBubble 
          key={message.id} 
          message={message}
          isLast={index === messages.length - 1}
        />
      ))}
    </div>
  );
}