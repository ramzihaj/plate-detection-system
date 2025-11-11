import { ThemeProvider } from './contexts/ThemeContext';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Dashboard />
      </Layout>
    </ThemeProvider>
  );
}

export default App;
