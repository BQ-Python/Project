from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Swap(BaseModel):
    spotRate: float
    forwardRate: float

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    points = swap.forwardRate - swap.spotRate
    return {"points": round(points, 4)}
