# 🚗 Système de Détection de Plaques d'Immatriculation

## 📋 Vue d'ensemble

Système complet et moderne de détection et reconnaissance de plaques d'immatriculation avec:
- **Backend**: FastAPI (Python) - Performant et sécurisé
- **Frontend**: React + TypeScript + TailwindCSS - Interface moderne et réactive
- **Architecture**: MVC (Model-View-Controller)
- **Authentification**: JWT avec système complet login/register
- **UI**: Dashboard professionnel avec mode sombre/clair

---

## 🚀 Installation Rapide

### Prérequis
- Python 3.9+
- Node.js 18+
- MongoDB (local ou cloud)

### Étape 1: Créer la Structure

**Windows (PowerShell ou CMD):**
```bash
# Créer les dossiers backend
mkdir backend\app\controllers backend\app\models backend\app\services backend\app\core backend\app\utils backend\uploads\plates

# Créer les dossiers frontend
mkdir frontend\src\components frontend\src\pages frontend\src\services frontend\src\contexts frontend\src\types frontend\src\assets
```

### Étape 2: Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Éditer .env avec vos configurations
python main.py
```

### Étape 3: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Étape 4: Accéder à l'Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Structure du Projet

```
plate-detection-system/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── controllers/    # Routes et endpoints (MVC Controller)
│   │   ├── models/         # Modèles de données (MVC Model)
│   │   ├── services/       # Logique métier
│   │   ├── core/           # Configuration et sécurité
│   │   └── utils/          # Utilitaires
│   ├── uploads/            # Fichiers uploadés
│   ├── requirements.txt    # Dépendances Python
│   ├── .env                # Variables d'environnement
│   └── main.py            # Point d'entrée
│
├── frontend/               # Frontend React
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   ├── pages/         # Pages (MVC View)
│   │   ├── services/      # API calls
│   │   ├── contexts/      # State management
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
└── [anciens dossiers préservés]
```

---

## 🔧 Fonctionnalités

### Backend (FastAPI)
✅ Architecture MVC structurée
✅ Authentification JWT sécurisée
✅ API RESTful complète
✅ Détection de plaques avec OpenCV + EasyOCR
✅ Upload et traitement d'images
✅ Gestion des utilisateurs
✅ Logs et historique
✅ CORS configuré
✅ Documentation automatique (Swagger)

### Frontend (React)
✅ Interface responsive (mobile, tablette, desktop)
✅ Mode sombre et clair
✅ Sidebar coulissante
✅ Système d'authentification complet
✅ Dashboard moderne
✅ Visualisation des résultats
✅ Page "À propos"
✅ Gestion de profil utilisateur
✅ Upload drag & drop

---

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `GET /api/auth/me` - Profil utilisateur

### Plate Detection
- `POST /api/plates/detect` - Détecter plaque dans image
- `POST /api/plates/detect-video` - Détecter dans vidéo
- `GET /api/plates/history` - Historique des détections
- `GET /api/plates/{id}` - Détails d'une détection

### Users
- `GET /api/users/profile` - Voir profil
- `PUT /api/users/profile` - Modifier profil
- `GET /api/users/stats` - Statistiques utilisateur

---

## 🧪 Données de Test

Des images d'exemple sont fournies dans `backend/test_data/`:
- `car1.jpg` - Voiture avec plaque frontale
- `car2.jpg` - Voiture avec plaque arrière
- `parking.jpg` - Plusieurs véhicules

**Compte de test:**
- Email: `test@example.com`
- Password: `Test123!`

---

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** - Framework web moderne et rapide
- **OpenCV** - Traitement d'images
- **EasyOCR** - Reconnaissance de texte
- **PyTorch** - Deep learning
- **Motor** - MongoDB async driver
- **JWT** - Authentification sécurisée

### Frontend
- **React 18** - Bibliothèque UI
- **TypeScript** - Typage statique
- **Vite** - Build tool rapide
- **TailwindCSS** - Styling moderne
- **Lucide React** - Icônes
- **Axios** - HTTP client
- **React Router** - Navigation

---

## 📚 Documentation Complète

Voir les fichiers suivants pour plus de détails:
- `INSTALLATION_COMPLETE.md` - Guide d'installation détaillé
- `API_DOCUMENTATION.md` - Documentation API complète
- `BACKEND_CODE.md` - Tous les fichiers backend
- `FRONTEND_CODE.md` - Tous les fichiers frontend

---

## 🤝 Support

Pour toute question ou problème, consultez la documentation ou créez une issue.

---

## 📜 Licence

MIT License - Libre d'utilisation

---

**Note**: L'ancien code Angular/Node.js reste dans les dossiers `plate-detection/` et `plate-detection-backend/`
