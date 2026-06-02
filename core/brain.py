import os
import requests
import logging
from typing import Optional

logger = logging.getLogger("bunshin.core.brain")

class OllamaBrain:
    """
    Client d'inférence sécurisé pour le serveur Ollama local.
    """
    def __init__(self):
        # Récupération des variables d'environnement configurées dans docker-compose
        self.base_url = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.model = os.getenv("INFERENCE_MODEL", "qwen2.5-coder:1.5b")
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None, timeout: Optional[int] = 300) -> str:
        """
        Envoie une requête d'inférence non-streamée à Ollama avec gestion et respect des timeouts.
        """
        # 💡 CORRECTION CRITIQUE : On n'écrase plus le timeout ! Si l'orchestrateur passe 10s, 
        # on utilise 10s. S'il ne passe rien, on applique la valeur par défaut de sécurité (300s).
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,  # Dynamique, modifié par l'orchestrateur au fil des paliers
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            logger.info(f"Envoi de la requête au modèle '{self.model}' via {url} (Timeout max autorisé : {timeout}s)...")
            
            # C'est ce paramètre réseau qui coupe l'appel si le CPU est trop lent
            response = requests.post(url, json=payload, timeout=timeout)
            
            if response.status_code == 404:
                logger.error(f"Erreur 404 : Le modèle '{self.model}' n'existe pas ou n'est pas encore téléchargé sur Ollama.")
                raise ValueError(f"Modèle '{self.model}' introuvable dans le volume de bunshin_ollama.")
                
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Erreur de connexion : Impossible de joindre Ollama à l'adresse {self.base_url}.")
            raise ConnectionError(f"Le service Ollama est injoignable sur {self.base_url}. Vérifiez vos conteneurs Docker.")
            
        except requests.exceptions.Timeout:
            # 🔄 LEVIER DU BURST : Capturé par le try/except de l'orchestrateur pour passer au modèle suivant
            logger.warning(f"⏰ SEUIL ATTEINT : Le modèle '{self.model}' a dépassé la limite de {timeout}s !")
            raise TimeoutError(f"Le modèle Ollama '{self.model}' a mis trop de temps à générer une réponse.")
            
        except Exception as e:
            logger.error(f"Erreur inattendue sur le module core.brain : {str(e)}")
            raise e

if __name__ == "__main__":
    brain = OllamaBrain()
    print(f"Module OllamaBrain initialisé sur {brain.base_url} avec le modèle {brain.model}.")
    