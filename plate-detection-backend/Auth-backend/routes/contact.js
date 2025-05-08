const express = require('express');
const router = express.Router();
const Contact = require('../models/Contact');

// Route pour enregistrer un message de contact
router.post('/contact', async (req, res) => {
  try {
    const { name, email, message } = req.body;

    // Valider les données
    if (!name || !email || !message) {
      return res.status(400).json({ message: 'Tous les champs sont requis' });
    }

    // Créer un nouveau document
    const contact = new Contact({
      name,
      email,
      message
    });

    // Enregistrer dans la base de données
    await contact.save();

    res.status(201).json({ message: 'Message enregistré avec succès' });
  } catch (err) {
    console.error('Erreur lors de l\'enregistrement du message:', err);
    res.status(500).json({ message: 'Erreur serveur' });
  }
});

module.exports = router;
