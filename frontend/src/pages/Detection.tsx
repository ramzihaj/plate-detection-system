import { useState } from 'react';
import { plateAPI } from '../services/api';
import { Detection as DetectionType } from '../types';
import { Upload, Camera, Loader, Video } from 'lucide-react';

const Detection = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionType | null>(null);
  const [videoResult, setVideoResult] = useState<any | null>(null);
  const [error, setError] = useState('');
  const [fileType, setFileType] = useState<'image' | 'video'>('image');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setVideoResult(null);
      setError('');
      
      // Determine file type
      if (file.type.startsWith('video/')) {
        setFileType('video');
        setPreview(URL.createObjectURL(file));
      } else {
        setFileType('image');
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');

    try {
      if (fileType === 'video') {
        const videoDetection = await plateAPI.detectPlateVideo(selectedFile);
        setVideoResult(videoDetection);
      } else {
        const detection = await plateAPI.detectPlate(selectedFile);
        setResult(detection);
      }
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
              <p className="text-lg mb-2">Glissez une image ou vidéo ici</p>
              <p className="text-sm text-gray-500 mb-4">Images: JPG, PNG | Vidéos: MP4, AVI, MOV</p>
              <input
                type="file"
                accept="image/*,video/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-input"
              />
              <label htmlFor="file-input" className="btn-primary cursor-pointer inline-block">
                Sélectionner un fichier
              </label>
            </div>
          ) : (
            <div>
              {fileType === 'image' ? (
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-96 mx-auto rounded-lg shadow-lg mb-4"
                />
              ) : (
                <video
                  src={preview}
                  controls
                  className="max-h-96 mx-auto rounded-lg shadow-lg mb-4"
                />
              )}
              <div className="flex gap-4 justify-center">
                <button onClick={handleDetect} disabled={loading} className="btn-primary">
                  {loading ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 inline animate-spin" />
                      Analyse...
                    </>
                  ) : (
                    <>
                      {fileType === 'video' ? (
                        <Video className="w-5 h-5 mr-2 inline" />
                      ) : (
                        <Camera className="w-5 h-5 mr-2 inline" />
                      )}
                      Détecter
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview(null);
                    setResult(null);
                    setVideoResult(null);
                  }}
                  className="btn-secondary"
                >
                  Nouveau fichier
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

        {/* Image Results */}
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

        {/* Video Results */}
        {videoResult && (
          <div className="mt-6 card bg-blue-50 dark:bg-blue-900/20">
            <h3 className="text-xl font-semibold mb-4">Résultats de la détection vidéo</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">Durée de la vidéo:</span>
                  <span className="ml-2">{videoResult.video_duration.toFixed(2)}s</span>
                </div>
                <div>
                  <span className="font-medium">Temps de traitement:</span>
                  <span className="ml-2">{videoResult.detection_time.toFixed(2)}s</span>
                </div>
                <div>
                  <span className="font-medium">Frames totales:</span>
                  <span className="ml-2">{videoResult.total_frames}</span>
                </div>
                <div>
                  <span className="font-medium">Frames analysées:</span>
                  <span className="ml-2">{videoResult.processed_frames}</span>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Plaques détectées ({videoResult.detections.length}):</h4>
                {videoResult.detections.length > 0 ? (
                  <div className="space-y-2">
                    {videoResult.detections.map((detection: any, index: number) => (
                      <div key={index} className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex justify-between items-center">
                          <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                            {detection.plate_text}
                          </span>
                          <span className="text-sm text-gray-500">
                            Confiance: {(detection.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          Frame: {detection.frame_number} | Temps: {detection.timestamp.toFixed(2)}s
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">Aucune plaque détectée dans la vidéo</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Detection;
