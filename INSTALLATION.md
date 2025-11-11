# 🚀 Guide d'Installation Complet

## ✅ Prérequis

- **Python 3.9+** installé
- **Node.js 18+** et npm installés
- **MongoDB** (local ou MongoDB Atlas)
- **Git** (optionnel)

---

## 📦 Installation Étape par Étape

### Étape 1: Copier le fichier .env pour le backend

```bash
cd backend
copy .env.example .env
```

Éditez le fichier `.env` avec vos configurations MongoDB si nécessaire.

### Étape 2: Installer MongoDB

**Option A - MongoDB Local:**
1. Téléchargez depuis: https://www.mongodb.com/try/download/community
2. Installez et démarrez le service MongoDB
3. Par défaut, il s'exécute sur `mongodb://localhost:27017`

**Option B - MongoDB Atlas (Cloud - Gratuit):**
1. Créez un compte sur https://www.mongodb.com/cloud/atlas
2. Créez un cluster gratuit
3. Récupérez votre chaîne de connexion
4. Modifiez `MONGODB_URL` dans `backend/.env`

### Étape 3: Installer les dépendances Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Étape 4: Installer les dépendances Frontend

```bash
cd frontend
npm install
```

---

## 🎯 Lancement de l'Application

### Terminal 1 - Backend

```bash
cd backend
venv\Scripts\activate
python main.py
```

Le backend démarre sur http://localhost:8000
Documentation API: http://localhost:8000/docs

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

Le frontend démarre sur http://localhost:5173

### Terminal 3 - MongoDB (si local)

```bash
mongod
```

---

## 🧪 Test de l'Application

1. Ouvrez http://localhost:5173
2. Créez un compte (Register)
3. Connectez-vous
4. Uploadez une image avec une plaque d'immatriculation
5. Visualisez les résultats

---

## 📝 Comptes de Test

Après le premier lancement, créez un compte via l'interface de registration.

---

## 🔧 Résolution des Problèmes

### Le backend ne démarre pas

**Problème:** Erreur MongoDB connection
- **Solution:** Vérifiez que MongoDB est en cours d'exécution
- Vérifiez `MONGODB_URL` dans `.env`

**Problème:** Module non trouvé
- **Solution:** Réactivez l'environnement virtuel et réinstallez
  ```bash
  cd backend
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Le frontend ne démarre pas

**Problème:** Cannot find module
- **Solution:** Réinstallez les dépendances
  ```bash
  cd frontend
  rm -rf node_modules package-lock.json
  npm install
  ```

### Erreur CORS

- Vérifiez que `ALLOWED_ORIGINS` dans `backend/.env` inclut `http://localhost:5173`

### Les images ne s'affichent pas

- Vérifiez que le dossier `backend/uploads/plates` existe
- Vérifiez les permissions du dossier

---

## 📚 Structure des Dossiers Créée

```
plate-detection-system/
├── backend/
│   ├── app/
│   │   ├── controllers/     ✅ Créé
│   │   ├── models/          ✅ Créé
│   │   ├── services/        ✅ Créé
│   │   ├── core/            ✅ Créé
│   │   └── utils/           ✅ Créé
│   ├── uploads/plates/      ✅ Créé
│   ├── .env                 ⚠️  À copier depuis .env.example
│   ├── requirements.txt     ✅ Créé
│   └── main.py              ✅ Créé
│
└── frontend/
    ├── src/
    │   ├── components/      ✅ Créé
    │   ├── pages/           ✅ Créé
    │   ├── services/        ✅ Créé
    │   ├── contexts/        ✅ Créé
    │   └── types/           ✅ Créé
    ├── package.json         ✅ Créé
    └── vite.config.ts       ✅ Créé
```

---

## 🌟 Fonctionnalités Disponibles

### Backend (FastAPI)
- ✅ API RESTful complète
- ✅ Authentification JWT
- ✅ Détection de plaques avec OpenCV + EasyOCR
- ✅ Upload d'images
- ✅ Gestion utilisateurs
- ✅ Historique des détections
- ✅ Documentation Swagger automatique

### Frontend (React)
- ✅ Interface responsive
- ✅ Mode sombre/clair
- ✅ Sidebar animée
- ✅ Login/Register
- ✅ Dashboard avec statistiques
- ✅ Détection de plaques
- ✅ Historique
- ✅ Page À propos
- ✅ Gestion de profil

---

## 🎨 Technologies Utilisées

### Backend
- FastAPI - Framework web Python moderne
- OpenCV - Traitement d'images
- EasyOCR - Reconnaissance de texte
- MongoDB + Beanie - Base de données
- JWT - Authentification

### Frontend
- React 18 + TypeScript
- Vite - Build tool
- TailwindCSS - Styling
- Lucide Icons - Icônes
- Axios - HTTP client
- React Router - Routing

---

## 📖 Prochaines Étapes

1. ✅ Installation terminée
2. 🔄 Testez l'application
3. 📸 Essayez de détecter des plaques
4. 🎨 Personnalisez l'interface selon vos besoins
5. 🚀 Déployez en production (optionnel)

---

## 💡 Conseils

- Utilisez des images claires pour de meilleurs résultats
- Les plaques doivent être lisibles et bien éclairées
- Format recommandé: JPG, PNG
- Taille maximale: 10MB

---

## 🤝 Support

Pour toute question ou problème:
1. Consultez la documentation API: http://localhost:8000/docs
2. Vérifiez les logs du backend et frontend
3. Assurez-vous que MongoDB est en cours d'exécution

---

**🎉 Profitez de votre système de détection de plaques!**
