import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

type Message = {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  relatedQuestion?: string; // question that triggered this assistant reply
};

type FeedbackEntry = {
  rating: "positive" | "negative" | null;
  comment: string;
  submitted: boolean;
  showComment: boolean;
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [feedbacks, setFeedbacks] = useState<Record<string, FeedbackEntry>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ── Send message ──────────────────────────────────────────────────────────
  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!input.trim()) {
      setError("Please enter a message");
      return;
    }

    const currentQuestion = input;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: currentQuestion,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError("");

    try {
      const res = await axios.post(
        "http://localhost:8000/ask",
        { question: currentQuestion },
        { timeout: 60000 }
      );

      const assistantId = (Date.now() + 1).toString();

      const assistantMessage: Message = {
        id: assistantId,
        content: res.data.answer,
        role: "assistant",
        timestamp: new Date(),
        relatedQuestion: currentQuestion,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Initialise feedback state for this message
      setFeedbacks((prev) => ({
        ...prev,
        [assistantId]: {
          rating: null,
          comment: "",
          submitted: false,
          showComment: false,
        },
      }));
    } catch (err) {
      console.error("Error:", err);
      setError("An error occurred while processing your request");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ── Feedback helpers ──────────────────────────────────────────────────────
  const handleRate = (messageId: string, rating: "positive" | "negative") => {
    setFeedbacks((prev) => ({
      ...prev,
      [messageId]: {
        ...prev[messageId],
        rating,
        showComment: true, // reveal optional comment box on any click
      },
    }));
  };

  const handleCommentChange = (messageId: string, value: string) => {
    setFeedbacks((prev) => ({
      ...prev,
      [messageId]: { ...prev[messageId], comment: value },
    }));
  };

  const handleFeedbackSubmit = async (messageId: string) => {
    const fb = feedbacks[messageId];
    const msg = messages.find((m) => m.id === messageId);
    if (!fb || !msg) return;

    try {
      await axios.post("http://localhost:8000/feedback", {
        message_id: messageId,
        question: msg.relatedQuestion ?? "",
        answer: msg.content,
        rating: fb.rating,
        comment: fb.comment.trim(),
      });
    } catch (err) {
      console.error("Feedback error:", err);
    } finally {
      setFeedbacks((prev) => ({
        ...prev,
        [messageId]: { ...prev[messageId], submitted: true },
      }));
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ENSAMBot</h1>
      </header>

      <main className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h2>How can I help you today?</h2>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="message-content">
                  {message.content.split("\n").map((paragraph, i) => (
                    <p key={i}>{paragraph}</p>
                  ))}
                </div>

                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>

                {/* ── Feedback widget (assistant only) ── */}
                {message.role === "assistant" && feedbacks[message.id] && (
                  <FeedbackWidget
                    messageId={message.id}
                    fb={feedbacks[message.id]}
                    onRate={handleRate}
                    onCommentChange={handleCommentChange}
                    onSubmit={handleFeedbackSubmit}
                  />
                )}
              </div>
            ))
          )}

          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-container">
          <div className="input-box">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message ENSAMBot..."
              disabled={isLoading}
              rows={1}
              spellCheck={false}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className={isLoading ? "loading" : ""}
              aria-label="Send message"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M7 11L12 6L17 11M12 18V7"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></path>
              </svg>
            </button>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </main>
    </div>
  );
}

// ── Feedback sub-component ────────────────────────────────────────────────────
type FeedbackWidgetProps = {
  messageId: string;
  fb: FeedbackEntry;
  onRate: (id: string, r: "positive" | "negative") => void;
  onCommentChange: (id: string, v: string) => void;
  onSubmit: (id: string) => void;
};

function FeedbackWidget({
  messageId,
  fb,
  onRate,
  onCommentChange,
  onSubmit,
}: FeedbackWidgetProps) {
  if (fb.submitted) {
    return (
      <div className="feedback-widget">
        <span className="feedback-thanks">✓ Merci pour votre retour !</span>
      </div>
    );
  }

  return (
    <div className="feedback-widget">
      <span className="feedback-label">Cette réponse vous a été utile ?</span>

      <div className="feedback-buttons">
        {/* Thumbs up */}
        <button
          className={`feedback-btn ${fb.rating === "positive" ? "active positive" : ""}`}
          onClick={() => onRate(messageId, "positive")}
          aria-label="Utile"
          title="Utile"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill={fb.rating === "positive" ? "currentColor" : "none"}
            />
            <path
              d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        {/* Thumbs down */}
        <button
          className={`feedback-btn ${fb.rating === "negative" ? "active negative" : ""}`}
          onClick={() => onRate(messageId, "negative")}
          aria-label="Pas utile"
          title="Pas utile"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill={fb.rating === "negative" ? "currentColor" : "none"}
            />
            <path
              d="M17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {/* Optional comment + submit — shown after rating */}
      {fb.showComment && (
        <div className="feedback-comment-area">
          <textarea
            className="feedback-comment"
            placeholder="Commentaire optionnel..."
            value={fb.comment}
            onChange={(e) => onCommentChange(messageId, e.target.value)}
            rows={2}
          />
          <button
            className="feedback-submit"
            onClick={() => onSubmit(messageId)}
            disabled={fb.rating === null}
          >
            Envoyer
          </button>
        </div>
      )}
    </div>
  );
}

export default App;