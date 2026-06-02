import os
import streamlit as st
import requests

# 1. Configuration de la page (Unique et au tout début !)
st.set_page_config(
    page_title="Bunshin-AI — Assistant Agentique",
    page_icon="🏯",
    layout="wide"
)

# Initialisation des variables de session indispensables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "show_burst_button" not in st.session_state:
    st.session_state.show_burst_button = False
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# 2. Barre latérale (Sidebar) - Suivi de l'infra & Configuration des paliers
st.sidebar.markdown("### ⚙️ Configuration de l'Inférence")

config_choice = st.sidebar.radio(
    "Choisir la stratégie de départ :",
    options=[
        "1. Mode Minimal (Qwen 1.5B)",
        "2. Mode Intermédiaire (Phi-3 Mini)",
        "3. Mode Cloud Direct (Qwen 32B)"
    ],
    index=0  # Par défaut sur le Mode Minimal (1.5B)
)

# Extraction de l'index numérique du stage (1, 2 ou 3)
initial_stage = int(config_choice.split(".")[0])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖥️ Suivi de l'infrastructure")
st.sidebar.success("Conteneur UI actif")
if st.session_state.thread_id:
    st.sidebar.info(f"🧵 Thread ID : `{st.session_state.thread_id}`")

# 3. En-tête principal de l'application
st.title("🏯 BunshinAI — Assistant Agentique")
st.caption("Architecture hybride locale (Ollama) & Déportée (Cloud Bursting avec cascade de Timeout)")

# URL du conteneur API FastAPI (via le réseau Docker) alignée sur main.py
API_URL = os.getenv("BACKEND_URL", "http://bunshin_api:8000/api/predict")

# Affichage des messages de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "metadata" in message and message["metadata"]:
            st.caption(message["metadata"])

# 4. Zone d'entrée utilisateur (Format Chat)
# Désactivé temporairement si le bouton rouge attend une validation
if user_query := st.chat_input("Posez votre question à BunshinAI...", disabled=st.session_state.show_burst_button):
    
    # Sauvegarde de la requête actuelle
    st.session_state.last_query = user_query
    
    # Affichage immédiat du message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Zone de réponse de l'assistant avec conteneurs dynamiques
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        metadata_placeholder = st.empty()
        
        with st.spinner("Bunshin analyse, planifie et orchestre la cascade de modèles..."):
            try:
                # Préparation du Payload avec transmission du thread_id s'il existe
                payload = {
                    "query": user_query,
                    "thread_id": st.session_state.thread_id,
                    "initial_stage": initial_stage,
                    "burst_approved": False
                }
                
                # Envoi de la requête au backend FastAPI
                response = requests.post(API_URL, json=payload, timeout=300)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # CAS A : Le graphe a été gelé et requiert une validation humaine
                    if data.get("status") == "requires_action":
                        st.session_state.thread_id = data.get("thread_id")
                        st.session_state.show_burst_button = True
                        
                        warning_text = f"⏸️ **Système Suspendu :** {data.get('message')}"
                        response_placeholder.warning(warning_text)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": warning_text,
                            "metadata": "Statut: Interruption HITL"
                        })
                        st.rerun() # Force Streamlit à rafraîchir pour afficher le bouton rouge
                        
                    # CAS B : Succès direct du traitement local
                    else:
                        output_text = data.get("response", "")
                        final_stage = data.get("final_stage", 1)
                        final_model = data.get("final_model", "Inconnu")
                        st.session_state.thread_id = data.get("thread_id")
                        
                        if final_stage > initial_stage:
                            metadata_text = f"⚠️ **Burst automatique actif !** Dépassé le timeout local ➡️ Réponse validée au Stage {final_stage} ({final_model})"
                        else:
                            metadata_text = f"✅ Réponse traitée au point de départ choisi : Stage {final_stage} ({final_model})"
                        
                        # Rendu visuel dans l'UI
                        response_placeholder.markdown(output_text)
                        metadata_placeholder.caption(metadata_text)
                        
                        # Sauvegarde dans l'historique
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": output_text,
                            "metadata": metadata_text
                        })
                else:
                    response_placeholder.error(f"❌ Erreur API ({response.status_code}) : {response.text}")
                    
            except requests.exceptions.ConnectionError:
                response_placeholder.error("❌ Impossible de contacter le serveur backend BunshinAI. Vérifiez le conteneur 'bunshin_api'.")
            except Exception as e:
                response_placeholder.error(f"❌ Une erreur inattendue est survenue : {str(e)}")

# 5. Affichage du Bouton Rouge de débrayage Cloud (HITL)
if st.session_state.show_burst_button:
    st.write("") # Espacement visuel
    col_btn, col_txt = st.columns([1, 3])
    
    with col_btn:
        if st.button("🔴 ACTIVER LE CLOUD BURSTING", type="primary", use_container_width=True):
            with st.chat_message("assistant"):
                res_placeholder = st.empty()
                meta_placeholder = st.empty()
                
                with st.spinner("Appel des infrastructures distantes (Modèle 32B)..."):
                    try:
                        payload = {
                            "query": st.session_state.last_query,
                            "thread_id": st.session_state.thread_id,
                            "initial_stage": 3,
                            "burst_approved": True # Débloque la barrière LangGraph
                        }
                        
                        response = requests.post(API_URL, json=payload, timeout=300)
                        
                        if response.status_code == 200:
                            data = response.json()
                            output_text = data.get("response", "")
                            final_stage = data.get("final_stage", 3)
                            final_model = data.get("final_model", "Inconnu")
                            
                            metadata_text = f"🚀 **Cloud Bursting approuvé !** Exécuté sur le Stage {final_stage} ({final_model})"
                            
                            res_placeholder.markdown(output_text)
                            meta_placeholder.caption(metadata_text)
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": output_text,
                                "metadata": metadata_text
                            })
                            
                            # Réinitialisation des états pour la prochaine question
                            st.session_state.show_burst_button = False
                            st.rerun()
                        else:
                            st.error(f"❌ Échec du Bursting ({response.status_code})")
                    except Exception as e:
                        st.error(f"❌ Erreur critique : {str(e)}")
                        
    with col_txt:
        st.info("💡 Les modèles locaux Ollama ont expiré ou échoué. Donnez votre feu vert pour déléguer la requête à notre infrastructure Cloud haute performance.")
        