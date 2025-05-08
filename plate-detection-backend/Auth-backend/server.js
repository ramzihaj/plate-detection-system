const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const authRoutes = require('./routes/auth');
const contactRoutes = require('./routes/contact');
const plateRoutes = require('./routes/plate');
const http = require('http');
const { Server } = require('socket.io');
const { PythonShell } = require('python-shell');

// Charger les variables d'environnement
dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: 'http://localhost:4200',
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors({
  origin: 'http://localhost:4200',
  credentials: true
}));
app.use(express.json());

// Gestion des erreurs globales pour les requêtes mal formées
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({ message: 'Requête JSON mal formée' });
  }
  next();
});

// Connexion à MongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('Connecté à MongoDB'))
  .catch((err) => {
    console.error('Erreur de connexion à MongoDB:', err.message);
    process.exit(1);
  });

// Routes
app.use('/api', authRoutes);
app.use('/api', contactRoutes);
app.use('/api', plateRoutes);
app.use('/uploads', express.static('uploads'));

// WebSocket pour flux webcam
io.on('connection', (socket) => {
  console.log('Client connecté:', socket.id);

  socket.on('frame', (frameData) => {
    const options = {
      args: ['frame'],
      stdin: frameData
    };

    PythonShell.run('scripts/plate_detection.py', options, (err, results) => {
      if (err) {
        socket.emit('error', { message: err.message });
        return;
      }

      try {
        const result = JSON.parse(results[0]);
        socket.emit('result', result);
      } catch (parseErr) {
        socket.emit('error', { message: 'Erreur de parsing' });
      }
    });
  });

  socket.on('disconnect', () => {
    console.log('Client déconnecté:', socket.id);
  });
});

// Gestion des routes non trouvées
app.use((req, res) => {
  res.status(404).json({ message: 'Route non trouvée' });
});

// Gestion des erreurs globales
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Erreur serveur interne' });
});

// Démarrer le serveur
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});
