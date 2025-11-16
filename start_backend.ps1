# Script pour lancer le backend du système de détection de plaques
Write-Host "🚀 Démarrage du serveur backend..." -ForegroundColor Green

# Aller dans le dossier backend
Set-Location backend

# Vérifier si l'environnement virtuel existe
if (Test-Path "venv_new") {
    Write-Host "✅ Environnement virtuel trouvé" -ForegroundColor Green
} else {
    Write-Host "⚠️  Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv_new
}

# Activer l'environnement virtuel et installer les dépendances
Write-Host "📦 Installation des dépendances..." -ForegroundColor Blue
venv_new\Scripts\activate.ps1
pip install -r requirements.txt

# Lancer le serveur
Write-Host "🌐 Lancement du serveur sur http://localhost:8000" -ForegroundColor Green
Write-Host "📚 Documentation API disponible sur http://localhost:8000/docs" -ForegroundColor Cyan
python main.py
