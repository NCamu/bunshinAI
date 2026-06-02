import psutil
import requests
import logging

# Configuration unique du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bunshin.core.resource_monitor")

# URL de l'API locale d'Ollama
OLLAMA_PS_URL = "http://ollama:11434/api/ps"

def is_model_warmed_up(target_model: str) -> bool:
    """
    Interroge l'API Ollama pour savoir si le modèle cible est déjà chargé en mémoire (RAM/VRAM).
    """
    try:
        # Timeout court (2s) pour ne pas bloquer le graphe si Ollama est éteint
        response = requests.get(OLLAMA_PS_URL, timeout=2)
        if response.status_code == 200:
            running_models = response.json().get("models", [])
            
            # On vérifie si notre modèle est dans la liste des modèles actifs
            for model in running_models:
                if model.get("name") == target_model or model.get("model") == target_model:
                    return True
    except Exception as e:
        logger.warning(f"⚠️ Impossible de joindre l'API d'Ollama pour le check de présence : {e}")
    return False

def check_ram_availability(threshold_gb: float = 1.5, target_model: str = "llama3:8b-instruct-q4_K_M") -> bool:
    """
    Analyse les ressources pour déterminer si l'exécution locale est possible.
    Retourne :
      - True  : Si on reste en LOCAL (soit modèle déjà chaud, soit assez de RAM à froid).
      - False : Si on bascule sur le CLOUD (modèle froid ET RAM insuffisante).
    """
    try:
        # Étape 1 : Le modèle est-il déjà chaud en mémoire ?
        if is_model_warmed_up(target_model):
            logger.info(f"🧠 Modèle '{target_model}' détecté comme déjà chargé en mémoire locale. Inférence locale immédiate autorisée.")
            return True  # True = OK pour le local, on bypass le check de RAM globale !

        # Étape 2 : Si le modèle n'est PAS chargé, on inspecte la RAM globale disponible
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)
        
        logger.info(f"Surveillance RAM : {available_gb:.2f} Go disponibles (Seuil critique : {threshold_gb} Go)")
        
        if available_gb < threshold_gb:
            logger.warning(f"⚠️ RAM insuffisante ({available_gb:.2f} Go) pour charger le modèle à froid. Alerte de basculement Cloud activée !")
            return False  # False = Pas assez de ressources -> Basculement Cloud
            
        return True  # Assez de RAM pour charger le modèle à froid -> Exécution locale
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des ressources : {str(e)}")
        # Par sécurité, on renvoie True pour tenter le local en cas de bug de lecture hardware
        return True

if __name__ == "__main__":
    # Ce bloc s'exécute UNIQUEMENT si tu lances ce fichier directement pour le tester
    print("--- Test à blanc du Resource Monitor ---")
    is_local_ok = check_ram_availability(threshold_gb=1.5)
    print(f"Résultat du test -> Autoriser l'exécution locale : {is_local_ok}")
    