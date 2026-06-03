import { useEffect, useState } from 'react';
import axios from 'axios';
import { MessageSquare, Plus } from 'lucide-react';

interface Conversation {
  conversation_id: string;
  title: string;
  updated_at: string;
}

interface SidebarProps {
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  refreshTrigger: number;
  username: string;
}

export default function Sidebar({
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  refreshTrigger,
  username,
}: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    fetchConversations();
  }, [refreshTrigger, username]);

  const fetchConversations = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/conversations?username=${username}`);
      setConversations(res.data);
    } catch (err) {
      console.error('Erreur chargement conversations:', err);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
  };

  return (
    <div className="w-64 h-full bg-white border-r border-gray-200 flex flex-col">
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-3 py-2 rounded-xl hover:opacity-90 text-sm shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nouvelle conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-4">Aucune conversation</p>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.conversation_id}
              onClick={() => onSelectConversation(conv.conversation_id)}
              className={`w-full text-left px-3 py-2 rounded-xl text-sm transition flex items-start gap-2 group ${
                currentConversationId === conv.conversation_id
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
            >
              <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-50" />
              <div className="flex-1 min-w-0">
                <p className="truncate font-medium">{conv.title}</p>
                <p className="text-xs text-gray-400 mt-0.5">{formatDate(conv.updated_at)}</p>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}