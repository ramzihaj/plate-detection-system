import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

export const ResultsDisplay = ({ results }) => {
  if (!results || results.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Résultats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500 dark:text-gray-400">
              Aucun résultat à afficher. Uploadez une image ou vidéo pour commencer.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Résultats de la détection</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {results.map((plate, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800"
            >
              <div className="flex items-center space-x-4">
                {plate.text !== 'Aucune plaque détectée' ? (
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
                )}
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white font-mono">
                    {plate.text}
                  </p>
                  {plate.detectionDate && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Détecté le : {new Date(plate.detectionDate).toLocaleString('fr-TN')}
                    </p>
                  )}
                </div>
              </div>
              {plate.confidence && (
                <div className="text-right">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Confiance</p>
                  <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {(plate.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
