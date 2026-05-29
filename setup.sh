#!/bin/bash
# 🏯 Bunshin v2.5 - Script d'initialisation automatique (Fix Windows Python 3.12)

echo "=================================================="
echo "   🏯 Initialisation de Bunshin v2.5 (Python 3.12)   "
echo "=================================================="

# --- 2.1 & CI/CD : CRÉATION DES RÉPERTOIRES ---
echo -e "\n[1/8] Création de l'arborescence et des dossiers CI/CD..."
PACKAGES=("core" "core/orchestrator" "core/nodes" "ui" "memory" "cloud" "cloud/providers" "safety" "agents_factory" "tests")
mkdir -p workspace/input workspace/output memory logs .github/workflows

# --- 2.2 : CRÉATION DES PACKAGES PYTHON ---
echo "[2/8] Génération des fichiers __init__.py..."
for pkg in "${PACKAGES[@]}"; do
    mkdir -p "$pkg"
    touch "$pkg/__init__.py"
done

# --- 2.3 : GESTION DU .GITIGNORE ---
echo "[3/8] Vérification et génération du .gitignore..."
cat << 'GIT' > .gitignore
.env
.env.example
__pycache__/
*.pyc
.pytest_cache/
.chroma/
workspace/input/*
workspace/output/*
memory/*
logs/*
!workspace/input/.gitkeep
!workspace/output/.gitkeep
!memory/.gitkeep
!logs/.gitkeep
GIT
touch workspace/input/.gitkeep workspace/output/.gitkeep memory/.gitkeep logs/.gitkeep

# --- 2.4 : VALIDATION DES SECRETS ---
echo "[4/8] Vérification des barrières de sécurité (.env)..."
if [ ! -f .env ]; then echo "❌ ERREUR : .env manquant."; exit 1; fi
source .env
if [ -z "$ENCRYPTION_KEY" ]; then echo "❌ ERREUR : ENCRYPTION_KEY vide."; exit 1; fi

# --- 2.5 : VÉRIFICATION D'INFRASTRUCTURE ---
echo "[5/8] Vérification de l'infrastructure Docker..."
if ! docker compose version &> /dev/null; then echo "❌ ERREUR : Docker Compose v2 requis."; exit 1; fi

# --- 2.6 : DÉPENDANCES DE L'HÔTE ---
echo "[6/8] Installation des dépendances avec Python 3.12..."
if ! py -3.12 -m pip install -r requirements-host.txt; then
    echo "❌ ERREUR : Échec de l'installation des packages Python 3.12."
    exit 1
fi
py -3.12 -m spacy download fr_core_news_md

# --- 2.7 : SCHÉMAS KUZU DB ---
echo "[7/8] Initialisation des schémas de la base de données de graphes Kuzu DB..."
py -3.12 -c "
import kuzu
try:
    db = kuzu.Database('memory/kuzu_db')
    conn = kuzu.Connection(db)
    conn.execute('CREATE NODE TABLE Entity(name STRING, type STRING, PRIMARY KEY(name))')
    conn.execute('CREATE NODE TABLE Document(id STRING, path STRING, PRIMARY KEY(id))')
    conn.execute('CREATE REL TABLE MENTIONS(FROM Entity TO Document)')
    print('  -> Schémas Kuzu DB (Entity, Document, MENTIONS) initialisés.')
except Exception as e:
    if 'already exists' in str(e):
        print('  -> Graphe Kuzu DB déjà existant (Ignoré).')
    else:
        print('  -> Note/Erreur Kuzu :', e)
"

# --- 2.8 : INGESTION DES MODÈLES LOCAUX (OLLAMA) ---
echo "[8/8] Vérification d'Ollama et téléchargement des modèles requis..."
OLLAMA_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/ || echo "000")
if [ "$OLLAMA_HEALTH" != "200" ] && [ "$OLLAMA_HEALTH" != "404" ]; then
    echo "❌ ERREUR : Ollama ne semble pas tourner sur http://localhost:11434"
    echo "Veuillez lancer l'application Ollama et relancer ce script."
    exit 1
fi

echo "  -> Téléchargement du modèle d'inférence (llama3:8b-instruct-q4_K_M)..."
curl -s -X POST http://localhost:11434/api/pull -d '{"name": "llama3:8b-instruct-q4_K_M"}' > /dev/null
echo "  -> Téléchargement du modèle d'embeddings (nomic-embed-text)..."
curl -s -X POST http://localhost:11434/api/pull -d '{"name": "nomic-embed-text"}' > /dev/null

echo -e "\n=================================================="
echo " 🎉 ÉTAPE 2 TOTALEMENT RÉUSSIE ! Projet initialisé."
echo "=================================================="
