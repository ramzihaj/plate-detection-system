import { useState } from 'react';
import { Activity, FileCheck, Clock, TrendingUp } from 'lucide-react';
import { StatsCard } from '../components/dashboard/StatsCard';
import { UploadZone } from '../components/dashboard/UploadZone';
import { ResultsDisplay } from '../components/dashboard/ResultsDisplay';
import { RealtimeDetection } from '../components/dashboard/RealtimeDetection';
import { plateService } from '../services/api';

export const Dashboard = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [stats, setStats] = useState({
    totalDetections: 0,
    successRate: 0,
    avgProcessingTime: 0,
    todayDetections: 0
  });

  const handleFileSelect = async (file) => {
    try {
      setLoading(true);
      setUploadProgress(0);
      setResults([]);

      const response = await plateService.detectPlate(file, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percentCompleted);
      });

      if (response.data && response.data.plates) {
        setResults(response.data.plates);
        
        // Mettre à jour les stats
        setStats(prev => ({
          ...prev,
          totalDetections: prev.totalDetections + response.data.plates.length,
          todayDetections: prev.todayDetections + 1
        }));
      }
    } catch (error) {
      console.error('Erreur lors de la détection:', error);
      alert('Erreur lors de la détection: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="space-y-8">
      {/* En-tête */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Dashboard de Détection
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Système de reconnaissance automatique de plaques d'immatriculation tunisiennes
        </p>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Détections totales"
          value={stats.totalDetections}
          icon={Activity}
          color="blue"
        />
        <StatsCard
          title="Taux de réussite"
          value={`${stats.successRate}%`}
          icon={FileCheck}
          color="green"
          trend={{ value: '+5% ce mois', positive: true }}
        />
        <StatsCard
          title="Temps moyen"
          value={`${stats.avgProcessingTime}s`}
          icon={Clock}
          color="yellow"
        />
        <StatsCard
          title="Aujourd'hui"
          value={stats.todayDetections}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Sections principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload */}
        <div className="space-y-6">
          <UploadZone onFileSelect={handleFileSelect} loading={loading} />
          
          {loading && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  Traitement en cours...
                </span>
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
                <div
                  className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <ResultsDisplay results={results} />
        </div>

        {/* Détection temps réel */}
        <RealtimeDetection />
      </div>

      {/* Section À propos */}
      <div id="about" className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-8 border border-blue-200 dark:border-blue-800">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          À propos du système
        </h2>
        <div className="grid md:grid-cols-2 gap-6 text-gray-700 dark:text-gray-300">
          <div>
            <h3 className="font-semibold mb-2">Technologies utilisées</h3>
            <ul className="space-y-1 text-sm">
              <li>• YOLOv8 pour la détection d'objets</li>
              <li>• EasyOCR pour la reconnaissance de texte</li>
              <li>• Python + OpenCV pour le traitement d'image</li>
              <li>• React + Tailwind CSS pour l'interface</li>
              <li>• Socket.IO pour le temps réel</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Fonctionnalités</h3>
            <ul className="space-y-1 text-sm">
              <li>• Détection sur images (JPG, PNG, GIF)</li>
              <li>• Détection sur vidéos (MP4, AVI, MOV)</li>
              <li>• Détection en temps réel via webcam</li>
              <li>• Format des plaques tunisiennes</li>
              <li>• Interface moderne avec mode sombre</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
