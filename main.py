import os
import logging
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.errors import GraphInterrupt  # 💡 Import propre de l'exception LangGraph

# Importation de l'orchestrateur Bunshin
from core.orchestrator import create_bunshin_orchestrator

# Configuration de la journalisation globale
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bunshin.api")

app = FastAPI(
    title="BunshinAI API",
    description="Point d'entrée du noyau décisionnel agentique avec interruption HITL",
    version="2.5"
)

# Configuration CORS pour autoriser l'UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schéma de données attendu par l'UI
class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None      # Optionnel pour éviter les erreurs 422 si l'UI ne l'envoie pas
    initial_stage: Optional[int] = 1    # Stage initial (défaut: 1)
    burst_approved: bool = False        # Vaut True si l'utilisateur a cliqué sur le bouton rouge

# Initialisation unique du graphe au lancement de l'API
try:
    logger.info("Compilation du graphe LangGraph Bunshin...")
    orchestrator_graph = create_bunshin_orchestrator()
    logger.info("Graphe compilé et prêt à l'action.")
except Exception as e:
    logger.critical(f"Erreur fatale lors de la compilation du graphe : {str(e)}")
    orchestrator_graph = None

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "LangGraph + Ollama"}

@app.post("/api/predict")
async def predict(request: QueryRequest):
    if not orchestrator_graph:
        raise HTTPException(status_code=500, detail="L'orchestrateur LangGraph n'est pas disponible.")
        
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La requête fournie ne peut pas être vide.")
        
    # Si le Front n'envoie pas de thread_id, on en génère un unique à la volée
    thread_id = request.thread_id or f"local_thread_{uuid.uuid4().hex[:8]}"
    
    # Configuration du thread pour le checkpointer de LangGraph
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # 🔴 CAS A : Approbation Cloud reçue (clic sur le bouton rouge)
        if request.burst_approved:
            logger.info(f"🔴 [BOUTON ROUGE] Autorisation Cloud Bursting validée pour le thread {thread_id}")
            
            # Mise à jour de l'état existant pour franchir la barrière du nœud humain
            orchestrator_graph.update_state(config, {"burst_approved": True, "current_stage": 3})
            
            # Reprise du flux (passer None reprend là où le GraphInterrupt a gelé le fil)
            events = orchestrator_graph.stream(None, config, stream_mode="values")
            final_state = list(events)[-1]
            
            return {
                "status": "success",
                "query": final_state.get("query"),
                "response": final_state.get("response"),
                "final_stage": final_state.get("current_stage"),
                "final_model": final_state.get("current_model"),
                "errors": final_state.get("errors", [])
            }
            
        # 🟢 CAS B : Premier envoi de la requête ou flux standard (Local)
        else:
            initial_state = {
                "query": request.query,
                "current_stage": request.initial_stage,
                "plan": "",
                "response": "",
                "verified": False,
                "burst_approved": False,
                "errors": []
            }
            
            logger.info(f"Nouvelle requête reçue : '{request.query}' sur le thread {thread_id}")
            
            # Utilisation de .stream() pour exécuter correctement avec le checkpointer actif
            events = orchestrator_graph.stream(initial_state, config, stream_mode="values")
            final_state = list(events)[-1]
            
            # Vérification post-exécution : Est-ce que le graphe s'est arrêté sur une demande de validation ?
            state_info = orchestrator_graph.get_state(config)
            if state_info.next and any("human_validation" in node for node in state_info.next):
                raise GraphInterrupt("Interruption HITL déclenchée.")

            return {
                "status": "success",
                "query": final_state.get("query"),
                "response": final_state.get("response", "Aucune réponse générée."),
                "final_stage": final_state.get("current_stage"),
                "final_model": final_state.get("current_model"),
                "errors": final_state.get("errors", [])
            }
            
    except GraphInterrupt:
        # Capturé proprement lorsque LangGraph lève une interruption humaine
        logger.warning(f"⏸️ Graphe suspendu (Stage 3 ciblé) sur le thread {thread_id}. En attente du feu vert de l'UI.")
        return {
            "status": "requires_action",
            "message": "Le mode Cloud Bursting (Modèle 32B) requiert votre validation.",
            "current_stage": 3,
            "thread_id": thread_id,
            "query": request.query
        }
        
    except Exception as e:
        # Sécurité additionnelle si l'interruption remonte sous une autre exception
        state_info = orchestrator_graph.get_state(config)
        if state_info.next and any("human_validation" in node for node in state_info.next):
            logger.warning(f"⏸️ Interruption détectée via inspection d'état sur le thread {thread_id}.")
            return {
                "status": "requires_action",
                "message": "Le mode Cloud Bursting (Modèle 32B) requiert votre validation.",
                "current_stage": 3,
                "thread_id": thread_id,
                "query": request.query
            }
        
        logger.error(f"Erreur lors de l'exécution du graphe : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    import streamlit as st
import time

# Initialisation
if 'manual_cloud_trigger' not in st.session_state:
    st.session_state.manual_cloud_trigger = False

# ... ton code de saisie utilisateur ...

if submit_button:
    st.write("Bunshin analyse, planifie...")
    
    # 1. Appel Qwen (10s)
    response = call_backend_qwen() # Avec timeout 10s interne
    
    if not response:
        # 2. Si Qwen échoue, on lance Phi-3 et on affiche le bouton de secours
        st.warning("Qwen n'a pas trouvé. Phi-3 prend le relais...")
        
        # Affiche le bouton rouge qui n'apparaît qu'après 20s
        placeholder = st.empty()
        start_time = time.time()
        
        while time.time() - start_time < 20:
            placeholder.write(f"En attente de Phi-3... ({int(20 - (time.time() - start_time))}s)")
            time.sleep(1)
            
        # Après 20s, on propose le bouton
        if st.button("🔴 Passer au Cloud (Stage 3)"):
            st.session_state.manual_cloud_trigger = True
            
        # Pendant ce temps, Phi-3 tourne en background (via thread ou asynchrone)
        # Si le résultat de Phi-3 arrive, on l'affiche et on cache le bouton

        import streamlit as st
import requests
import concurrent.futures
import time

def call_backend(query, burst=False):
    # Appel vers ton FastAPI
    return requests.post("http://bunshin_api:8000/api/predict", 
                         json={"query": query, "burst_approved": burst}).json()

if st.button("Envoyer"):
    # 1. Étape Qwen (synchrone)
    with st.spinner("Analyse par Qwen..."):
        res_qwen = call_backend(st.session_state.query)
    
    if res_qwen.get("status") == "success":
        st.write(res_qwen["response"])
    else:
        # 2. Étape Phi-3 (Asynchrone avec ThreadPool)
        st.warning("Qwen a échoué. Phi-3 travaille...")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(call_backend, st.session_state.query)
            
            # On affiche le bouton pendant l'attente
            placeholder = st.empty()
            start_time = time.time()
            
            while not future.done():
                elapsed = time.time() - start_time
                if elapsed > 20: # Après 20s, on affiche le bouton rouge
                    if placeholder.button("🔴 Passer au Cloud (Stage 3)"):
                        # Logique de trigger Cloud ici
                        res_cloud = call_backend(st.session_state.query, burst=True)
                        st.success(res_cloud["response"])
                        return
                
                placeholder.text(f"Phi-3 réfléchit... ({int(elapsed)}s)")
                time.sleep(1)
            
            # Si Phi-3 finit avant le bouton ou sans interruption
            result = future.result()
            st.write(result["response"])