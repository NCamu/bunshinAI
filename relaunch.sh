#!/bin/bash

# 1. Arrête proprement tous les conteneurs et supprime le réseau
docker compose down

# 2. Reconstruis TOUTE l'infrastructure (API, UI, etc.) en ignorant le cache
docker compose build --no-cache

# 3. Relance tous les conteneurs en tâche de fond
docker compose up -d

##############################################
# si tu utile ces commande ça fera un RAZ complet de l'infrastructure, il faudra aussi re dl les modèles d'IA(dlmodelAI.sh)
## (à utiliser si tu as fait des changements majeurs ou si tu rencontres des problèmes persistants)

#docker-compose down -v
#docker-compose build --no-cache
#docker-compose up