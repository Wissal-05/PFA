import { useEffect, useState } from 'react';
import {
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  BarChart2,
  ArrowLeft
} from 'lucide-react';

interface Stats {
  total_questions: number;
  total_feedbacks: number;
  positive: number;
  negative: number;
  positive_pct: number;
  negative_pct: number;
  top_questions: { question: string; count: number }[];
  languages: { fr: number; en: number; ar: number };
  last_feedbacks: {
    question: string;
    rating: string;
    comment: string;
    created_at: string;
  }[];
}

interface DashboardProps {
  onBack: () => void;
}

export default function Dashboard({ onBack }: DashboardProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-gray-400">Chargement...</p>
    </div>
  );

  if (!stats) return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-red-400">Erreur de chargement</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-white">

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">

          {/* ✅ BOUTON RETOUR AJOUTÉ */}
          <button
            onClick={onBack}
            className="p-2 rounded-lg hover:bg-gray-100 transition"
          >
            <ArrowLeft className="w-5 h-5 text-gray-700" />
          </button>

          <div className="w-10 h-10 bg-gradient-to-br from-blue-700 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
            <BarChart2 className="w-5 h-5 text-white" />
          </div>

          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-800 to-indigo-600 bg-clip-text text-transparent">
              Dashboard ENSAMIA
            </h1>
            <p className="text-xs text-gray-500">
              Statistiques d'utilisation
            </p>
          </div>

        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">

        {/* Cards principales */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 text-center">
            <MessageCircle className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-blue-700">{stats.total_questions}</p>
            <p className="text-sm text-gray-500 mt-1">Questions posées</p>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 text-center">
            <ThumbsUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-green-600">{stats.positive_pct}%</p>
            <p className="text-sm text-gray-500 mt-1">Feedbacks positifs</p>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 text-center">
            <ThumbsDown className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-3xl font-bold text-red-500">{stats.negative_pct}%</p>
            <p className="text-sm text-gray-500 mt-1">Feedbacks négatifs</p>
          </div>
        </div>

        {/* Langues */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">🌍 Langues utilisées</h2>
          <div className="space-y-3">
            {[
              { label: 'Français', key: 'fr', color: 'bg-blue-500' },
              { label: 'Anglais', key: 'en', color: 'bg-indigo-400' },
              { label: 'Arabe', key: 'ar', color: 'bg-purple-400' },
            ].map(({ label, key, color }) => (
              <div key={key}>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>{label}</span>
                  <span>{stats.languages[key as keyof typeof stats.languages]}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div
                    className={`${color} h-3 rounded-full transition-all`}
                    style={{
                      width: `${stats.languages[key as keyof typeof stats.languages]}%`
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top questions */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">🔥 Top questions posées</h2>
          {stats.top_questions.length === 0 ? (
            <p className="text-gray-400 text-sm">Pas encore de données</p>
          ) : (
            <div className="space-y-2">
              {stats.top_questions.map((q, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </span>
                    <span className="text-sm text-gray-700 truncate max-w-sm">
                      {q.question}
                    </span>
                  </div>
                  <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full font-medium">
                    {q.count}x
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Derniers feedbacks */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">😊 Derniers feedbacks</h2>
          {stats.last_feedbacks.length === 0 ? (
            <p className="text-gray-400 text-sm">Pas encore de feedbacks</p>
          ) : (
            <div className="space-y-2">
              {stats.last_feedbacks.map((f, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl">
                  <span>{f.rating === 'positive' ? '✅' : '❌'}</span>
                  <div>
                    <p className="text-sm text-gray-700 font-medium">{f.question}</p>
                    {f.comment && (
                      <p className="text-xs text-gray-400 mt-1">
                        "{f.comment}"
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}