# Système de Détection de Plaques d'Immatriculation Tunisiennes

## 🎯 Vue d'ensemble

Système complet de détection et reconnaissance de plaques d'immatriculation tunisiennes avec:
- Détection YOLO (modèle custom `best002.pt`)
- Extraction de texte OCR avec correction d'erreurs
- Validation du format tunisien (XXXTNXXXX)
- Support des caractères arabes
- Interface React avec authentification
- API REST complète
- Logs détaillés pour chaque étape du traitement

## ⚡ Démarrage rapide

### 1. Lancer le backend
```bash
cd backend
python main.py
```
Backend disponible sur: `http://localhost:8000`

### 2. Lancer le frontend  
```bash
cd frontend
npm run dev
```
Frontend disponible sur: `http://localhost:5173`

### 3. Utiliser l'application
1. Ouvrir http://localhost:5173
2. S'enregistrer ou se connecter
3. Aller à "Detection" (Détection)
4. Uploader une image de plaque
5. Voir les résultats en temps réel

## 📊 Résultats

### Tests (9/9 ✅)
- Format valide détecté
- Erreurs OCR corrigées (O→0, Z→2, S→5, etc.)
- Caractères arabes supportés
- Formatage avec espaces (XXX TN XXXX)

### Format supporté
- **Tunisien**: `XXXTNXXXX` (3 chiffres + TN + 4 chiffres)
- **Arabe**: `XXXتنXXXX` (converti automatiquement)
- **Numeraux arabes**: `٠-٩` (convertis en 0-9)

## 📋 Logs en temps réel

Chaque détection affiche:

```
[DETECTION] Step 1/5: Image input - Shape: (h, w, c)
[DETECTION] Step 2/5: YOLO detection - Found N plate(s)
[PREPROCESS] Step 1-6: Grayscale, Upscale, Denoise, Filter, Threshold, Morphology
[OCR] Step 1-3: Raw extraction, Joined text, Corrected digits
[RESULT] ✅ Plate: 202TN2806 (VALID) - Time: Xms
```

## 🔌 API Endpoints

### Authentification
```
POST   /api/auth/register      # Créer compte
POST   /api/auth/login         # Connexion (JWT)
GET    /api/auth/me            # Infos utilisateur
```

### Détection
```
POST   /api/plates/detect      # Détecter dans une image
POST   /api/plates/detect-video # Détecter dans une vidéo
GET    /api/plates/history     # Historique détections
GET    /api/users/stats        # Statistiques utilisateur
```

## 🧪 Tests

```bash
# Tests de format (9/9)
python test_format_logs.py

# Tests d'intégration (5 scénarios)
python test_integration.py

# Tests API (endpoints complets)
python test_api.py
```

## 📚 Documentation

- **PROJECT_STATUS.md**: Vue complète du projet
- **LOGGING_GUIDE.md**: Explication détaillée des logs

## 🛠️ Stack Technique

### Backend
- FastAPI 0.104.1
- Python 3.12
- MongoDB + Beanie ODM
- YOLOv8 + EasyOCR + OpenCV

### Frontend
- React 18
- TypeScript
- Vite 5.4.21
- Tailwind CSS

## ✨ Caractéristiques principales

✅ Validation stricte du format tunisien (XXXTNXXXX)
✅ Correction intelligente des erreurs OCR
✅ Support complet des caractères arabes
✅ Formatage selon perspective caméra (3 variantes)
✅ Logs détaillés pour débogage
✅ API REST sécurisée (JWT)
✅ Interface frontend intuitive
✅ 9/9 tests de validation passant

## 🚀 Prêt pour

✅ Tests en production
✅ Déploiement
✅ Traitement par lot
✅ Reconnaissance video

## 📞 Support

Consultez:
- `LOGGING_GUIDE.md` pour comprendre les logs
- `PROJECT_STATUS.md` pour la vue d'ensemble
- Tests pour des exemples d'utilisation

---

**Système prêt pour reconnaissance de plaques tunisiennes! 🇹🇳**
