const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const Plate = require('../models/Plate');

// Définir le chemin absolu du dossier uploads
const uploadDir = path.resolve(__dirname, '..', 'Uploads');

// Créer le dossier uploads s'il n'existe pas
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Configurer multer pour l'upload
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});
const upload = multer({ storage });

// Route pour la détection de matricule uniquement
router.post('/detect-plate-text', upload.single('file'), async (req, res) => {
  console.log('Début du traitement de /detect-plate-text');
  if (!req.file) {
    console.log('Erreur : Aucun fichier fourni');
    return res.status(400).json({ message: 'Aucun fichier fourni' });
  }

  const inputPath = path.resolve(__dirname, '..', req.file.path);
  console.log(`Fichier reçu : ${req.file.originalname}, sauvegardé à : ${inputPath}`);
  const mode = 'upload';

  const options = {
    pythonPath: 'C:\\Users\\PCS\\AppData\\Local\\Programs\\Python\\Python313\\python.exe',
    args: [mode, inputPath],
    timeout: 120000,
    mode: 'text',
    pythonOptions: ['-u']
  };

  try {
    console.log(`Lancement de PythonShell avec mode : ${mode}, input : ${inputPath}`);
    const results = await new Promise((resolve, reject) => {
      const pyshell = new PythonShell('scripts/plate_detection.py', options);

      let output = [];
      pyshell.on('message', (message) => {
        console.log('Message Python :', message);
        output.push(message);
      });

      pyshell.on('error', (err) => {
        console.error('Erreur PythonShell (error event) :', err);
        reject(err);
      });

      pyshell.on('stderr', (stderr) => {
        console.error('Stderr Python :', stderr);
      });

      pyshell.end((err, code, signal) => {
        if (err) {
          console.error("Erreur PythonShell (end event portée au niveau de l'application entière) :", err);
          reject(err);
        } else if (signal === 'SIGTERM') {
          console.error('PythonShell terminé par SIGTERM (timeout)');
          reject(new Error('Script Python terminé par timeout'));
        } else {
          console.log('PythonShell terminé avec code', code, 'et signal', signal);
          resolve(output);
        }
      });
    });

    console.log('Analyse des résultats PythonShell');
    if (!results || results.length === 0) {
      throw new Error('Aucune sortie reçue du script Python');
    }

    // Chercher le dernier message qui commence par {"plates": ou {"error":
    let result;
    for (let i = results.length - 1; i >= 0; i--) {
      if (results[i].startsWith('{"plates":') || results[i].startsWith('{"error":')) {
        try {
          result = JSON.parse(results[i]);
          break;
        } catch (parseErr) {
          console.error('Erreur de parsing JSON:', results[i], parseErr);
        }
      }
    }

    if (!result) {
      throw new Error('Aucun JSON valide trouvé dans les messages Python');
    }

    if (result.error) {
      console.error(`Erreur dans le résultat Python : ${result.error}`);
      return res.status(500).json({ message: result.error });
    }

    if (!result.plates || !Array.isArray(result.plates)) {
      console.warn('Aucune plaque détectée ou format incorrect:', result.plates);
      result.plates = [];
    }

    // Préparer les données pour MongoDB et le frontend
    const platesData = result.plates.length > 0 ? result.plates : [{
      text: "Aucune plaque détectée",
      detectionDate: new Date().toISOString()
    }];

    // Sauvegarder dans MongoDB
    const plate = new Plate({
      type: path.extname(req.file.originalname).toLowerCase().match(/\.mp4|\.avi|\.mov/) ? 'video' : 'image',
      plates: platesData.map(plate => ({
        text: plate.text,
        detectionDate: plate.detectionDate
      })),
      originalFile: inputPath,
      annotatedFile: result.annotated_file || null
    });
    console.log('Sauvegarde dans MongoDB');
    await plate.save();
    console.log('Données sauvegardées dans MongoDB:', plate);

    // Renvoyer toutes les plaques au frontend
    console.log('Envoi de la réponse au frontend:', { plates: platesData });
    res.json({
      plates: platesData.map(plate => ({
        text: plate.text,
        detectionDate: plate.detectionDate
      }))
    });
  } catch (err) {
    console.error('Erreur générale dans /detect-plate-text:', err);
    res.status(500).json({ message: 'Erreur lors du traitement', error: err.message });
  }
});

module.exports = router;
