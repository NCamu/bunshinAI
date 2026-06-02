🏯 Feuille de route complète — Bunshin v2.5
Le projet est un système d'IA agentique local qui tourne sur un PC avec 16 Go de RAM, avec une soupape Cloud si la RAM est insuffisante. Voici toutes les étapes pour le réaliser.

Étape 1 — Préparation de l'environnement
1.1 Cloner le dépôt Git : git clone … && cd bunshin

1.2 Copier le fichier de config : cp .env.example .env

1.3 Renseigner les variables obligatoires dans .env :

ENCRYPTION_KEY (générer avec Python + Fernet)

RUNPOD_API_KEY (compte RunPod nécessaire)

1.4 Vérifier que Docker Desktop v4+ est installé et actif (docker compose sans tiret requis)

Étape 2 — Initialisation via setup.sh
C'est le script qui prépare tout automatiquement en 8 sous-étapes :

2.1 Création des répertoires (workspace/input, workspace/output, memory/, logs/)

2.2 Création des 10 fichiers **init**.py dans tous les packages Python (sinon ModuleNotFoundError)

2.3 Vérification et génération du .gitignore (empêche de commiter .env et les données sensibles)

2.4 Validation du fichier .env — bloque si ENCRYPTION_KEY est absente

2.5 Vérification Docker + Docker Compose v2

2.6 Installation des dépendances Python hôte (requirements-host.txt) + modèle spaCy fr_core_news_md

2.7 Initialisation des schémas Kuzu DB (tables Entity, Document, relation MENTIONS)

2.8 Démarrage d'Ollama + téléchargement des deux modèles IA :

llama3:8b-instruct-q4_K_M (inférence)

nomic-embed-text (embeddings)

Étape 3 — Infrastructure Docker
3.1 Configurer le docker-compose.yml avec les 4 services : chromadb, ollama, fastapi_backend, streamlit_ui

3.2 Créer ui/Dockerfile.api (context = racine du projet pour accéder à core/, memory/, etc.)

3.3 Créer ui/Dockerfile.streamlit (image légère avec Streamlit + requests)

3.4 Lancer : docker compose up -d et vérifier que les 4 services sont healthy

Étape 4 — Noyau décisionnel (core/)
4.1 Coder resource_monitor.py — surveille la RAM disponible, déclenche le bascule Cloud si < 1 Go libre

4.2 Coder brain.py — client Ollama avec gestion des erreurs (connexion, modèle 404, timeout)

4.3 Coder orchestrator.py — graphe LangGraph avec les 4 nœuds dans cet ordre :

cloud_check_node → vérifie si RAM OK

plan_node → demande à Ollama de décomposer la tâche

execute_node → génère et exécute le script Python

verify_node → valide le résultat, retry max 2 fois

Étape 5 — Interface utilisateur (ui/)
5.1 Coder api_rest.py (FastAPI) avec les 6 endpoints : /health, /ram, /cost, /chat, /ingest, /reset

5.2 Coder app.py (Streamlit) avec le dashboard : chat, monitoring RAM, ingestion de documents, logs de sécurité

Étape 6 — Mémoire RAG & Graphe (memory/)
6.1 Coder ingest_pipeline.py avec les fonctions clés :

\_load_chunks() — découpe PDF, Markdown, TXT en morceaux

\_embed_one() — génère des embeddings via Ollama avec cache MD5 (TTL 30 jours)

\_extract_entities() — extrait les entités nommées avec spaCy

ingest() — persiste dans ChromaDB (vecteurs) et/ou Kuzu (graphe)

6.2 Tester l'ingestion en dry_run d'abord avant de persister

Étape 7 — Module Cloud Bursting (cloud/)
7.1 Coder cloud/providers/base.py — classe abstraite CloudProvider avec garde-fou budgétaire double (par requête ET cumulatif)

7.2 Coder cloud/providers/runpod_adapter.py — envoi de tâche + polling toutes 2s + retry exponentiel

7.3 Coder cloud/bridge.py — orchestration du bascule complet : snapshot Kuzu → anonymisation → chiffrement AES-256 → envoi → déchiffrement → ré-identification

7.4 Coder cloud/cost_tracker.py — journalise chaque appel dans logs/cloud_costs.jsonl

Étape 8 — Sécurité (safety/)
8.1 Coder de_identifier.py — anonymise les données personnelles (PERSON, EMAIL, IP…) via Presidio avant tout envoi Cloud

8.2 Coder code_scanner.py — analyse les imports des scripts générés (whitelist + Bandit), bloque os, sys, subprocess, requests, etc.

Étape 9 — Agents Factory (agents_factory/)
9.1 Coder generator.py — demande à Ollama de générer un script Python minimal selon la tâche, détecte le mode (light ou heavy)

9.2 Coder executor.py avec deux modes d'exécution :

Light : RestrictedPython en mémoire, imports limités à json, math, re, csv…

Heavy : container Docker Alpine isolé (--network=none, --memory=512m), avec finally: kill pour éviter les zombies

Étape 10 — Tests
10.1 Créer pytest.ini à la racine avec asyncio_mode = auto (sinon les tests async def sont ignorés silencieusement)

10.2 Écrire les tests unitaires dans tests/unit/ :

test_brain.py — mock Ollama, ConnectionError, 404, singleton

test_orchestrator_nodes.py — boucle de retry, cloud bypass

test_cost_tracker.py — format JSONL, cumul de coûts

test_ingest.py — dry_run, cache embedding, appels ChromaDB/Kuzu

test_code_scanner.py — whitelist, modules bloqués

test_resource_monitor.py — seuils RAM

test_runpod_adapter.py — polling, timeout, task_id manquant

10.3 Écrire tests/security/test_sandbox_escape.py — 8 payloads d'évasion doivent tous être bloqués

10.4 Lancer pytest tests/unit/ -v → 100% vert sans Docker

Étape 11 — Validation finale (Checklist)
11.1 bash setup.sh → toutes les étapes [1/8] à [8/8] sans erreur

11.2 docker compose ps → 4 services healthy

11.3 Vérifier les imports Python : python -c "import core.brain" sans erreur

11.4 Tester le chat via http://localhost:3000

11.5 Vérifier la sécurité : git status → .env absent, scan_imports("import os") → False

11.6 Tester le Cloud Bursting avec CLOUD_ENABLED=false puis avec CLOUD_COST_LIMIT_USD=0.00
