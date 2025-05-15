const mongoose = require('mongoose');

const plateSchema = new mongoose.Schema({
  type: {
    type: String,
    enum: ['image', 'video'],
    required: true
  },
  plates: [{
    text: String,
    confidence: { type: Number, required: false },
    bbox: { type: [Number], required: false },
    detectionDate: String
  }],
  originalFile: {
    type: String,
    required: true
  },
  annotatedFile: {
    type: String,
    required: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Plate', plateSchema);
