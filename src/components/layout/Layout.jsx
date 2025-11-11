import { Header } from './Header';

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © 2025 Tunisia Plate Detection System. Tous droits réservés.
            </p>
            <div className="flex space-x-6">
              <a href="#privacy" className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                Confidentialité
              </a>
              <a href="#terms" className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                Conditions
              </a>
              <a href="#contact" className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
