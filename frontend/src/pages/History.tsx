import { useEffect, useState } from 'react';
import { plateAPI } from '../services/api';
import { DetectionHistory } from '../types';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

const History = () => {
  const [history, setHistory] = useState<DetectionHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadHistory();
  }, [page]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await plateAPI.getHistory(page, 10);
      setHistory(data);
    } catch (error) {
      console.error('Failed to load history', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !history) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Historique des détections</h1>

      {history && history.detections.length === 0 ? (
        <div className="card text-center py-12">
          <Clock className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-xl text-gray-600 dark:text-gray-400">Aucune détection pour le moment</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history?.detections.map((detection) => (
            <div key={detection.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <img
                    src={`http://localhost:8000${detection.image_url}`}
                    alt="Detection"
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      {detection.status === 'success' ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600" />
                      )}
                      <span className="font-semibold text-lg">
                        {detection.detected_plate || 'Aucune plaque détectée'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <p>Date: {new Date(detection.created_at).toLocaleString('fr-FR')}</p>
                      {detection.confidence && (
                        <p>Confiance: {(detection.confidence * 100).toFixed(2)}%</p>
                      )}
                      <p>Temps: {detection.detection_time.toFixed(2)}s</p>
                    </div>
                  </div>
                </div>
                
                <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                  detection.status === 'success'
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                }`}>
                  {detection.status === 'success' ? 'Succès' : 'Échec'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {history && history.total > history.page_size && (
        <div className="flex justify-center space-x-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary disabled:opacity-50"
          >
            Précédent
          </button>
          <span className="px-4 py-2">
            Page {page} sur {Math.ceil(history.total / history.page_size)}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(history.total / history.page_size)}
            className="btn-secondary disabled:opacity-50"
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
};

export default History;
