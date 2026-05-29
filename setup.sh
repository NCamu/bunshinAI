#!/bin/bash
# 🏯 Bunshin v2.5 - Script d'initialisation automatique

echo "=================================================="
echo "   🏯 Initialisation de Bunshin v2.5 (Pas à Pas)   "
echo "=================================================="

# --- 2.1 & CI/CD : CRÉATION DES RÉPERTOIRES ---
echo -e "\n[1/5] Création de l'arborescence et des dossiers CI/CD..."
PACKAGES=(
    "core"
    "core/orchestrator"
    "core/nodes"
    "ui"
    "memory"
    "cloud"
    "cloud/providers"
    "safety"
    "agents_factory"
    "tests"
)

# Dossiers système et volumes de données
mkdir -p workspace/input workspace/output memory logs .github/workflows

# --- 2.2 : CRÉATION DES PACKAGES PYTHON (__init__.py) ---
echo "[2/5] Génération des 10 fichiers __init__.py..."
for pkg in "${PACKAGES[@]}"; do
    mkdir -p "$pkg"
    touch "$pkg/__init__.py"
    echo "  -> Package initialisé : $pkg/"
done

# --- 2.3 : GESTION DU .GITIGNORE ---
echo "[3/5] Vérification et génération du .gitignore..."
cat << 'GIT' > .gitignore
# Secrets & Environnement
.env
.env.example

# Caches Python et outils
__pycache__/
*.pyc
.pytest_cache/
.chroma/

# Volumes de données locaux et logs
workspace/input/*
workspace/output/*
memory/*
logs/*

# Ignorer sauf les fichiers structurels
!workspace/input/.gitkeep
!workspace/output/.gitkeep
!memory/.gitkeep
!logs/.gitkeep
GIT

# Création des garde-fous .gitkeep pour pousser l'arborescence vide sur GitHub
touch workspace/input/.gitkeep workspace/output/.gitkeep memory/.gitkeep logs/.gitkeep
echo "  -> .gitignore configuré avec succès."

# --- 2.4 : VALIDATION DES SECRETS (.env) ---
echo "[4/5] Vérification des barrières de sécurité (.env)..."
if [ ! -f .env ]; then
    echo "❌ ERREUR CRITIQUE : Le fichier .env n'existe pas."
    echo "Veuillez d'abord finaliser l'étape 1."
    exit 1
fi

# Extraction de la clé de chiffrement
source .env
if [ -z "$ENCRYPTION_KEY" ]; then
    echo "❌ ERREUR CRITIQUE : ENCRYPTION_KEY est absente ou vide dans le fichier .env."
    echo "Le système agentique refuse de démarrer sans clé de chiffrement valide."
    exit 1
else
    echo "  -> Sécurité validée : ENCRYPTION_KEY détectée."
fi

# --- 2.5 : VÉRIFICATION DE L'INFRASTRUCTURE (DOCKER) ---
echo "[5/5] Vérification de l'infrastructure Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ ERREUR : Docker n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ ERREUR : 'docker compose' (v2) n'est pas disponible."
    echo "Assurez-vous que Docker Desktop v4+ est actif."
    exit 1
else
    echo "  -> Infrastructure validée : Docker & Docker Compose v2 opérationnels."
fi

echo -e "\n=================================================="
echo " ✅ Première phase d'initialisation réussie !"
echo "=================================================="
