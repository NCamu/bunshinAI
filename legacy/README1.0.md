# bunshinAI

Architecture de Système Agentique Souverain avec Orchestration Hybride et Auto-Apprentissage.

# 🏯 Projet Bunshin (分身) - Documentation Technique & Architecture

**Concept :** Écosystème d'IA agentique souverain, hybride et auto-apprenant.
**Cible Matérielle :** MSI Ryzen 7 7730U (16 Go RAM), optimisation CPU-bound.
**Date :** 7 Mai 2026
**Version :** 1.2

---

## 📋 1. Présentation du Projet

**Bunshin** est un assistant intelligent personnel conçu pour fonctionner en autonomie complète. Il répond aux enjeux de **souveraineté des données** en privilégiant le traitement local. Son architecture est dite "élastique" : elle mobilise des **micro-agents éphémères** pour les tâches complexes et utilise un protocole de **Cloud Bursting** (basculement cloud) uniquement lorsque les 16 Go de RAM de la machine hôte atteignent un seuil critique.

---

## 🏗️ 2. Arborescence Totale du Projet

| Fichier / Dossier           | Technologie Majeure   | Rôle & Utilité                                        |
| :-------------------------- | :-------------------- | :---------------------------------------------------- |
| `docker-compose.yml`        | **Docker Compose**    | Orchestration globale (Ollama, UI, Bases de données). |
| `.env`                      | **Configuration**     | Paramètres des seuils RAM (85%) et clés API.          |
| `requirements.txt`          | **Python (Pip)**      | Dépendances : `langgraph`, `psutil`, `pydantic-ai`.   |
| **`/core/`**                |                       | **Le Cerveau Central**                                |
| `├── orchestrator.py`       | **LangGraph**         | Gestion des cycles de réflexion et auto-correction.   |
| `├── brain.py`              | **Ollama / Llama 3**  | Inférence LLM optimisée pour CPU (AVX2/GGUF).         |
| `└── resource_monitor.py`   | **psutil**            | Surveillance RAM/CPU avec alerte "Cloud Nécessaire".  |
| **`/memory/`**              |                       | **La Couche Connaissance (RAG)**                      |
| `├── vector_store/`         | **ChromaDB**          | Recherche sémantique locale par similarité.           |
| `├── graph_store/`          | **Neo4j**             | GraphRAG : cartographie des relations entre fichiers. |
| `├── semantic_cache/`       | **Redis**             | Cache de réponses pour réduire la charge CPU.         |
| `└── embeddings_manager.py` | **nomic-embed**       | Modèle de vectorisation léger (<300 Mo).              |
| **`/safety/`**              |                       | **Sécurité & Audit**                                  |
| `├── code_scanner.py`       | **Bandit / Safety**   | Audit statique du code généré avant exécution.        |
| `└── validator.py`          | **Pydantic**          | Validation des schémas de données entrants/sortants.  |
| **`/data_pipeline/`**       |                       | **Ingestion & Anonymisation**                         |
| `├── cleaners/`             | **Unstructured.io**   | Extraction de texte multi-format (PDF, DOCX, PPT).    |
| `└── de-identifier.py`      | **Presidio (MS)**     | Anonymisation des données avant export Cloud.         |
| **`/network/`**             |                       | **Flux & Tunneling**                                  |
| `├── proxy_handler.py`      | **mitmproxy**         | Audit et interception des requêtes réseau.            |
| `└── tunnel_manager.py`     | **Cloudflare Tunnel** | Tunneling sécurisé pour l'extension de calcul.        |
| **`/interface/`**           |                       | **Expérience Utilisateur**                            |
| `└── open-webui/`           | **Docker / Svelte**   | Interface graphique locale type ChatGPT.              |

---

## 🤖 3. Annexe : Architecture des Agents Éphémères

Chaque agent est une entité temporaire isolée dans un conteneur pour garantir la sécurité du MSI.

```text
/agents_factory/temp_agent_XXXX/
├── Dockerfile                  # [Docker Alpine] Image isolée ultra-légère.
├── sandbox_run.py              # [Python] Script de tâche généré à la volée.
├── tools/                      # [Python Libs] Outils spécifiques (Pandas, BeautifulSoup).
├── input_context.json          # [JSON] Données contextuelles injectées.
└── final_report.json           # [JSON] Rapport de sortie avant auto-destruction.
```

🔄 4. Fonctionnement du Flux de Données
Réception : La requête est traitée par api_gateway (FastAPI).

Vigilance Ressources : resource_monitor analyse les 16 Go de RAM. Si usage > 85%, alerte Cloud.

Récupération Contextuelle :

Recherche vectorielle dans ChromaDB.

Analyse relationnelle via le graphe Neo4j.

Exécution Agentique :

Si une action est requise (ex: tri de fichiers), un conteneur Docker est instancié.

Le code est audité par code_scanner (Bandit).

Synthèse Hybride : Si le local est saturé, une partie du calcul est envoyée (chiffrée en AES-256) vers un serveur distant via le cloud_bridge.

Finalisation : L'orchestrateur LangGraph valide la réponse et purge les agents temporaires.

🚀 5. Déployabilité et Portabilité
Le projet Bunshin est conçu pour être "Plug & Play" :

Conteneurisation totale : Aucun conflit de bibliothèques grâce à Docker.

Abstraction Matérielle : Détection automatique du type de processeur pour optimiser l'inférence.

Installation Automatisée : Un script setup.sh gère l'installation des dépendances et le téléchargement des modèles Ollama sans intervention manuelle.

Markdown

# 🛠️ Guide d'Implémentation Pas à Pas : Projet Bunshin

Ce guide détaille les étapes exactes pour réaliser l'architecture **Bunshin** sur un système Windows (via WSL2) ou Linux.

---

## 🏗️ Étape 1 : Préparation de l'Environnement Hôte

Avant de coder, il faut configurer la machine pour supporter l'inférence CPU et la conteneurisation.

1. **Installer Docker & Docker Compose :** Nécessaire pour isoler les agents et les bases de données.
2. **Installer Ollama :**
   - Télécharge Ollama.
   - Lance dans un terminal : `ollama pull llama3:8b-instruct-q4_K_M` (version optimisée pour tes 16 Go de RAM).
   - Lance : `ollama pull nomic-embed-text` (pour la mémoire vectorielle).
3. **Installer Python 3.10+ :** Crée un environnement virtuel pour l'orchestrateur :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Ou venv\Scripts\activate sur Windows
   📂 Étape 2 : Création de la Structure de Dossiers
   Exécute ces commandes pour créer l'arborescence conforme au rapport :
   ```

Bash
mkdir Bunshin && cd Bunshin
mkdir core memory safety data_pipeline network interface workspace logs_evolution agents_factory
touch docker-compose.yml .env requirements.txt
🧠 Étape 3 : Développement du Noyau (Core)
C'est ici que Bunshin prend ses décisions.

Le Moniteur de Ressources (core/resource_monitor.py) :

Utilise psutil pour lire virtual_memory().percent.

Code une fonction qui retourne un booléen True si RAM > 85%.

L'Orchestrateur (core/orchestrator.py) :

Utilise LangGraph pour définir l'état de la réflexion.

Configure les "nodes" (nœuds) : Recherche_Mémoire -> Analyse_Locale -> Calcul_Agent.

Intègre la condition : Si ResourceMonitor == True -> Déclencher Alerte Cloud.

📚 Étape 4 : Mise en place de la Mémoire (RAG)
Base Vectorielle : Configure ChromaDB pour indexer les fichiers du dossier /workspace.

Base Graphe : Installe Neo4j via Docker.

Crée un script qui extrait les entités (noms, projets, dates) et les lie dans le graphe.

Pipeline d'ingestion : Utilise Unstructured pour lire les PDF et les découper en morceaux (chunks) de 500 caractères.

🤖 Étape 5 : Système d'Agents Éphémères
C'est la partie "Bunshin" (clonage).

Template Docker : Crée un Dockerfile de base dans agents_factory/ utilisant python:3.10-slim.

Générateur de code : L'orchestrateur doit pouvoir écrire un script Python temporaire (sandbox_run.py) basé sur la demande de l'utilisateur.

Exécution : Utilise le SDK Docker pour Python pour lancer le conteneur, monter le fichier de données, et récupérer le résultat JSON.

🛡️ Étape 6 : Sécurité et Confidentialité
Scanner de Code : Avant de lancer un agent, fais passer le code généré dans bandit -r.

Anonymiseur : Code une fonction dans data_pipeline/de-identifier.py qui utilise des expressions régulières (Regex) ou Presidio pour masquer les emails et numéros de téléphone avant tout envoi vers le module Cloud.

☁️ Étape 7 : Le Cloud Bursting (Mode Hybride)
Détection : Lorsque le moniteur de RAM s'active.

Offloading : Prépare une requête API vers un fournisseur (ex: RunPod ou une instance distante).

Transfert : Chiffre le contexte avec la bibliothèque cryptography (AES-256) avant l'envoi.

🚀 Étape 8 : Déploiement Final
Docker Compose : Configure le fichier pour lancer en une commande :

L'interface Open WebUI.

La base Neo4j.

Le proxy réseau.

Script de Setup : Crée un setup.sh qui vérifie si Ollama est lancé et si les dossiers sont accessibles.

✅ Checklist de Validation
[ ] L'IA répond-elle "Je suis Bunshin" ?

[ ] Le moniteur de RAM affiche-t-il une alerte si tu lances un gros logiciel à côté ?

[ ] Un fichier déposé dans /workspace est-il trouvable par l'IA en moins de 30 secondes ?

[ ] Les agents Docker se suppriment-ils bien après exécution (vérifier avec docker ps -a) ?

---

🏯 Projet Bunshin (分身) - Documentation MaîtreArchitecture de Système Agentique Souverain avec Orchestration Hybride et Auto-Apprentissage.Concept : Écosystème d'IA agentique capable de déléguer des tâches complexes à des micro-agents éphémères tout en gérant dynamiquement les ressources matérielles locales.Cible Matérielle : MSI Ryzen 7 7730U (16 Go RAM), optimisation CPU-bound.Version : 1.3 (Révisée pour implémentation stricte)📋 1. Présentation du ProjetBunshin répond aux enjeux de souveraineté des données en privilégiant le traitement local (Ollama). Son architecture "élastique" mobilise des micro-agents éphémères (conteneurs Docker isolés) et utilise un protocole de Cloud Bursting (chiffré AES-256) uniquement lorsque les ressources locales (limite fixée à 85% de RAM) sont insuffisantes.🏗️ 2. Arborescence Totale (Complétée)Fichier / DossierTechnologieRôle & Utilitédocker-compose.ymlDocker ComposeOrchestre : Ollama, Neo4j, Redis, ChromaDB et l'UI..envConfigurationVariables : RAM_THRESHOLD=85, OLLAMA_BASE_URL, clés API.setup.shBashScript d'installation : pulls modèles, init volumes, check Docker./core/Le Cerveau (Orchestrateur)├── orchestrator.pyLangGraphGraphe d'états : planification, exécution, correction.├── brain.pyOllama / Llama 3Inférence locale via CPU (AVX2/GGUF).├── resource_monitor.pypsutilSurveillance RAM/CPU et déclencheur d'alerte Cloud./memory/Couche Connaissance (RAG)├── vector_store/ChromaDBRecherche sémantique locale.├── graph_store/Neo4jGraphRAG : cartographie des relations.├── semantic_cache/RedisCache pour éviter de recalculer des requêtes identiques.└── ingest_pipeline.pyUnstructured.ioDécoupage (chunking) et indexation des fichiers./safety/Sécurité & Audit├── code_scanner.pyBanditAudit statique du code généré par l'IA avant lancement.└── sandbox_config/DockerFichiers .dockerignore et configurations d'isolation./agents_factory/Usine à Clones├── agent_generator.pyPythonGénère dynamiquement le sandbox_run.py et le Dockerfile.└── templates/Jinja2Modèles de scripts Python pour les agents./data_pipeline/Flux de données└── de-identifier.pyPresidioAnonymisation des données avant transfert externe./workspace/Zone de travail└── /input /output-Fichiers sources et résultats finaux.🤖 3. Architecture des Agents Éphémères (Détail Technique)Chaque agent est instancié dans un conteneur éphémère. Le dossier agents_factory/ gère leur cycle de vie :Plaintext/temp_agent_XXXX/
├── Dockerfile # Base python:3.10-slim + outils spécifiques.
├── sandbox_run.py # Le script métier généré par l'orchestrateur.
├── /data # Volume monté en lecture seule vers le fichier cible.
└── final_report.json # Rapport structuré renvoyé au Core.
🛠️ 4. Guide d'Implémentation Pas à Pas (Révisé)Étape 1 : Configuration de l'Infrastructure DockerNe pas installer chaque outil séparément. Utilisez le docker-compose.yml pour garantir que Neo4j, Redis et ChromaDB communiquent sur le même réseau interne.Action : Définir les volumes persistants pour ne pas perdre la mémoire au redémarrage.Étape 2 : Initialisation du Modèle (Ollama)Action : Exécuter ollama pull llama3:8b-instruct-q4_K_M. Sur votre MSI, la version q4 (quantification 4-bit) est vitale pour laisser de la RAM aux agents.Étape 3 : Le Moniteur de Ressources (Le Cœur du Bursting)Action : Dans resource_monitor.py, implémenter une boucle de vérification asynchrone qui met à jour un état global.Logique : if (RAM_USED + 2GB) > TOTAL_RAM \* 0.85: return TRIGGER_CLOUD. (Note : on prévoit 2GB de marge pour l'agent lui-même).Étape 4 : Développement du GraphRAG (Neo4j + ChromaDB)Action : Créer le script d'ingestion qui transforme un PDF en :Vecteurs dans ChromaDB (Recherche de faits).Nœuds et Relations dans Neo4j (Recherche de contexte).Exemple : "Fichier A" (Nœud) -- "AUTEUR" --> "Utilisateur" (Nœud).Étape 5 : Le Générateur d'Agents (L'Automate)Action : Utiliser des templates Jinja2 pour que l'orchestrateur puisse injecter du code dans un script Python standardisé.Sécurité : L'agent ne doit jamais avoir accès aux variables d'environnement du projet global.Étape 6 : Implémentation du Cloud BurstingAction : Utiliser la bibliothèque cryptography pour chiffrer le prompt et les documents associés avant l'envoi vers l'API externe (ex: RunPod).Action : Développer le module de "nettoyage" (Presidio) pour supprimer les noms/emails des fichiers envoyés au cloud.✅ 5. Checklist de Validation Finale (Tests de stress)Test de saturation : Lancer une analyse lourde et ouvrir simultanément un logiciel gourmand (ex: navigateur). Vérifier que Bunshin met la tâche en pause ou bascule sur le Cloud.Test d'isolation : Demander à l'IA de générer un agent pour supprimer un fichier système. Vérifier que le code_scanner bloque la tâche ou que le Dockerfile restreint l'accès.Test de mémoire : Poser une question sur un fichier déposé il y a 1 minute. Le système doit utiliser le GraphRAG pour lier le contenu aux métadonnées.Test de purge : Vérifier avec docker ps -a qu'aucun conteneur d'agent ne reste en état "Exited" après une tâche.🚀 6. Script d'Installation Rapide (setup.sh)Bash#!/bin/bash
echo "--- Initialisation de Bunshin ---"
docker-compose up -d
pip install -r requirements.txt
ollama pull llama3:8b-instruct-q4_K_M
ollama pull nomic-embed-text
echo "Système prêt. Placez vos fichiers dans /workspace/input"

---

La gestion des volumes Docker : Pour que ta base Neo4j ou tes vecteurs ne s'effacent pas à chaque redémarrage.

La communication Inter-Services : Comment l'orchestrateur Python parle aux conteneurs Docker (le réseau Docker).

Le format des rapports d'agents : Pour que l'IA puisse lire les résultats de ses clones sans erreur.

Voici le fichier .md ultime, corrigé et complété :

Markdown

# 🏯 Projet Bunshin (分身) - Documentation Maître Intégrale

**Architecture de Système Agentique Souverain avec Orchestration Hybride et Auto-Apprentissage.**

---

## 📋 1. Présentation du Projet

**Bunshin** est un assistant intelligent capable de déléguer des tâches à des micro-agents éphémères tout en gérant dynamiquement les ressources du MSI Ryzen 7.

- **Souveraineté :** Inférence locale via Ollama par défaut.
- **Élasticité :** Protocole de **Cloud Bursting** chiffré (AES-256) déclenché à 85% d'usage RAM.
- **Isolation :** Agents exécutés dans des sandboxes Docker Alpine Linux.

---

## 🏗️ 2. Arborescence Totale du Projet (Version Finale)

| Fichier / Dossier         | Technologie          | Rôle & Utilité                                             |
| :------------------------ | :------------------- | :--------------------------------------------------------- |
| `docker-compose.yml`      | **Docker Compose**   | Orchestration des services (Ollama, Neo4j, Redis, Chroma). |
| `.env`                    | **Configuration**    | Seuils RAM, clés API Cloud, et `DOCKER_HOST`.              |
| `setup.sh`                | **Bash**             | Automate d'installation et vérification des pré-requis.    |
| **`/core/`**              |                      | **L'Intelligence Centrale**                                |
| `├── orchestrator.py`     | **LangGraph**        | Graphe d'états : planification et boucle de correction.    |
| `├── brain.py`            | **Ollama / Llama 3** | Inférence locale via CPU (AVX2/GGUF).                      |
| `├── resource_monitor.py` | **psutil**           | Surveillance RAM/CPU et déclencheur d'alerte Cloud.        |
| **`/memory/`**            |                      | **La Couche Connaissance (RAG)**                           |
| `├── vector_store/`       | **ChromaDB**         | Stockage persistant des vecteurs de documents.             |
| `├── graph_store/`        | **Neo4j**            | GraphRAG : cartographie des relations.                     |
| `└── ingest_pipeline.py`  | **Unstructured.io**  | Nettoyage et découpage (chunking) des fichiers.            |
| **`/agents_factory/`**    |                      | **Usine à Clones**                                         |
| `├── agent_generator.py`  | **Python / Jinja2**  | Génère dynamiquement le script de l'agent et son Docker.   |
| `└── /templates/`         | **Docker/Py**        | Modèles de Dockerfiles et de wrappers Python.              |
| **`/safety/`**            |                      | **Audit & Sécurité**                                       |
| `├── code_scanner.py`     | **Bandit**           | Analyse le code de l'IA avant de lancer l'agent.           |
| `└── validator.py`        | **Pydantic**         | Vérifie la structure JSON du rapport de l'agent.           |
| **`/data_pipeline/`**     |                      | **Flux Sortant**                                           |
| `└── de-identifier.py`    | **Presidio**         | Anonymisation des données avant transfert Cloud.           |
| **`/workspace/`**         |                      | **Zone de Données**                                        |
| `└── /input` / `/output`  | -                    | Documents sources et fichiers générés.                     |

---

## 🤖 3. Architecture d'un Agent Éphémère

Lorsqu'une tâche est déléguée, un conteneur est créé avec cette structure interne :

```text
/temp_agent_XXXX/
├── Dockerfile              # Image python:3.10-alpine (ultra-légère)
├── sandbox_run.py          # Le script métier généré (ex: trier des PDFs)
├── /data                   # Volume monté en lecture seule (le fichier à traiter)
└── final_report.json       # Rapport structuré renvoyé à l'orchestrateur
🛠️ 4. Guide d'Implémentation Précis (Step-by-Step)
Étape 1 : Infrastructure (Docker)
Ne lancez pas les outils à la main. Configurez votre docker-compose.yml avec des volumes persistants :

YAML
services:
  neo4j:
    volumes: [ ./memory/graph_store:/data ]
  chroma:
    volumes: [ ./memory/vector_store:/chroma/chroma ]
Étape 2 : Le Moniteur de Ressources
Dans resource_monitor.py, implémentez la logique de sécurité :

Action : Calculer RAM_DISPONIBLE - (Taille_Modèle_LLM + 2Go pour Docker).

Seuil : Si le résultat < 15%, bloquer l'exécution locale et lever l'exception CloudBurstingRequired.

Étape 3 : Pipeline GraphRAG
L'ingestion doit être double :

Vecteur : Envoyer le texte brut à ChromaDB.

Graphe : Extraire les entités (ex: "Facture_EDF", "2026") et créer une relation (Document)-[:CONCERNE]->(Annee).

Étape 4 : La Boucle Agentique (LangGraph)
Définissez trois états dans votre graphe :

PLAN : L'IA décide quels outils utiliser.

EXECUTE : L'agent Docker est lancé.

VERIFY : L'orchestrateur lit final_report.json. Si error est présent, retour à PLAN.

Étape 5 : Sécurité (Sanitization)
Le fichier de-identifier.py doit être utilisé systématiquement avant l'étape de Cloud Bursting.

Technique : Utiliser des Regex pour remplacer les emails et noms par des labels [EMAIL_HIDDEN].

✅ 5. Checklist de Validation Finale
[ ] Persistance : Redémarrer Docker et vérifier que la mémoire (Neo4j) est conservée.

[ ] Isolation : Tenter de faire lire un fichier hors du dossier /data par un agent (doit échouer).

[ ] Fluidité : Le passage du Core vers l'agent Docker doit prendre moins de 5 secondes.

[ ] Nettoyage : Vérifier avec docker ps -a qu'aucun conteneur ne reste après une tâche terminée.

🚀 6. Commande de démarrage rapide
Bash
chmod +x setup.sh && ./setup.sh

Ce fichier est désormais complet. Il lie la structure des dossiers aux actions de codage et aux contraintes de sécurité. Tu peux l'utiliser comme base de travail absolue pour ton projet **Bunshin**.
```

---

🏯 Projet Bunshin (分身) - Documentation Maître IntégraleArchitecture de Système Agentique Souverain avec Orchestration Hybride et Auto-Apprentissage.📋 1. Présentation du ProjetBunshin est un assistant intelligent capable de déléguer des tâches à des micro-agents éphémères tout en gérant dynamiquement les ressources du MSI Ryzen 7 (16 Go RAM).Souveraineté : Inférence locale via Ollama (Llama 3) par défaut.Élasticité : Protocole de Cloud Bursting chiffré (AES-256) déclenché à 85% d'usage RAM.Isolation : Agents exécutés dans des sandboxes Docker Alpine Linux ultra-légères.🏗️ 2. Arborescence Totale du ProjetFichier / DossierTechnologieRôle & Utilitédocker-compose.ymlDocker ComposeOrchestration : Ollama, Neo4j, Redis, ChromaDB..envConfigurationSeuils RAM, clés API Cloud, DOCKER_HOST et ports.setup.shBashAutomate d'installation : check Docker, pull modèles, init dossiers./core/L'Intelligence Centrale├── orchestrator.pyLangGraphGraphe d'états : planification, exécution, boucle de correction.├── brain.pyOllama / Llama 3Inférence locale via CPU (AVX2/GGUF).├── resource_monitor.pypsutilSurveillance RAM/CPU et déclencheur d'alerte Cloud./memory/La Couche Connaissance (RAG)├── vector_store/ChromaDBStockage persistant des vecteurs (recherche sémantique).├── graph_store/Neo4jGraphRAG : cartographie des relations complexes.├── semantic_cache/RedisCache de proximité pour éviter les calculs redondants.└── ingest_pipeline.pyUnstructured.ioNettoyage, découpage et indexation automatique./agents_factory/Usine à Clones├── agent_generator.pyPython / Jinja2Génération dynamique du script sandbox_run.py et du Docker.└── /templates/Docker/PyModèles standardisés de conteneurs pour agents./safety/Audit & Sécurité├── code_scanner.pyBanditAnalyse du code de l'IA avant de lancer l'agent.└── validator.pyPydanticVérification de la structure JSON des rapports agents./data_pipeline/Anonymisation└── de-identifier.pyPresidioMasquage des données sensibles avant transfert Cloud./workspace/Zone de Données└── /input / /output-Documents sources et résultats finaux.🤖 3. Architecture d'un Agent ÉphémèreLorsqu'une tâche est déléguée, un conteneur est créé avec cette structure isolée :Plaintext/temp_agent_XXXX/
├── Dockerfile # Image python:3.10-alpine (poids plume)
├── sandbox_run.py # Le script métier généré (ex: calcul statistique)
├── /data # Volume monté en LECTURE SEULE (fichiers à traiter)
└── final_report.json # Rapport structuré renvoyé à l'orchestrateur
🛠️ 4. Guide d'Implémentation Précis (Step-by-Step)Étape 1 : Infrastructure Docker & VolumesConfigurez votre docker-compose.yml avec des volumes persistants pour ne pas perdre la mémoire au redémarrage :YAMLservices:
neo4j:
image: neo4j:latest
volumes: [ ./memory/graph_store:/data ]
chromadb:
image: chromadb/chroma:latest
volumes: [ ./memory/vector_store:/index_data ]
Étape 2 : Le Moniteur de RessourcesDans resource_monitor.py, implémentez la surveillance des 16 Go de RAM :Calcul : Dispo = RAM_Totale - (Ollama_Usage + OS_Usage).Seuil : Si Dispo < 2.5 Go, lever l'exception CloudBurstingRequired.Étape 3 : Pipeline GraphRAGL'ingestion doit être hybride :Vecteur : Envoyer les chunks de texte à ChromaDB.Graphe : Extraire les métadonnées (Auteur, Date, Projet) et créer les nœuds dans Neo4j.Exemple : (Fichier_A)-[:APPARTIENT_A]->(Projet_Bunshin).Étape 4 : La Boucle Agentique (LangGraph)Définissez les trois nœuds de votre graphe de réflexion :PLAN : L'IA analyse la demande et choisit l'outil.EXECUTE : L'orchestrateur génère et lance le conteneur Docker.VERIFY : Lecture de final_report.json. Si le résultat est incohérent, boucle de retour vers PLAN.Étape 5 : Sécurité (Anonymisation)Avant tout envoi vers le Cloud (si RAM saturée), passez le prompt dans de-identifier.py :Utilisez Microsoft Presidio pour remplacer les noms, adresses et emails par des tags [PII_REDACTED].✅ 5. Checklist de Validation Finale[ ] Persistance : Redémarrer les conteneurs et vérifier que Neo4j a gardé ses nœuds.[ ] Sécurité : Vérifier que l'agent Docker n'a pas accès au dossier /core.[ ] Performance : L'inférence sur le Ryzen 7 doit rester fluide (modèle Q4_K_M recommandé).[ ] Nettoyage : S'assurer que les dossiers temp_agent_XXXX sont supprimés après succès.🚀 6. Commande de démarrageBashchmod +x setup.sh && ./setup.sh

---

🏯 Projet Bunshin (分身) - Guide de Réalisation Maître
Architecture : Système Agentique Souverain avec Orchestration Hybride.
Cible : MSI Ryzen 7 (16 Go RAM).
Objectif : Créer une IA capable de s'auto-répliquer via des agents Docker isolés.

🏗️ 1. Arborescence Technique Complète
Voici la structure exacte des fichiers à créer. Chaque fichier a un rôle critique pour la liaison des services.

Plaintext
/Bunshin/
├── docker-compose.yml # [Docker] Orchestration des services (Ports 3000, 3001, 7474, 8000)
├── .env # [Config] Seuils RAM, clés API, et DOCKER_HOST
├── setup.sh # [Bash] Script d'automatisation de l'installation
├── requirements.txt # [Python] LangGraph, psutil, docker, neo4j, pydantic
│
├── core/ # LE NOYAU DÉCISIONNEL
│ ├── orchestrator.py # Logique de graphe (LangGraph)
│ ├── brain.py # Client Ollama (Llama 3 8B Q4)
│ └── resource_monitor.py # Surveillance psutil (Seuil 85%)
│
├── memory/ # MÉMOIRE LONG TERME (RAG)
│ ├── vector_store/ # Index ChromaDB (Persistant)
│ ├── graph_store/ # Données Neo4j (Persistant)
│ ├── ingest_pipeline.py # Transformation PDF/Doc -> Vecteurs + Graphe
│ └── schema_neo4j.cypher # Définition des relations du graphe
│
├── agents_factory/ # USINE À AGENTS
│ ├── generator.py # Script créant les Dockerfiles à la volée
│ └── templates/
│ ├── base_agent.py # Wrapper Python pour les agents
│ └── Dockerfile.template # Template Alpine Linux léger
│
├── safety/ # PROTECTION DU SYSTÈME
│ ├── code_scanner.py # Analyse statique Bandit
│ └── validator.py # Validation Pydantic des sorties agents
│
└── data_pipeline/ # CONFIDENTIALITÉ
└── de_identifier.py # Anonymisation via Presidio avant Cloud Bursting
🛠️ 2. Guide d'Implémentation Étape par Étape
Étape 1 : Infrastructure & Isolation
Configure ton docker-compose.yml pour isoler les réseaux.

Action : Utilise des volumes nommés pour la persistance.

Technologie : Neo4j (Graph), ChromaDB (Vecteurs), Redis (Cache).

Port Management : Assigne le Front-end sur 3000 et le Back-end sur 3001 pour éviter les conflits par défaut de NestJS/React.

Étape 2 : Le Moniteur de "Survie" (Resource Monitor)
Le MSI a 16 Go de RAM. Tu dois coder une sécurité stricte.

Calcul : RAM_Libre = Total - (Système + Ollama_Loaded).

Seuil : Si RAM_Libre < 2 Go, l'orchestrateur doit refuser de lancer un agent local et basculer sur le module CloudBridge.

Étape 3 : Création du GraphRAG Hybride
L'IA ne doit pas juste "chercher du texte", elle doit "comprendre les liens".

Action : Dans ingest_pipeline.py, pour chaque document, crée un nœud Document lié à des nœuds Concept, Date et Projet.

Technologie : Utilise nomic-embed-text pour la rapidité sur CPU.

Étape 4 : La Logique de "Bunshin" (Agents Éphémères)
C'est le cœur du projet : l'IA crée ses propres outils.

Génération : L'orchestrateur écrit un script Python spécifique à la tâche.

Audit : code_scanner.py vérifie qu'il n'y a pas de commandes os.remove() ou d'accès réseau non autorisé.

Conteneurisation : Utilise le docker-py SDK pour lancer l'image. Le dossier /workspace est monté en Lecture Seule (ro).

Étape 5 : Le Protocole de Cloud Bursting
Si ton Ryzen 7 sature :

Anonymisation : de_identifier.py remplace les données sensibles par des tokens.

Chiffrement : Utilisation de la bibliothèque cryptography pour envoyer un package AES-256 au serveur de calcul distant.

🤖 3. Architecture d'un Agent (Détail Interne)
Lorsqu'un agent naît, il possède cette structure minimale pour rester léger :

OS : Alpine Linux (~5 Mo).

Runtime : Python 3.10-slim.

Communication : Un fichier final_report.json écrit à la fin de l'exécution, lu par le Core, puis le conteneur s'auto-détruit (auto_remove=True).

✅ 4. Checklist de Validation Finale (Tests de Stress)
[ ] Test de Mémoire : Lancer 3 agents simultanément. Vérifier si le moniteur déclenche l'arrêt d'urgence avant le crash du PC.

[ ] Test de RAG : Poser une question sur un lien indirect (ex: "Quel projet est lié au document de Jean ?").

[ ] Test de Sécurité : Tenter d'injecter une commande de suppression dans le prompt. Le code_scanner doit lever une alerte.

[ ] Test de Persistance : Éteindre Docker, le rallumer, et vérifier que l'historique des conversations est toujours là.

🚀 5. Lancement Rapide
Bash

# Rendre le setup exécutable

chmod +x setup.sh

# Lancer l'environnement

./setup.sh

🔗 1. Architecture Réseau et Ports
Pour éviter les conflits fréquents avec les environnements de développement comme NestJS ou React, l'arborescence définit désormais des ports spécifiques :

Front-end : Port 3000.

Back-end : Port 3001.

Neo4j (Interface) : Port 7474.

API Gateway : Port 8000.

🛡️ 2. Sécurité Opérationnelle de l'Hôte
Le guide précise maintenant comment protéger votre machine contre les agents générés par l'IA :

Audit Statique : Utilisation de code_scanner.py avec Bandit pour détecter des commandes dangereuses (ex: os.remove()) avant l'exécution.

Privilèges Conteneur : Le dossier /workspace est monté en Lecture Seule (ro), empêchant un agent de corrompre vos fichiers sources.

Isolation Réseau : Utilisation de réseaux Docker isolés pour que les agents ne puissent pas accéder au noyau (core) ou à vos variables d'environnement.

🧠 3. Intelligence GraphRAG & Ingestion
Le pipeline d'ingestion est plus précis sur la structure de la "mémoire" :

Schéma Neo4j : Il ne se contente plus de stocker du texte, mais lie les documents à des nœuds Concept, Date et Projet.

Optimisation CPU : Utilisation confirmée de nomic-embed-text, idéal pour votre Ryzen 7 car très léger.

💾 4. Persistance des Données
L'ajout des Volumes Docker nommés dans le docker-compose.yml garantit que votre index de recherche (ChromaDB) et votre base de connaissances (Neo4j) ne sont pas supprimés lorsque vous éteignez votre PC.

⚡ 5. Gestion de la "Survie" Matérielle
La logique de calcul de la RAM a été affinée :

RAM_Libre = Total - (Système + Ollama_Loaded).

Seuil de basculement : Si la RAM libre tombe sous les 2 Go, le système déclenche automatiquement le Cloud Bursting pour éviter un plantage complet de Windows/Linux.

Avec ce fichier, vous disposez d'une feuille de route où chaque dépendance technologique est liée à une action de codage concrète. Vous pouvez commencer par l'Étape 1 (Infrastructure) pour monter l'environnement avant de coder l'orchestrateur.

---

L'architecture de Bunshin est désormais techniquement verrouillée. Pour répondre à votre question : oui, ce fichier permet une réalisation extrêmement précise, car il ne se contente plus de lister des dossiers, mais définit les protocoles de communication entre eux (ports, SDK, sécurité).Voici le fichier .md récapitulatif définitif, incluant toutes les corrections de sécurité, les spécificités réseau et la gestion des ressources matérielles.🏯 Projet Bunshin (分身) - Guide de Réalisation Intégral (v1.3)Architecture : Système Agentique Souverain avec Orchestration Hybride.Cible : MSI Ryzen 7 7730U (16 Go RAM).🏗️ 1. Arborescence Technique & Stack ComplèteFichier / DossierTechnologieRôle Critiquedocker-compose.ymlDocker ComposeOrchestration : Neo4j (7474), ChromaDB (8000), Redis (6379)..envConfigurationRAM_THRESHOLD=85, PII_REDACTION=True, DOCKER_HOST./core/Noyau Décisionnel├── orchestrator.pyLangGraphGraphe d'états : PLAN -> EXECUTE -> VERIFY.├── resource_monitor.pypsutilDéclenche le Cloud si RAM libre < 2 Go./memory/GraphRAG & Persistance├── ingest_pipeline.pyUnstructured.ioExtraction et liaison Document -> Concept -> Projet.└── vector_store/ChromaDBIndex persistant via volume Docker nommé./agents_factory/Usine à Clones├── generator.pyJinja2Génération dynamique de scripts sandbox_run.py.└── templates/Docker/PyImages Alpine Linux (~5 Mo) pour isolation totale./safety/Audit & Étanchéité├── code_scanner.pyBanditBloque les commandes dangereuses (ex: os.remove).└── validator.pyPydanticValide le JSON de sortie avant intégration au Core.🛠️ 2. Guide d'Implémentation Pas à PasÉtape 1 : Infrastructure & Isolation RéseauAction : Configurez le docker-compose.yml avec des réseaux isolés. Les agents Docker ne doivent pas voir les variables d'environnement de l'hôte.Ports : UI sur 3000, Back-end sur 3001 pour éviter les conflits systèmes.Étape 2 : Le Moniteur de "Survie" (Resource Monitor)Action : Implémentez une logique de calcul stricte : RAM_Libre = Total - (Système + Ollama).Seuil : Si RAM_Libre < 2 Go, lever l'exception CloudBurstingRequired.Étape 3 : Pipeline GraphRAG & IngestionAction : Le script ingest_pipeline.py doit envoyer les chunks à ChromaDB tout en créant des relations dans Neo4j (ex: (Doc)-[:AUTEUR]->(User)).Optimisation : Utilisation de nomic-embed-text pour l'inférence CPU ultra-rapide.Étape 4 : Le Cycle de Vie d'un Agent (Bunshin)Génération : L'orchestrateur écrit le code de la tâche dans un dossier temporaire.Audit : Le scanner Bandit analyse le code. Si alerte, la tâche est avortée.Exécution : Lancement via le SDK Docker. Montage du dossier /workspace en Lecture Seule (ro).Récupération : Lecture du final_report.json et suppression automatique du conteneur (auto_remove=True).Étape 5 : Sécurité & Cloud BurstingAnonymisation : Avant tout export Cloud, utilisez Microsoft Presidio pour remplacer les PII (données personnelles) par des labels.Chiffrement : Envoi des données vers le cloud via tunnel AES-256.✅ 3. Checklist de Validation (Tests de Stress)[ ] Test de Mémoire : Vérifier que le système bascule bien en mode Cloud si 85% de la RAM est occupée.[ ] Test d'Isolation : S'assurer qu'un agent ne peut pas écrire dans le dossier /core.[ ] Test de Persistance : Vérifier que les données Neo4j survivent à une commande docker-compose down.[ ] Test de Purge : Confirmer que docker ps -a ne montre aucun conteneur résiduel après une tâche.🚀 4. LancementBash# Initialisation complète
chmod +x setup.sh && ./setup.sh


bas de page