from fastapi import FastAPI

app = FastAPI(title="Bunshin AI - API", version="2.5")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "API Bunshin active (Placeholder de l'étape 3)"
    }
