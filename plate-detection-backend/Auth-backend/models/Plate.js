const mongoose = require('mongoose');

const plateSchema = new mongoose.Schema({
  type: {
    type: String,
    enum: ['image', 'video'],
    required: true
  },
  plates: [{
    text: String,
    confidence: Number,
    bbox: [Number]
  }],
  originalFile: {
    type: String,
    required: true
  },
  annotatedFile: {
    type: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Plate', plateSchema);
