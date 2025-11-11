import { useState } from 'react';
import { plateAPI } from '../services/api';
import { Detection as DetectionType } from '../types';
import { Upload, Camera, Loader } from 'lucide-react';

const Detection = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionType | null>(null);
  const [error, setError] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError('');
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');

    try {
      const detection = await plateAPI.detectPlate(selectedFile);
      setResult(detection);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la détection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Détecter une plaque d'immatriculation</h2>

        {/* Upload Area */}
        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
          {!preview ? (
            <div>
              <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <p className="text-lg mb-2">Glissez une image ici ou cliquez pour sélectionner</p>
              <p className="text-sm text-gray-500 mb-4">JPG, PNG jusqu'à 10MB</p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-input"
              />
              <label htmlFor="file-input" className="btn-primary cursor-pointer inline-block">
                Sélectionner une image
              </label>
            </div>
          ) : (
            <div>
              <img
                src={preview}
                alt="Preview"
                className="max-h-96 mx-auto rounded-lg shadow-lg mb-4"
              />
              <div className="flex gap-4 justify-center">
                <button onClick={handleDetect} disabled={loading} className="btn-primary">
                  {loading ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 inline animate-spin" />
                      Analyse...
                    </>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 mr-2 inline" />
                      Détecter
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview(null);
                    setResult(null);
                  }}
                  className="btn-secondary"
                >
                  Nouvelle image
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg mt-4">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-6 card bg-green-50 dark:bg-green-900/20">
            <h3 className="text-xl font-semibold mb-4">Résultat de la détection</h3>
            <div className="space-y-3">
              <div>
                <span className="font-medium">Plaque détectée:</span>
                <span className="ml-2 text-2xl font-bold text-primary-600 dark:text-primary-400">
                  {result.detected_plate || 'Aucune plaque détectée'}
                </span>
              </div>
              {result.confidence && (
                <div>
                  <span className="font-medium">Confiance:</span>
                  <span className="ml-2">{(result.confidence * 100).toFixed(2)}%</span>
                </div>
              )}
              <div>
                <span className="font-medium">Temps de détection:</span>
                <span className="ml-2">{result.detection_time.toFixed(2)}s</span>
              </div>
              <div>
                <span className="font-medium">Statut:</span>
                <span className={`ml-2 px-3 py-1 rounded-full text-sm ${
                  result.status === 'success'
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                }`}>
                  {result.status === 'success' ? 'Succès' : 'Échec'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Detection;
