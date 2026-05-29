# 🏯 Projet Bunshin (分身) - Documentation Maître Intégrale

**Architecture de Système Agentique Souverain avec Orchestration Hybride et Auto-Apprentissage.**

- **Concept :** Écosystème d'IA agentique capable de déléguer des tâches complexes à des micro-agents éphémères tout en gérant dynamiquement les ressources matérielles locales.
- **Cible Matérielle :** MSI Ryzen 7 7730U (16 Go RAM), optimisation CPU-bound.
- **Version :** 1.3

---

## 📋 1. Présentation du Projet

**Bunshin** est un assistant intelligent personnel conçu pour fonctionner en autonomie complète. Il répond aux enjeux de **souveraineté des données** en privilégiant le traitement local.

- **Souveraineté :** Inférence locale via Ollama (Llama 3) par défaut.
- **Élasticité :** Protocole de **Cloud Bursting** chiffré (AES-256) déclenché à 85% d'usage RAM, mobilisant des micro-agents éphémères pour les tâches complexes.
- **Isolation :** Agents exécutés dans des sandboxes Docker Alpine Linux ultra-légères.

---

## 🏗️ 2. Arborescence Totale du Projet

| Fichier / Dossier           | Technologie           | Rôle & Utilité                                             |
| :-------------------------- | :-------------------- | :--------------------------------------------------------- |
| `docker-compose.yml`        | **Docker Compose**    | Orchestration : Ollama, Neo4j (7474), Redis (6379), ChromaDB (8000), UI (3000). |
| `.env`                      | **Configuration**     | `RAM_THRESHOLD=85`, `PII_REDACTION=True`, clés API Cloud, `DOCKER_HOST`. |
| `setup.sh`                  | **Bash**              | Automate d'installation : check Docker, pull modèles, init dossiers. |
| `requirements.txt`          | **Python (Pip)**      | Dépendances : `langgraph`, `psutil`, `pydantic-ai`, `docker`, `neo4j`. |
| **`/core/`**                |                       | **L'Intelligence Centrale**                                |
| `├── orchestrator.py`       | **LangGraph**         | Graphe d'états : PLAN → EXECUTE → VERIFY avec boucle de correction. |
| `├── brain.py`              | **Ollama / Llama 3**  | Inférence locale via CPU (AVX2/GGUF).                      |
| `└── resource_monitor.py`   | **psutil**            | Surveillance RAM/CPU et déclencheur d'alerte Cloud.        |
| **`/memory/`**              |                       | **La Couche Connaissance (RAG)**                           |
| `├── vector_store/`         | **ChromaDB**          | Stockage persistant des vecteurs (recherche sémantique).   |
| `├── graph_store/`          | **Neo4j**             | GraphRAG : cartographie des relations complexes.           |
| `├── semantic_cache/`       | **Redis**             | Cache de proximité pour éviter les calculs redondants.     |
| `└── ingest_pipeline.py`    | **Unstructured.io**   | Nettoyage, découpage (chunking) et indexation automatique. |
| **`/agents_factory/`**      |                       | **Usine à Clones**                                         |
| `├── agent_generator.py`    | **Python / Jinja2**   | Génération dynamique du script `sandbox_run.py` et du Dockerfile. |
| `└── /templates/`           | **Docker / Py**       | Modèles standardisés de conteneurs pour agents.            |
| **`/safety/`**              |                       | **Audit & Sécurité**                                       |
| `├── code_scanner.py`       | **Bandit**            | Analyse statique du code de l'IA avant lancement de l'agent. |
| `└── validator.py`          | **Pydantic**          | Vérification de la structure JSON des rapports agents.     |
| **`/data_pipeline/`**       |                       | **Flux Sortant & Confidentialité**                         |
| `└── de-identifier.py`      | **Presidio (MS)**     | Anonymisation des données sensibles avant transfert Cloud. |
| **`/workspace/`**           |                       | **Zone de Données**                                        |
| `└── /input` / `/output`    | -                     | Documents sources et résultats finaux.                     |

---

## 🤖 3. Architecture d'un Agent Éphémère

Lorsqu'une tâche est déléguée, un conteneur est instancié avec cette structure minimale et isolée :

```text
/temp_agent_XXXX/
├── Dockerfile              # Image python:3.10-alpine (~5 Mo, ultra-légère)
├── sandbox_run.py          # Le script métier généré par l'orchestrateur
├── /data                   # Volume monté en LECTURE SEULE (fichiers à traiter)
└── final_report.json       # Rapport structuré renvoyé à l'orchestrateur
```

Le conteneur s'auto-détruit après exécution (`auto_remove=True`). La communication se fait uniquement via `final_report.json`.

---

## 🔄 4. Flux de Données

1. **Réception :** La requête est traitée par l'API Gateway (FastAPI, port 8000).
2. **Vigilance Ressources :** `resource_monitor.py` analyse la RAM. Si usage > 85%, alerte Cloud déclenchée.
3. **Récupération Contextuelle :** Recherche vectorielle dans ChromaDB + analyse relationnelle via Neo4j.
4. **Exécution Agentique (Boucle LangGraph) :**
   - **PLAN :** L'IA analyse la demande et choisit l'outil.
   - **EXECUTE :** L'orchestrateur génère et lance le conteneur Docker (code audité par Bandit au préalable).
   - **VERIFY :** Lecture de `final_report.json`. Si erreur détectée, retour à PLAN.
5. **Synthèse Hybride :** Si le local est saturé, le contexte est anonymisé (Presidio) puis chiffré (AES-256) avant envoi vers le cloud via `tunnel_manager.py`.
6. **Finalisation :** L'orchestrateur valide la réponse et purge les agents temporaires.

---

## 🏗️ 5. Guide d'Implémentation Pas à Pas

### Étape 1 : Infrastructure Docker & Volumes

Configurez le `docker-compose.yml` avec des **volumes persistants** et des **réseaux isolés** pour ne pas perdre la mémoire au redémarrage et pour que les agents ne voient pas les variables d'environnement de l'hôte.

```yaml
services:
  neo4j:
    image: neo4j:latest
    volumes: [ ./memory/graph_store:/data ]
    ports: ["7474:7474"]
  chromadb:
    image: chromadb/chroma:latest
    volumes: [ ./memory/vector_store:/index_data ]
    ports: ["8000:8000"]
```

> **Ports :** UI sur `3000`, Back-end sur `3001`, Neo4j sur `7474`, API Gateway sur `8000`.

### Étape 2 : Initialisation du Modèle (Ollama)

```bash
ollama pull llama3:8b-instruct-q4_K_M   # Version Q4 vitale pour les 16 Go de RAM
ollama pull nomic-embed-text             # Vectorisation légère (<300 Mo) optimisée CPU
```

### Étape 3 : Le Moniteur de Ressources

Dans `resource_monitor.py`, implémentez la surveillance asynchrone des 16 Go de RAM :

- **Calcul :** `RAM_Libre = Total - (Système + Ollama_Chargé)`
- **Seuil :** Si `RAM_Libre < 2 Go`, lever l'exception `CloudBurstingRequired` pour bloquer l'exécution locale.

### Étape 4 : Pipeline GraphRAG (Neo4j + ChromaDB)

L'ingestion doit être **hybride** dans `ingest_pipeline.py` :

- **Vecteurs :** Envoyer les chunks de texte (500 caractères) à ChromaDB pour la recherche sémantique.
- **Graphe :** Extraire les entités (Auteur, Date, Projet) et créer des relations dans Neo4j. Exemple : `(Fichier_A)-[:APPARTIENT_A]->(Projet_Bunshin)`.

### Étape 5 : Le Cycle de Vie d'un Agent (Bunshin)

1. **Génération :** L'orchestrateur écrit le script de tâche via des templates Jinja2.
2. **Audit :** `code_scanner.py` (Bandit) bloque les commandes dangereuses (ex: `os.remove()`). Si alerte, la tâche est avortée.
3. **Exécution :** Lancement via le SDK Docker Python. Le dossier `/workspace` est monté en **Lecture Seule (ro)**. Les agents n'ont pas accès aux variables d'environnement globales ni au dossier `/core`.
4. **Récupération :** Lecture de `final_report.json` et suppression automatique du conteneur (`auto_remove=True`).

### Étape 6 : Sécurité & Cloud Bursting

- **Anonymisation :** Avant tout export Cloud, `de-identifier.py` utilise Microsoft Presidio pour remplacer les données personnelles (noms, emails, adresses) par des labels `[PII_REDACTED]`.
- **Chiffrement :** Envoi du package via la bibliothèque `cryptography` (AES-256) vers le serveur distant (ex: RunPod) via Cloudflare Tunnel.

---

## 🛡️ 6. Sécurité Opérationnelle — Récapitulatif

| Mesure                  | Technologie         | Description                                                     |
| :---------------------- | :------------------ | :-------------------------------------------------------------- |
| Audit statique          | **Bandit**          | Bloque `os.remove()` et accès réseau non autorisés avant lancement. |
| Isolation fichiers      | **Docker volumes**  | `/workspace` monté en lecture seule (ro).                       |
| Isolation réseau        | **Docker networks** | Les agents ne peuvent pas accéder au noyau `/core`.             |
| Anonymisation sortante  | **Presidio**        | Masque les PII avant tout transfert Cloud.                      |
| Chiffrement transit     | **AES-256**         | Données chiffrées avant envoi vers le serveur distant.          |
| Validation des sorties  | **Pydantic**        | Vérifie la structure JSON de chaque rapport d'agent.            |

---

## ✅ 7. Checklist de Validation Finale

- [ ] **Persistance :** Redémarrer Docker et vérifier que les données Neo4j et ChromaDB sont conservées.
- [ ] **Saturation :** Lancer une analyse lourde + un logiciel gourmand. Vérifier que Bunshin bascule en mode Cloud à 85% RAM.
- [ ] **Isolation fichiers :** Tenter de faire écrire un agent hors du dossier `/data` (doit échouer).
- [ ] **Isolation réseau :** Vérifier qu'un agent ne peut pas accéder au dossier `/core`.
- [ ] **RAG :** Poser une question sur un fichier déposé il y a 1 minute. Le système doit répondre en moins de 30 secondes.
- [ ] **Sécurité :** Injecter une commande de suppression dans le prompt. Le `code_scanner` doit lever une alerte.
- [ ] **Purge :** Confirmer que `docker ps -a` ne montre aucun conteneur résiduel après une tâche terminée.

---

## 🚀 8. Lancement Rapide

```bash
#!/bin/bash
echo "--- Initialisation de Bunshin ---"
docker-compose up -d
pip install -r requirements.txt
ollama pull llama3:8b-instruct-q4_K_M
ollama pull nomic-embed-text
echo "Système prêt. Placez vos fichiers dans /workspace/input"
```

```bash
chmod +x setup.sh && ./setup.sh
```
