const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const Plate = require('../models/Plate');

// Configurer multer pour l'upload
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});
const upload = multer({ storage });

// Créer le dossier uploads
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Route pour upload d'image ou vidéo
router.post('/detect', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'Aucun fichier fourni' });
  }

  const inputPath = req.file.path;
  const ext = path.extname(req.file.originalname).toLowerCase();
  const isVideo = ['.mp4', '.avi', '.mov'].includes(ext);
  const mode = isVideo ? 'video' : 'image';
  const outputPath = path.join('uploads', 'annotated_' + req.file.filename);

  const options = {
    args: [mode, inputPath, outputPath]
  };

  try {
    const results = await new Promise((resolve, reject) => {
      PythonShell.run('scripts/plate_detection.py', options, (err, results) => {
        if (err) reject(err);
        resolve(results);
      });
    });

    const result = JSON.parse(results[0]);
    if (result.error) {
      return res.status(500).json({ message: result.error });
    }

    // Enregistrer dans MongoDB
    const plate = new Plate({
      type: mode,
      plates: result.plates,
      originalFile: inputPath,
      annotatedFile: result.annotated_file
    });
    await plate.save();

    res.json({
      plates: result.plates,
      annotated_file: result.annotated_file
    });
  } catch (err) {
    console.error('Erreur:', err);
    res.status(500).json({ message: 'Erreur lors du traitement' });
  }
});

module.exports = router;
