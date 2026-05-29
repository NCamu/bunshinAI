# 🏯 Projet Bunshin (分身) - Documentation Maître (v1.4)

**Architecture de Système Agentique Souverain avec Orchestration Hybride et Optimisation Matérielle.**

---

## 📋 1. Vision et Stratégie d'Optimisation
Bunshin est conçu pour maximiser l'intelligence locale sur une configuration de **16 Go de RAM**. Cette version 1.4 abandonne les services serveurs lourds au profit de solutions **embarquées** et introduit un **ordonnancement séquentiel** pour garantir la stabilité du système MSI Ryzen 7.

- **Souveraineté :** Inférence locale (Ollama) avec déchargement automatique de la RAM.
- **Élasticité :** Cloud Bursting AES-256 uniquement pour les charges dépassant les capacités révisées.
- **Efficience :** Remplacement de Neo4j par Kuzu et de Redis par Diskcache pour libérer ~2 Go de RAM.

---

## 🏗️ 2. Arborescence Totale du Projet (Révisée)

| Fichier / Dossier | Technologie | Rôle & Utilité |
| :--- | :--- | :--- |
| `docker-compose.yml` | **Docker Compose** | Orchestration réduite : Ollama, ChromaDB, UI. |
| `.env` | **Configuration** | `RAM_THRESHOLD=85`, `OLLAMA_KEEP_ALIVE=0`. |
| **`/core/`** | | **Noyau Décisionnel** |
| `├── orchestrator.py` | **LangGraph** | Graphe d'états avec **Queue séquentielle** (un seul agent à la fois). |
| `├── brain.py` | **Ollama / Llama 3** | Inférence locale via CPU (Lazy loading activé). |
| `├── resource_monitor.py` | **psutil** | Monitoring RAM avec seuil de sécurité recalibré. |
| **`/memory/`** | | **Couche Connaissance (Légère)** |
| `├── vector_store/` | **ChromaDB** | Recherche sémantique locale. |
| `├── graph_store/` | **Kuzu DB** | **Graphe embarqué** (Remplace Neo4j) : gain ~1.3 Go RAM. |
| `├── cache/` | **Diskcache** | Cache sur disque (Remplace Redis) : gain ~0.3 Go RAM. |
| `└── ingest_pipeline.py` | **Unstructured.io** | Ingestion avec versionnement par snapshots (JSON). |
| **`/agents_factory/`** | | **Usine à Clones** |
| `├── generator.py` | **RestrictedPython** | Génération de scripts avec **Whitelist d'imports**. |
| `└── executor.py` | **Subprocess / Docker** | Arbitre entre exécution légère (Subprocess) ou lourde (Docker). |
| **`/safety/`** | | **Sécurité Multi-Couches** |
| `├── code_scanner.py` | **Bandit + Whitelist** | Audit statique ET vérification stricte des bibliothèques. |
| `└── validator.py` | **Pydantic** | Validation des schémas de sortie. |

---

## 🤖 3. Architecture des Agents : Le Double Blindage

Pour économiser les ressources, Bunshin utilise désormais deux modes d'exécution :

1. **Mode Light (Subprocess) :** Pour les tâches simples (tri, calcul). Utilise `RestrictedPython` pour isoler l'exécution sans le coût de Docker.
2. **Mode Heavy (Docker) :** Uniquement pour les tâches nécessitant des dépendances complexes (Pandas, Selenium).



### 🛡️ Whitelist d'imports autorisés
Tout script généré par l'IA doit valider cette liste avant exécution :
`ALLOWED_IMPORTS = {"pandas", "json", "csv", "pathlib", "re", "math", "datetime"}`

---

## 🔄 4. Gestion de la Mémoire et Erreurs

### Stratégie de "Lazy Loading" (Ollama)
Pour éviter la saturation, le modèle n'est pas maintenu en mémoire.
- Configuration : `OLLAMA_KEEP_ALIVE=0`.
- Impact : Le modèle se décharge après chaque requête, libérant ~5.5 Go pour les autres tâches système.

### Résilience et Erreurs
- **Erreur d'inférence :** En cas de plantage d'Ollama, l'orchestrateur effectue deux tentatives de redémarrage du service avant de basculer automatiquement la tâche spécifique vers le Cloud (Bursting).
- **Intégrité du Graphe :** Un snapshot JSON de la base Kuzu est créé après chaque session d'ingestion majeure pour prévenir la corruption.

---

## 🛠️ 5. Guide d'Implémentation Pas à Pas

### Étape 1 : Infrastructure Minimale
Configurez le `docker-compose.yml`. Notez l'absence de Neo4j et Redis pour préserver la RAM.
```yaml
services:
  chromadb:
    image: chromadb/chroma:latest
    volumes: [ ./memory/vector_store:/index_data ]
  ollama:
    image: ollama/ollama:latest
    deploy:
      resources:
        reservations:
          devices: [{driver: nvidia, count: all, capabilities: [compute, utility]}] # Optionnel si GPU présent
Étape 2 : Configuration du Graphe Embarqué (Kuzu)
Remplacez votre client Neo4j par Kuzu :

Python
import kuzu
db = kuzu.Database('./memory/graph_store')
conn = kuzu.Connection(db)
# Utilise le Cypher standard, mais sans serveur actif en arrière-plan.
Étape 3 : Le Moniteur de Ressources Recalibré
Le seuil de 2 Go de RAM libre est désormais le point de bascule vers le mode séquentiel strict :

Si RAM libre < 2 Go : Mise en attente de tout nouvel agent.

Si RAM libre < 1 Go : Cloud Bursting immédiat pour la tâche en cours.

✅ 6. Checklist de Validation Finale (Révisée)
[ ] Persistance Kuzu : Vérifier que les relations graphes sont lisibles après fermeture du script Python.

[ ] Lazy Loading : Confirmer via le gestionnaire de tâches que la RAM d'Ollama redescend après 5 min d'inactivité.

[ ] Whitelist : Tenter d'importer os ou shutil dans un agent (doit être bloqué par le code_scanner).

[ ] File d'attente : Lancer deux requêtes complexes et vérifier qu'elles s'exécutent l'une après l'autre.

🚀 7. Lancement Rapide
Bash
#!/bin/bash
echo "--- Initialisation de Bunshin v1.4 (Mode Optimisé) ---"
docker-compose up -d
pip install langgraph psutil kuzu diskcache RestrictedPython pydantic-ai
ollama pull llama3:8b-instruct-q4_K_M
echo "Système prêt. Mode 'Séquentiel Strict' activé par défaut."
