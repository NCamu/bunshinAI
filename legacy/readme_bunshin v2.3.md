🏯 Bunshin (分身) — Documentation Maître v2.3
Architecture : Système Agentique Souverain avec Orchestration Hybride et Optimisation RAM.
Cible matérielle : MSI Ryzen 7 7730U · 16 Go RAM · Mode CPU-only.

📋 Table des matières
Vision & Stratégie

Arborescence du projet

Schéma de flux

Décision architecturale — Images UI

Infrastructure Docker

Noyau décisionnel

Interface utilisateur

Mémoire RAG & Graphe

Module Cloud Bursting

Sécurité & Anonymisation

Agents Factory

Initialisation (setup.sh)

Configuration (.env.example)

Dépendances

Modes d'exécution des agents

Tests unitaires

Guide de démarrage rapide

Historique des corrections

Checklist de validation

1. Vision & Stratégie
   Bunshin maximise l'intelligence locale sur 16 Go de RAM tout en disposant d'une soupape Cloud pour les surcharges.

Principe Décision technique Gain RAM estimé
Souveraineté Inférence locale via Ollama + KEEP_ALIVE=0 ~5.5 Go libérés entre requêtes
Légèreté Kuzu DB embarqué (remplace Neo4j) ~1.3 Go
Légèreté Diskcache sur disque (remplace Redis) ~0.3 Go
Séquençage MAX_CONCURRENT_AGENTS=1 câblé via asyncio.Semaphore Évite les pics cumulés
Élasticité Cloud Bursting AES-256 si RAM libre < 1 Go + retry exponentiel —
Résilience AGENT_TIMEOUT=45 + cleanup finally containers Docker Zéro container zombie 2. Arborescence du projet
text
/Bunshin/
├── docker-compose.yml # logging: rotation 10m × 3 fichiers sur tous les services
├── .env # ⚠️ Ne jamais commiter
├── .env.example
├── .gitignore # .env, memory/, logs/, workspace/ exclus
├── requirements.txt # Env Docker complet (spacy>=3.7.0 inclus)
├── requirements-host.txt # Hôte minimal : kuzu, psutil, pytest, ollama, langgraph
├── setup.sh
│
├── core/
│ ├── **init**.py
│ ├── orchestrator.py # LangGraph : CLOUD_CHECK → PLAN → EXECUTE → VERIFY
│ │ # NEW v2.3 : cloud_check_node câblé
│ │ # FIX v2.2 : route_after_verify < MAX_RETRIES
│ ├── brain.py # Lazy Loading + gestion ConnectionError/404
│ └── resource_monitor.py # should_offload_to_cloud() → RAM libre < 1 Go
│
├── ui/
│ ├── **init**.py
│ ├── Dockerfile.api # context: . (racine) + python -m spacy download fr_core_news_md
│ ├── Dockerfile.streamlit
│ ├── app.py # NEW v2.3 : affichage coût Cloud via GET /cost
│ └── api_rest.py # NEW v2.3 : endpoint GET /cost ajouté
│
├── agents_factory/
│ ├── **init**.py
│ ├── generator.py # \_extract_imports() : ast.Import + ast.ImportFrom
│ └── executor.py # FIX v2.2 : get_running_loop() + finally kill Heavy
│
├── memory/
│ ├── **init**.py
│ ├── graph_store/ # Kuzu DB (volume Docker persisté)
│ ├── vector_store/ # ChromaDB (volume Docker persisté)
│ ├── cache/ # Diskcache embeddings TTL 30j (volume Docker persisté)
│ └── ingest_pipeline.py # FIX v2.2 : \_embed_one() + import hashlib + dry_run
│
├── cloud/
│ ├── **init**.py
│ ├── bridge.py # FIX v2.2 : ValueError si ENCRYPTION_KEY absente
│ ├── cost_tracker.py # log_cost() → logs/cloud_costs.jsonl
│ └── providers/
│ ├── **init**.py
│ ├── base.py # NEW v2.3 : CloudProvider ABC + send_task_safe()
│ └── runpod_adapter.py # NEW v2.3 : POST /run + poll_until_done() + retry
│
├── safety/
│ ├── **init**.py
│ ├── code_scanner.py # FIX v2.2 : scan_imports() implémentée (AST + Bandit)
│ └── de_identifier.py # Presidio fr — anonymize() / reidentify()
│
└── tests/
├── **init**.py
├── unit/
│ ├── **init**.py
│ ├── test_brain.py
│ ├── test_orchestrator_nodes.py
│ ├── test_cost_tracker.py
│ ├── test_ingest.py
│ ├── test_code_scanner.py
│ └── test_resource_monitor.py
└── security/
├── **init**.py
└── test_sandbox_escape.py
⚠️ Les **init**.py sont obligatoires dans chaque dossier pour que Python les reconnaisse comme des packages. Sans eux, tous les import core.brain, import cloud.bridge, etc. lèvent un ModuleNotFoundError.

3.  Schéma de flux : Cycle de vie d'une requête
    text
    flowchart TD
    A([👤 Prompt utilisateur\nStreamlit / API REST]) --> SEM[asyncio.Semaphore\nMAX_CONCURRENT_AGENTS=1]
    SEM --> CC[cloud_check_node\nNEW v2.3]
    CC --> RAM{RAM libre > 1 Go ?}

        RAM -- NON --> CLOUD[☁️ Cloud Bursting]
        CLOUD --> C0[Snapshot Kuzu → kuzu_snapshot.json]
        C0 --> C1[Gel state LangGraph → JSON]
        C1 --> C2[de_identifier.py\nAnonymisation Presidio]
        C2 --> C3[bridge.py\nChiffrement AES-256\nTable Fernet → RAM]
        C3 --> C4[runpod_adapter.py\nPOST /run → polling /status/id\nRetry exponentiel si failed]
        C4 --> C5[Résultat reçu\nDéchiffrement]
        C5 --> C6[Ré-identification\n+ finally: suppression table + snapshot]
        C6 --> C7[cost_tracker.py\nLog coût USD → cloud_costs.jsonl]
        C7 --> OUT

        RAM -- OUI --> LOCAL[🧠 brain.py\nOllama llama3:8b-q4]
        LOCAL --> PLAN[plan_node]
        PLAN --> EXEC[execute_node\ngenerator.py + executor.py]
        EXEC --> VERIFY[verify_node\nmax 2 retries]
        VERIFY --> OUT([✅ Résultat → UI])

        style CLOUD fill:#dc2626,color:#fff
        style OUT fill:#16a34a,color:#fff
        style CC fill:#7c3aed,color:#fff
        style LOCAL fill:#0369a1,color:#fff

4.  Décision architecturale — Images UI
    Option Avantages Inconvénients RAM estimée
    A — Deux images séparées ✅ Isolation totale, healthcheck précis, redémarrage ciblé Deux builds ~360 Mo
    B — supervisor Un seul build Si Streamlit crash, FastAPI reste sans raison ~200 Mo
    C — honcho Simple Procfile Supervision partielle ~190 Mo
    Décision retenue : Option A. Sur 16 Go de RAM, la différence est négligeable. L'isolation garantit des logs séparés et un healthcheck fiable par service.

5.  Infrastructure Docker
    ⚠️ Docker Compose v2 requis. Commande : docker compose (sans tiret).

docker-compose.yml
text
services:
chromadb:
image: chromadb/chroma:latest
restart: unless-stopped
volumes: - ./memory/vector_store:/index_data
ports: - "8001:8000"
healthcheck:
test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
interval: 15s
timeout: 5s
retries: 3
logging:
driver: "json-file"
options:
max-size: "10m"
max-file: "3"

ollama:
image: ollama/ollama:latest
restart: unless-stopped
ports: - "11434:11434"
volumes: - ollama_models:/root/.ollama
environment: - OLLAMA_KEEP_ALIVE=0
healthcheck:
test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
interval: 10s
timeout: 5s
retries: 5
start_period: 20s
logging:
driver: "json-file"
options:
max-size: "10m"
max-file: "3"

fastapi_backend:
build:
context: . # Racine — accès à core/, memory/, safety/, cloud/
dockerfile: ui/Dockerfile.api
restart: unless-stopped
ports: - "8000:8000"
depends_on:
chromadb:
condition: service_healthy
ollama:
condition: service_healthy
env_file: .env
volumes: - ./memory/graph_store:/app/memory/graph_store # Kuzu persisté - ./memory/cache:/app/memory/cache # Diskcache persisté - ./logs:/app/logs - ./workspace:/app/workspace
healthcheck:
test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
interval: 15s
timeout: 5s
retries: 3
logging:
driver: "json-file"
options:
max-size: "10m"
max-file: "3"

streamlit_ui:
build:
context: ./ui
dockerfile: Dockerfile.streamlit
restart: unless-stopped
ports: - "3000:3000"
depends_on:
fastapi_backend:
condition: service_healthy
volumes: - ./workspace:/app/workspace - ./logs:/app/logs # Logs Safety visibles dans le dashboard
env_file: .env
logging:
driver: "json-file"
options:
max-size: "10m"
max-file: "3"

volumes:
ollama_models:
Référence des ports
Service Port hôte Accès
Streamlit UI 3000 http://localhost:3000
FastAPI 8000 http://localhost:8000/docs
ChromaDB 8001 http://localhost:8001 (debug)
Ollama 11434 http://localhost:11434 (debug) 6. Noyau décisionnel (core/)
orchestrator.py — Graphe LangGraph v2.3
Le graphe comporte maintenant 4 nœuds : cloud_check → plan → execute → verify.

text
Entrée
└─► cloud_check_node ← NEW v2.3 — point d'entrée
├─ RAM OK ──────────────────► plan_node
│ └─► execute_node
│ └─► verify_node
│ ├─ ok ──► END
│ └─ retry ──► plan_node
└─ RAM critique + CLOUD_ENABLED=true
└─► bridge.offload()
├─ succès ──► END (court-circuit)
└─ erreur ──► plan_node (fallback local silencieux)
cloud_check_node — Nouveau nœud d'entrée (v2.3). Appelle should_offload_to_cloud() (RAM < 1 Go). Si vrai et CLOUD_ENABLED=true, sérialise l'état en JSON et appelle bridge.offload(). En cas d'erreur Cloud (CLOUD_ERROR: ou ImportError), fallback silencieux vers le chemin local — l'utilisateur n'est jamais bloqué.

route_after_verify — FIX v2.2 : comparaison stricte < MAX_RETRIES. L'ancienne version <= causait une boucle infinie quand retry_count == MAX_RETRIES : verify_node avait déjà écrit [DÉGRADÉ] mais le routeur renvoyait encore "retry".

resource_monitor.py
python
def should_offload_to_cloud() -> bool:
return psutil.virtual_memory().available / (1024 \*_ 3) < 1.0 7. Interface utilisateur (ui/)
Endpoints FastAPI (api_rest.py)
Méthode Route Description
GET /health Liveness probe Docker
GET /ram Métriques RAM (total, libre, offload_required)
GET /cost NEW v2.3 — Coût Cloud cumulatif en USD
POST /chat Envoie un prompt à l'orchestrateur
POST /ingest Ingestion document (file_path, mode, dry_run)
POST /reset Vide ChromaDB + Kuzu
Dashboard Streamlit (app.py)
text
┌────────────────────────────────┬──────────────────────────────────┐
│ 💬 Chat │ 📊 Monitoring RAM │
│ > question │ ████████░░ 78% │
│ 🤖 réponse │ Libre : 3.2 Go / 16 Go │
│ │ Cloud Bursting : 🟢 OFF │
│ ───────────────────────── │ 💸 Coût Cloud ce mois : $0.0023 │
│ 📄 Ingestion │ ← NEW v2.3 │
│ Chemin du fichier ├──────────────────────────────────┤
│ Mode : hybrid ▾ │ 📋 Logs Safety │
│ □ Dry-run │ [INFO] Agent validé (retry 0/2) │
│ [Ingérer 📥] │ ─────────────────────────────── │
│ │ 🔄 Reset mémoire │
└────────────────────────────────┴──────────────────────────────────┘
ui/Dockerfile.api
text
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential curl libmagic1 && rm -rf /var/lib/apt/lists/_
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download fr_core_news_md
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "ui.api_rest:app", "--host", "0.0.0.0", "--port", "8000"]
ui/Dockerfile.streamlit
text
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit requests psutil
COPY app.py .
EXPOSE 3000
CMD ["streamlit", "run", "app.py", "--server.port=3000", "--server.address=0.0.0.0"] 8. Mémoire RAG & Graphe (memory/)
Modèles
Rôle Modèle Variable
Inférence llama3:8b-instruct-q4_K_M INFERENCE_MODEL
Embeddings nomic-embed-text EMBEDDING_MODEL
Cache diskcache — Zéro ré-embedding
Clé = MD5 du chunk. TTL = 30 jours. Stocké dans memory/cache/ — zéro RAM.

Commandes CLI
bash

# Ingestion complète

python memory/ingest_pipeline.py --file ./workspace/input/rapport.pdf --mode hybrid

# Dry-run (affiche chunks sans persister)

python memory/ingest_pipeline.py --file ./workspace/input/test.pdf --mode hybrid --dry-run

# Reset complet

docker compose down -v
rm -rf ./memory/vector_store ./memory/graph_store ./memory/cache
./setup.sh && docker compose up -d
⚠️ Migration Kuzu : aucune procédure automatique. Si le schéma évolue, reset complet requis.

9.  Module Cloud Bursting (cloud/)
    cloud/providers/base.py — NEW v2.3
    python
    class CloudProvider(ABC):
    @abstractmethod
    def send_task(self, encrypted_payload: bytes) -> str: ...
    @abstractmethod
    def get_result(self, task_id: str) -> dict: ...
    @abstractmethod
    def estimate_cost(self, payload_size_bytes: int) -> float: ...
    @abstractmethod
    def poll_until_done(self, task_id: str) -> dict: ...

        def send_task_safe(self, encrypted_payload: bytes) -> str:
            """Garde-fou budgétaire — lève RuntimeError si CLOUD_COST_LIMIT_USD dépassé."""
            from cloud.cost_tracker import get_total_cost
            total = get_total_cost()
            estimated = self.estimate_cost(len(encrypted_payload))
            if total + estimated > CLOUD_COST_LIMIT_USD:
                raise RuntimeError(f"Budget Cloud dépassé : {total:.4f} + {estimated:.4f} USD")
            return self.send_task(encrypted_payload)

    cloud/providers/runpod_adapter.py — NEW v2.3
    python
    class RunPodAdapter(CloudProvider):

        def send_task(self, encrypted_payload: bytes) -> str:
            """POST /run → retourne le task_id RunPod."""

        def get_result(self, task_id: str) -> dict:
            """GET /status/{task_id} — poll unique.
            Retourne {"status": "completed|pending|failed", "result": bytes | None}"""

        def poll_until_done(self, task_id: str) -> dict:
            """Polling toutes les 2s, timeout AGENT_TIMEOUT secondes."""

        def estimate_cost(self, payload_size_bytes: int) -> float:
            """~$0.0002 par Ko (GPU A40)."""

    Processus de bascule complet
    text
    resource_monitor → RAM libre < 1 Go
    ↓
    cloud_check_node → should_offload_to_cloud() == True
    ↓

10. bridge.offload() → Snapshot Kuzu → logs/kuzu*snapshot*{ts}.json
    ↓
11. de_identifier → Anonymisation Presidio — "Jean Dupont" → [PERSON_1]
    ↓
12. bridge.py → Chiffrement AES-256 (Fernet)
    │ FIX v2.2 : ValueError si ENCRYPTION_KEY absente
    ↓
13. RunPodAdapter.send_task_safe() → garde-fou budget
    ↓
14. poll_until_done() → polling /status/{id} toutes 2s
    │ retry exponentiel : 2s → 4s → 8s
    ↓
15. Déchiffrement + ré-identification (finally: suppression table + snapshot)
    ↓
16. cost_tracker.log_cost() → logs/cloud_costs.jsonl
    ↓
17. Résultat retourné à l'orchestrateur → state.verified = True
    cloud/bridge.py — Clé de chiffrement
    python

# FIX v2.2 — Exception explicite si ENCRYPTION_KEY absente

\_raw_key = os.getenv("ENCRYPTION_KEY")
if not \_raw_key:
raise ValueError(
"ENCRYPTION_KEY manquante dans .env. "
"Génère-la : python -c \"from cryptography.fernet import Fernet; "
"print(Fernet.generate_key().decode())\""
)
FERNET = Fernet(\_raw_key.encode()) 10. Sécurité & Anonymisation (safety/)
safety/de_identifier.py — Presidio français
⚠️ Requiert fr_core_news_md. Installé par setup.sh (hôte) et Dockerfile.api (Docker).

python
SUPPORTED_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "ORG"]

def anonymize(text: str) -> tuple[str, dict]:
"""Retourne (texte_anonymisé, table). La table doit être détruite dans un finally."""

def reidentify(text: str, table: dict) -> str:
"""Ré-identifie depuis la table. Appeler dans finally."""
safety/code_scanner.py — Whitelist AST + Bandit
python
WHITELIST_LIGHT = {"json", "math", "re", "csv", "pathlib", "datetime"}
WHITELIST_HEAVY = {"pandas", "numpy", "scipy", "bs4"}
BLOCKED_ALWAYS = {"os", "sys", "subprocess", "shutil", "socket", "ctypes", "requests"}

def scan_imports(code: str) -> bool:
"""FIX v2.2 — implémentée. True = sûr, False = bloqué ou hors whitelist."""

def full_scan(code: str) -> tuple[bool, str]:
"""scan_imports() + Bandit. Retourne (ok, rapport).""" 11. Agents Factory (agents_factory/)
executor.py
python

# FIX v2.2 — get_running_loop() (get_event_loop() déprécié Python 3.10+)

loop = asyncio.get_running_loop()

# FIX v2.2 — finally kill : zéro container zombie

finally:
if proc.returncode is None:
proc.kill(); await proc.wait()
generator.py — Détection mode
python
def \_extract_imports(code: str) -> set[str]:
"""Gère ast.Import ET ast.ImportFrom.
'from pandas import DataFrame' → détecte 'pandas' correctement.""" 12. Initialisation (setup.sh)
bash
#!/bin/bash
set -e

# [1/6] Répertoires

mkdir -p workspace/input workspace/output memory/graph_store memory/vector_store memory/cache logs

# [2/6] Docker

docker info > /dev/null 2>&1 || { echo "❌ Docker non actif."; exit 1; }
docker compose version --short > /dev/null 2>&1 || { echo "❌ Docker Compose v2 requis."; exit 1; }

# [3/6] Dépendances hôte

pip install -r requirements-host.txt --quiet
pip install "spacy>=3.7.0" --quiet
python -m spacy download fr_core_news_md

# [4/6] Kuzu DB — schémas

python3 -c "
import kuzu
db = kuzu.Database('./memory/graph_store')
conn = kuzu.Connection(db)
conn.execute('CREATE NODE TABLE IF NOT EXISTS Entity (id STRING, label STRING, PRIMARY KEY(id))')
conn.execute('CREATE NODE TABLE IF NOT EXISTS Document (id STRING, title STRING, ingested_at STRING, PRIMARY KEY(id))')
conn.execute('CREATE REL TABLE IF NOT EXISTS MENTIONS (FROM Document TO Entity)')
"

# [5/6] Pull modèles Ollama

docker compose up -d ollama

# ... polling healthcheck ...

OLLAMA_CID=$(docker compose ps -q ollama)
docker exec "$OLLAMA_CID" ollama pull "${INFERENCE_MODEL:-llama3:8b-instruct-q4_K_M}"
docker exec "$OLLAMA_CID" ollama pull "${EMBEDDING_MODEL:-nomic-embed-text}" 13. Configuration (.env.example)
text

# ── RESSOURCES ──────────────────────────────────────────────────────────────

RAM_THRESHOLD=0.85
RAM_CRITICAL=0.94
OLLAMA_KEEP_ALIVE=0
MAX_CONCURRENT_AGENTS=1
AGENT_TIMEOUT=45

# ── MODÈLES ─────────────────────────────────────────────────────────────────

INFERENCE_MODEL=llama3:8b-instruct-q4_K_M
EMBEDDING_MODEL=nomic-embed-text

# ── MÉMOIRE ─────────────────────────────────────────────────────────────────

CHROMA_SERVER_HOST=chromadb
CHROMA_SERVER_PORT=8000
KUZU_PATH=./memory/graph_store
CACHE_PATH=./memory/cache

# ── CLOUD BURSTING ──────────────────────────────────────────────────────────

CLOUD_ENABLED=true
CLOUD_PROVIDER=runpod
RUNPOD_API_KEY=your_key_here
CLOUD_ENDPOINT=https://api.runpod.ai/v2/

# Génère : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

ENCRYPTION_KEY=your_fernet_key_here
CLOUD_COST_LIMIT_USD=0.10
CLOUD_MAX_RETRIES=3

# ── SÉCURITÉ ────────────────────────────────────────────────────────────────

PII_REDACTION=true
WHITELIST_LEVEL=strict
LOG_LEVEL=INFO
LOG_DIR=./logs

# ── API & UI ────────────────────────────────────────────────────────────────

API_BASE_URL=http://fastapi_backend:8000

# FIX v2.2 — localhost dans Docker = le container lui-même, pas Ollama

OLLAMA_HOST=http://ollama:11434 14. Dépendances
requirements.txt
text
langgraph>=0.1.0
langchain-core>=0.2.0
ollama>=0.2.0
chromadb>=0.5.0
kuzu>=0.4.0
diskcache>=5.6.0
unstructured[pdf]>=0.14.0
pandas>=2.0.0
RestrictedPython>=7.0
bandit>=1.7.0
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0
spacy>=3.7.0
pydantic>=2.0.0
cryptography>=42.0.0
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
streamlit>=1.35.0
requests>=2.32.0
psutil>=5.9.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
requirements-host.txt
text
kuzu>=0.4.0
psutil>=5.9.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
ollama>=0.2.0
langgraph>=0.1.0
langchain-core>=0.2.0 15. Modes d'exécution des agents
Mode Technologie Imports autorisés Réseau Timeout
Light run_in_executor + RestrictedPython json math re csv pathlib datetime Aucun 45s
Heavy Docker Alpine --read-only + finally: kill pandas numpy scipy bs4 --network=none 45s
requests est dans BLOCKED_ALWAYS — incompatible avec --network=none.

16. Tests unitaires (tests/unit/)
    text
    tests/
    ├── unit/
    │ ├── test_brain.py # Mock OllamaClient + ConnectionError + 404 + singleton
    │ ├── test_orchestrator_nodes.py # plan/verify/route_after_verify + régression bug <=
    │ ├── test_cost_tracker.py # log_cost() + get_total_cost() + JSONL
    │ ├── test_ingest.py # dry_run + cache embedding (mock \_embed_one)
    │ ├── test_code_scanner.py # import x + from x import y + full_scan
    │ └── test_resource_monitor.py # get_free_ram_gb + should_offload + get_ram_status
    └── security/
    └── test_sandbox_escape.py # 8 payloads d'évasion — tous bloqués
    Lancer les tests
    bash

# Dépendances hôte

pip install -r requirements-host.txt

# Tests unitaires (sans Docker)

pytest tests/unit/ -v

# Tests sécurité

pytest tests/security/ -v
Test clé — régression route_after_verify
python
def test_route_not_verified_at_max_returns_end():
"""
FIX v2.2 — retry_count == MAX_RETRIES doit retourner 'end', pas 'retry'.
"""
state = AgentState(prompt="test", verified=False, retry_count=MAX_RETRIES)
assert route_after_verify(state) == "end"
Test clé — Cloud Bursting câblé (v2.3)
python
async def test_cloud_check_offloads_when_ram_critical():
"""v2.3 — cloud_check_node appelle bridge.offload() si RAM critique."""
with patch("core.orchestrator.should_offload_to_cloud", return_value=True), \
 patch("core.orchestrator.CLOUD_ENABLED", True), \
 patch("cloud.bridge.offload", return_value="résultat_cloud") as mock_offload:
state = AgentState(prompt="test")
result = await cloud_check_node(state)
mock_offload.assert_called_once()
assert result.verified is True
assert result.result == "résultat_cloud" 17. Guide de démarrage rapide
bash

# 1. Cloner et configurer

git clone https://github.com/votre-repo/bunshin.git && cd bunshin
cp .env.example .env

# 2. Remplir .env — obligatoire avant de continuer

# RUNPOD_API_KEY=...

# ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# 3. Initialiser (répertoires + spaCy + Kuzu + Ollama pull)

bash setup.sh

# 4. Démarrer tous les services

docker compose up -d

# 5. Vérifier que les 4 services sont healthy

docker compose ps

# 6. Tests unitaires (sans Docker)

pytest tests/unit/ -v

# 7. Ingestion d'un document

python memory/ingest_pipeline.py --file ./workspace/input/doc.pdf --mode hybrid

# 8. Accéder à l'UI

# Dashboard : http://localhost:3000

# API docs : http://localhost:8000/docs

# Coût Cloud: curl http://localhost:8000/cost

Reset complet
bash
docker compose down -v
rm -rf ./memory/vector_store ./memory/graph_store ./memory/cache
bash setup.sh && docker compose up -d 18. Historique des corrections
🔴 v2.2 — Bloquant (projet ne démarrait pas)

# Fichier Bug Correction

1 requirements.txt spacy absent → RUN spacy download plantait spacy>=3.7.0 ajouté
2 .env.example OLLAMA_HOST=http://localhost:11434 — dans Docker = le container lui-même → http://ollama:11434
3 ui/Dockerfile.api Context ./ui → pas d'accès à core/, memory/, safety/ Context corrigé en . (racine)
4 docker-compose.yml fastapi_backend sans volumes memory/ → Kuzu et cache éphémères Volumes graph_store, cache, logs montés
5 core/orchestrator.py retry_count <= MAX_RETRIES → boucle infinie → < MAX_RETRIES (strict)
6 ui/app.py Seulement ASCII art — aucun code Streamlit Dashboard complet
7 ui/Dockerfile.streamlit Absent (référencé dans compose) Créé
8 ui/api_rest.py ChatRequest et IngestRequest non définies → NameError Modèles Pydantic ajoutés
🟡 v2.2 — Important (démarrait mais fonctions cassées)

# Fichier Bug Correction

9 memory/ingest_pipeline.py \_embed_one() non définie + import hashlib manquant Implémentée + import ajouté
10 safety/code_scanner.py scan_imports() non implémentée AST + Bandit
11 agents_factory/executor.py get_event_loop() déprécié Python 3.10+ → get_running_loop()
12 cloud/bridge.py Fernet.generate_key() silencieux → clé différente à chaque restart ValueError explicite
13 ui/api_rest.py /ingest synchrone bloquait l'event loop run_in_executor
14 ui/api_rest.py Pas de CORSMiddleware Ajouté
15 requirements-host.txt ollama, langgraph, langchain-core absents Ajoutés
🔴 v2.3 — Bloquant (Cloud Bursting non fonctionnel)

# Fichier Bug Correction

16 cloud/providers/runpod_adapter.py Absent — ImportError au premier appel Cloud Créé (polling + retry)
17 cloud/providers/base.py Absent — CloudProvider ABC non définie Créé (ABC + send_task_safe)
18 core/orchestrator.py Cloud Bursting documenté mais jamais appelé dans le code cloud_check_node câblé en entrée du graphe
🟡 v2.3 — Important

# Fichier Bug Correction

19 ui/api_rest.py GET /cost absent — coût non exposé Endpoint ajouté
20 ui/app.py Coût affiché dans la maquette mais non récupéré Appel GET /cost ajouté
21 docker-compose.yml (README) Directives logging: absentes de la doc Ajoutées dans tous les services
22 Arborescence README **init**.py non listés → développeur les oublie Listés avec note explicative
🟢 v2.2/v2.3 — Non bloquant

# Action

23 .gitignore créé
24 cloud/providers/de_identifier.py (doublon) supprimé
25 dry_run transmis dans le payload /ingest 19. Checklist de validation
Infrastructure
docker compose ps → 4 services healthy

http://localhost:3000 → dashboard accessible, jauge RAM visible, coût Cloud visible

curl http://localhost:8000/health → {"status": "ok"}

curl http://localhost:8000/cost → {"total_usd": 0.0}

curl http://localhost:8000/docs → Swagger avec /chat, /ingest, /ram, /reset, /cost

Cloud Bursting (v2.3)
cloud/providers/base.py présent — from cloud.providers.base import CloudProvider ne lève pas d'erreur

cloud/providers/runpod_adapter.py présent — from cloud.providers.runpod_adapter import RunPodAdapter ne lève pas d'erreur

core/orchestrator.py importe should_offload_to_cloud et bridge.offload

cloud_check_node est le set_entry_point du graphe

Démarrer sans ENCRYPTION_KEY → ValueError explicite au boot FastAPI

CLOUD_ENABLED=false dans .env → cloud_check_node passe sans appeler bridge

Corrections logiques
Prompt générant un résultat vide → [DÉGRADÉ] après exactement 2 retries (pas de boucle infinie)

dry_run=true dans /ingest → rien n'est persisté dans ChromaDB ni Kuzu

Kuzu et Diskcache survivent à docker compose restart fastapi_backend

logs/cloud_costs.jsonl : chaque appel Cloud ajoute une ligne JSON

Tests
pytest tests/unit/ -v → 100% vert sans Docker

pytest tests/security/ -v → 8 payloads d'évasion tous bloqués

test_route_not_verified_at_max_returns_end passe

test_cloud_check_offloads_when_ram_critical passe

Sécurité
git status → .env absent (.gitignore actif)

scan_imports("import os") → False

scan_imports("import math") → True

Bunshin v2.3 · Architecture Agentique Souverain · MSI Ryzen 7 7730U · 2026

Préparé avec Claude Sonnet 4.6 Thinking
