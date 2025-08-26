from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Swap(BaseModel):
    spotRate: float
    forwardRate: float

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    points = swap.forwardRate - swap.spotRate
    return {"points": round(points, 4)}

# Démarrage pour Railway
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
