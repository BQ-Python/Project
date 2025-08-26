from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.stackblitz.io", "http://localhost:3000"],  # Add your StackBlitz domain or localhost for testing
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
