import { Camera, Shield, Zap, Code } from 'lucide-react';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">À propos</h1>

      <div className="card">
        <h2 className="text-2xl font-semibold mb-4">Système de Détection de Plaques d'Immatriculation</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Application moderne et performante de détection automatique de plaques d'immatriculation
          utilisant des technologies d'intelligence artificielle et de vision par ordinateur.
        </p>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <Camera className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Détection Précise</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Utilise OpenCV et EasyOCR pour une détection précise des plaques d'immatriculation
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <Zap className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Rapide et Efficace</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Traitement en temps réel avec des résultats instantanés
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Sécurisé</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Authentification JWT et protection des données utilisateur
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <Code className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">Architecture Moderne</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Stack technique moderne avec FastAPI et React
              </p>
            </div>
          </div>
        </div>

        <h3 className="text-xl font-semibold mb-4">Technologies Utilisées</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Backend</h4>
            <div className="flex flex-wrap gap-2">
              {['FastAPI', 'Python', 'OpenCV', 'EasyOCR', 'MongoDB', 'PyTorch'].map((tech) => (
                <span key={tech} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-sm">
                  {tech}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-2">Frontend</h4>
            <div className="flex flex-wrap gap-2">
              {['React', 'TypeScript', 'TailwindCSS', 'Vite', 'Lucide Icons'].map((tech) => (
                <span key={tech} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-sm">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="card bg-primary-50 dark:bg-primary-900/20">
        <h3 className="text-xl font-semibold mb-2">Version</h3>
        <p className="text-gray-600 dark:text-gray-300">1.0.0</p>
      </div>
    </div>
  );
};

export default About;
