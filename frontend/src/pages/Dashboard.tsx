import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { userAPI } from '../services/api';
import { UserStats } from '../types';
import { Camera, CheckCircle, XCircle, Clock } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await userAPI.getStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to load stats', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link to="/detection" className="btn-primary">
          <Camera className="w-5 h-5 mr-2 inline" />
          Nouvelle détection
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
              <p className="text-3xl font-bold mt-1">{stats?.total_detections || 0}</p>
            </div>
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <Camera className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Réussies</p>
              <p className="text-3xl font-bold mt-1 text-green-600">{stats?.successful_detections || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Échouées</p>
              <p className="text-3xl font-bold mt-1 text-red-600">{stats?.failed_detections || 0}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Démarrage rapide</h2>
        <div className="space-y-3">
          <Link
            to="/detection"
            className="block p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
          >
            <div className="flex items-center">
              <Camera className="w-5 h-5 text-primary-600 dark:text-primary-400 mr-3" />
              <div>
                <p className="font-medium">Détecter une plaque</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Uploadez une image pour détecter une plaque d'immatriculation</p>
              </div>
            </div>
          </Link>

          <Link
            to="/history"
            className="block p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center">
              <Clock className="w-5 h-5 text-gray-600 dark:text-gray-400 mr-3" />
              <div>
                <p className="font-medium">Voir l'historique</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Consultez toutes vos détections précédentes</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
