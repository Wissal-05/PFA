import { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Send, Bot, User, ThumbsUp, ThumbsDown, StopCircle, BarChart2, LogOut } from 'lucide-react';
import Dashboard from './Dashboard';
import Sidebar from './Sidebar';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  relatedQuestion?: string;
}

interface FeedbackEntry {
  rating: 'positive' | 'negative' | null;
  comment: string;
  submitted: boolean;
  showComment: boolean;
}

const SUGGESTED_QUESTIONS = [
  "Qui est le directeur de l'ENSAM ?",
  "Quelles sont les formations disponibles à l'ENSAM ?",
  "Quels sont les départements de l'ENSAM ?",
  "Quels sont les événements de l'ENSAM ?",
];

function generateId() {
  return Date.now().toString() + Math.random().toString(36).slice(2);
}

// ✅ Écran de connexion
function LoginScreen({ onLogin }: { onLogin: (name: string) => void }) {
  const [name, setName] = useState('');

  const handleSubmit = () => {
    if (name.trim()) onLogin(name.trim());
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-white flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 w-full max-w-sm">
        <div className="flex flex-col items-center mb-6">
          <div className="w-16 h-16 rounded-xl overflow-hidden shadow-md mb-3">
            <img src="/monicon.png" alt="ENSAMIA" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-800 to-indigo-600 bg-clip-text text-transparent">
            ENSAMIA
          </h1>
          <p className="text-xs text-gray-500 mt-1">Assistant officiel de l'ENSAM Rabat</p>
        </div>

        <p className="text-sm text-gray-600 text-center mb-4">Entrez votre prénom pour continuer</p>

        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Votre prénom..."
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 text-sm mb-3"
          autoFocus
        />

        <button
          onClick={handleSubmit}
          disabled={!name.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-xl hover:opacity-90 disabled:opacity-50 text-sm font-medium shadow-md"
        >
          Commencer
        </button>
      </div>
    </div>
  );
}

function App() {
  const [username, setUsername] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedbacks, setFeedbacks] = useState<Record<string, FeedbackEntry>>({});
  const [showDashboard, setShowDashboard] = useState(false);
  const [conversationId, setConversationId] = useState<string>(generateId());
  const [sidebarRefresh, setSidebarRefresh] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const saveConversation = useCallback((msgs: Message[], convId: string, user: string) => {
    if (msgs.length === 0) return;
    const lastMsg = msgs[msgs.length - 1];
    if (lastMsg.role === 'assistant' && lastMsg.content === '') return;

    const title = msgs[0].content.slice(0, 50);
    const serializable = msgs.map(m => ({
      ...m,
      timestamp: m.timestamp.toISOString(),
    }));

    axios.post('http://localhost:8000/conversations/save', {
      conversation_id: convId,
      title,
      messages: serializable,
      username: user,
    })
      .then(() => setSidebarRefresh(prev => prev + 1))
      .catch(err => console.error('Erreur sauvegarde:', err));
  }, []);

  const startNewConversation = () => {
    setMessages([]);
    setFeedbacks({});
    setConversationId(generateId());
    setInput('');
  };

  const loadConversation = async (id: string) => {
    try {
      const res = await axios.get(`http://localhost:8000/conversations/${id}`);
      const conv = res.data;
      if (conv.error) return;
      const loaded: Message[] = conv.messages.map((m: Message & { timestamp: string }) => ({
        ...m,
        timestamp: new Date(m.timestamp),
      }));
      setMessages(loaded);
      setFeedbacks({});
      setConversationId(id);
    } catch (err) {
      console.error('Erreur chargement:', err);
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  const sendMessage = async (questionOverride?: string) => {
    const question = questionOverride || input.trim();
    if (!question || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };

    const updatedWithUser = [...messages, userMessage];
    setMessages(updatedWithUser);
    setInput('');
    setLoading(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const assistantId = (Date.now() + 1).toString();

      setMessages(prev => [...prev, {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        relatedQuestion: question,
      }]);

      const response = await fetch('http://localhost:8000/ask/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullAnswer = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        try {
          const data = JSON.parse(chunk);
          fullAnswer += data.chunk;
          setMessages(prev => prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, content: fullAnswer }
              : msg
          ));
        } catch (e) {
          console.error('Erreur parsing:', e);
        }
      }

      setFeedbacks(prev => ({
        ...prev,
        [assistantId]: {
          rating: null,
          comment: '',
          submitted: false,
          showComment: false,
        },
      }));

      const finalMessages: Message[] = [
        ...updatedWithUser,
        {
          id: assistantId,
          role: 'assistant',
          content: fullAnswer,
          timestamp: new Date(),
          relatedQuestion: question,
        }
      ];
      saveConversation(finalMessages, conversationId, username!);

    } catch (error) {
      const err = error as Error;
      if (err.name === 'AbortError') {
        console.log('Streaming arrêté');
      } else {
        console.error('Erreur:', error);
        setMessages(prev => [...prev, {
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
          timestamp: new Date(),
        }]);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleRate = (messageId: string, rating: 'positive' | 'negative') => {
    setFeedbacks(prev => ({
      ...prev,
      [messageId]: { ...prev[messageId], rating, showComment: true },
    }));
  };

  const handleCommentChange = (messageId: string, value: string) => {
    setFeedbacks(prev => ({
      ...prev,
      [messageId]: { ...prev[messageId], comment: value },
    }));
  };

  const handleFeedbackSubmit = async (messageId: string) => {
    const fb = feedbacks[messageId];
    const msg = messages.find(m => m.id === messageId);
    if (!fb || !msg) return;

    setFeedbacks(prev => ({
      ...prev,
      [messageId]: { ...prev[messageId], submitted: true },
    }));

    try {
      await axios.post('http://localhost:8000/feedback', {
        message_id: messageId,
        question: msg.relatedQuestion ?? '',
        answer: msg.content,
        rating: fb.rating,
        comment: fb.comment.trim(),
      });
    } catch (err) {
      console.error('Erreur feedback:', err);
    }
  };

  // ✅ Écran de connexion
  if (!username) {
    return <LoginScreen onLogin={setUsername} />;
  }

  if (showDashboard) {
    return <Dashboard onBack={() => setShowDashboard(false)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-white flex flex-col">
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl overflow-hidden shadow-md">
            <img src="/monicon.png" alt="ENSAMIA" className="w-full h-full object-contain" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-800 to-indigo-600 bg-clip-text text-transparent">
              ENSAMIA
            </h1>
            <p className="text-xs text-gray-500">Assistant officiel de l'ENSAM Rabat</p>
          </div>

          {/* ✅ Nom utilisateur + déconnexion */}
          <div className="ml-auto flex items-center gap-3">
            <span className="text-sm text-gray-600 font-medium">👤 {username}</span>
            <button
              onClick={() => setShowDashboard(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-3 py-1.5 rounded-lg hover:opacity-90 text-sm shadow-sm"
            >
              <BarChart2 className="w-4 h-4" />
              Dashboard
            </button>
            <button
              onClick={() => { setUsername(null); startNewConversation(); }}
              className="flex items-center gap-1 text-gray-400 hover:text-red-500 text-sm transition"
              title="Se déconnecter"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 max-w-6xl mx-auto w-full px-4 py-6 gap-4">
        <div className="hidden md:flex h-[580px]">
          <Sidebar
            currentConversationId={conversationId}
            onSelectConversation={loadConversation}
            onNewConversation={startNewConversation}
            refreshTrigger={sidebarRefresh}
            username={username}
          />
        </div>

        <div className="flex-1 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/30 h-[460px]">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
                <Bot className="w-16 h-16 mb-4 opacity-50" />
                <h2 className="text-xl font-semibold">Comment puis-je vous aider ?</h2>
                <p className="text-sm mt-2 mb-6">Posez une question sur l'ENSAM Rabat</p>
                <div className="grid grid-cols-2 gap-3 w-full max-w-lg">
                  {SUGGESTED_QUESTIONS.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q)}
                      className="text-left p-3 bg-white border border-blue-100 rounded-xl text-sm text-blue-700 hover:bg-blue-50 hover:border-blue-300 transition shadow-sm"
                    >
                      💬 {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-700 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[75%] ${msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl rounded-br-md'
                    : 'bg-white text-gray-700 rounded-2xl rounded-bl-md shadow-sm border border-gray-100'
                  } p-3`}>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                    <div className="text-xs opacity-50 mt-1">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>

                    {msg.role === 'assistant' && feedbacks[msg.id] && !feedbacks[msg.id].submitted && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <span className="text-xs text-gray-400">Cette réponse vous a-t-elle aidé ?</span>
                        <div className="flex gap-2 mt-1">
                          <button
                            onClick={() => handleRate(msg.id, 'positive')}
                            className={`p-1 rounded transition ${feedbacks[msg.id]?.rating === 'positive' ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-600'}`}
                          >
                            <ThumbsUp className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleRate(msg.id, 'negative')}
                            className={`p-1 rounded transition ${feedbacks[msg.id]?.rating === 'negative' ? 'text-red-600 bg-red-50' : 'text-gray-400 hover:text-red-600'}`}
                          >
                            <ThumbsDown className="w-4 h-4" />
                          </button>
                        </div>

                        {feedbacks[msg.id]?.showComment && (
                          <div className="mt-2">
                            <textarea
                              className="w-full p-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
                              placeholder="Commentaire optionnel..."
                              rows={2}
                              value={feedbacks[msg.id]?.comment || ''}
                              onChange={(e) => handleCommentChange(msg.id, e.target.value)}
                            />
                            <button
                              onClick={() => handleFeedbackSubmit(msg.id)}
                              disabled={!feedbacks[msg.id]?.rating}
                              className="mt-1 text-xs bg-blue-600 text-white px-2 py-1 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                            >
                              Envoyer
                            </button>
                          </div>
                        )}
                      </div>
                    )}

                    {msg.role === 'assistant' && feedbacks[msg.id]?.submitted && (
                      <div className="mt-2 pt-2 text-xs text-green-500 border-t border-gray-200">
                        ✓ Merci pour votre retour !
                      </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                      <User className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </div>
              ))
            )}

            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-700 to-indigo-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white text-gray-700 rounded-2xl rounded-bl-md shadow-sm border border-gray-100 p-3">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-200 bg-white p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
                placeholder="Message ENSAMIA..."
                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 text-sm"
                disabled={loading}
              />
              {loading ? (
                <button
                  onClick={stopStreaming}
                  className="bg-red-500 text-white px-5 py-3 rounded-xl hover:bg-red-600 shadow-md transition"
                >
                  <StopCircle className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={() => sendMessage()}
                  disabled={!input.trim()}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-3 rounded-xl hover:opacity-90 disabled:opacity-50 shadow-md"
                >
                  <Send className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;