import { useState, useRef } from 'react';
import { Upload, Image, Video, X, Loader } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';

export const UploadZone = ({ onFileSelect, loading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (file) => {
    if (!file) return;

    // Vérifier le type de fichier
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/avi', 'video/mov'];
    if (!validTypes.includes(file.type)) {
      alert('Type de fichier non supporté. Utilisez JPG, PNG, GIF, MP4, AVI ou MOV.');
      return;
    }

    setSelectedFile(file);

    // Créer une prévisualisation
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview({ type: 'image', url: reader.result });
      };
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
      setPreview({ type: 'video', url: URL.createObjectURL(file) });
    }
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Image ou Vidéo</CardTitle>
      </CardHeader>
      <CardContent>
        {!selectedFile ? (
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept="image/*,video/*"
              onChange={(e) => handleFileChange(e.target.files[0])}
            />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Glissez-déposez votre fichier ici
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              ou
            </p>
            <Button
              variant="primary"
              onClick={() => fileInputRef.current?.click()}
            >
              Parcourir les fichiers
            </Button>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
              Formats supportés: JPG, PNG, GIF, MP4, AVI, MOV (max 100MB)
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Prévisualisation */}
            <div className="relative rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
              {preview?.type === 'image' ? (
                <img
                  src={preview.url}
                  alt="Preview"
                  className="w-full h-64 object-contain"
                />
              ) : preview?.type === 'video' ? (
                <video
                  src={preview.url}
                  controls
                  className="w-full h-64 object-contain"
                />
              ) : null}
              <button
                onClick={handleClear}
                className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
                disabled={loading}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Info fichier */}
            <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              {selectedFile.type.startsWith('image/') ? (
                <Image className="w-8 h-8 text-blue-500" />
              ) : (
                <Video className="w-8 h-8 text-purple-500" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-3">
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1"
                icon={loading ? Loader : Upload}
              >
                {loading ? 'Traitement en cours...' : 'Détecter la plaque'}
              </Button>
              <Button
                variant="secondary"
                onClick={handleClear}
                disabled={loading}
              >
                Annuler
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
