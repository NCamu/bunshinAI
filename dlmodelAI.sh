# 1. Télécharge le modèle Stage 1 (1.5 Milliards 1go)
docker exec -it bunshin_ollama ollama pull qwen2.5-coder:1.5b

# 2. Télécharge le modèle Stage 2 (Phi-3 Mini de Microsoft 7go)
docker exec -it bunshin_ollama ollama pull phi3:mini

# 3. Télécharge le modèle Stage 3 (Uniquement si tu as de la place pour le Cloud / local 19go)
docker exec -it bunshin_ollama ollama pull qwen2.5-coder:32b


