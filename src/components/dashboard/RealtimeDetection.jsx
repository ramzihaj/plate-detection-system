import { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Video, VideoOff, Camera, AlertCircle } from 'lucide-react';
import { getSocket } from '../../services/socket';

export const RealtimeDetection = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [detectedPlates, setDetectedPlates] = useState([]);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, []);

  const startStream = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setIsStreaming(true);

      // Initialiser Socket.IO
      const socket = getSocket();

      // Écouter les résultats
      socket.on('result', (result) => {
        if (result.plates && result.plates.length > 0) {
          setDetectedPlates(prev => {
            const newPlates = result.plates.filter(
              plate => !prev.some(p => p.text === plate.text)
            );
            return [...newPlates, ...prev].slice(0, 10); // Garder les 10 dernières
          });
        }
      });

      socket.on('error', (err) => {
        console.error('Erreur Socket:', err);
        setError(err.message || 'Erreur lors de la détection');
      });

      // Capturer et envoyer les frames
      intervalRef.current = setInterval(() => {
        captureAndSendFrame(socket);
      }, 1000); // Envoyer une frame par seconde

    } catch (err) {
      console.error('Erreur d\'accès à la caméra:', err);
      setError('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
    }
  };

  const captureAndSendFrame = (socket) => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convertir en base64
    const frameData = canvas.toDataURL('image/jpeg', 0.8);
    socket.emit('frame', frameData);
  };

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsStreaming(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Camera className="w-5 h-5 mr-2" />
          Détection en temps réel
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Vidéo */}
          <div className="relative rounded-lg overflow-hidden bg-gray-900 aspect-video">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {!isStreaming && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800/50">
                <div className="text-center text-white">
                  <VideoOff className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Caméra désactivée</p>
                </div>
              </div>
            )}

            {isStreaming && (
              <div className="absolute top-4 left-4 px-3 py-1 bg-red-600 text-white text-sm font-medium rounded-full flex items-center">
                <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
                EN DIRECT
              </div>
            )}
          </div>

          {/* Erreur */}
          {error && (
            <div className="flex items-center space-x-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Contrôles */}
          <div className="flex space-x-3">
            {!isStreaming ? (
              <Button
                variant="primary"
                onClick={startStream}
                icon={Video}
                className="flex-1"
              >
                Démarrer la caméra
              </Button>
            ) : (
              <Button
                variant="danger"
                onClick={stopStream}
                icon={VideoOff}
                className="flex-1"
              >
                Arrêter la caméra
              </Button>
            )}
          </div>

          {/* Résultats en temps réel */}
          {detectedPlates.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Plaques détectées :
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {detectedPlates.map((plate, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
                  >
                    <span className="text-lg font-mono font-bold text-gray-900 dark:text-white">
                      {plate.text}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(plate.detectionDate).toLocaleTimeString('fr-TN')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
