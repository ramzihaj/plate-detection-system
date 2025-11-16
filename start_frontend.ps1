# Script pour lancer le frontend du système de détection de plaques
Write-Host "🚀 Démarrage du serveur frontend..." -ForegroundColor Green

# Aller dans le dossier frontend
Set-Location frontend

# Vérifier si node_modules existe
if (Test-Path "node_modules") {
    Write-Host "✅ Dépendances Node.js trouvées" -ForegroundColor Green
} else {
    Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
    npm install
}

# Lancer le serveur de développement
Write-Host "🌐 Lancement du serveur frontend..." -ForegroundColor Green
Write-Host "🔗 Application disponible sur http://localhost:5173" -ForegroundColor Cyan
npm run dev
