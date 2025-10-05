from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data from file
with open(os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")) as f:
    telemetry_data = json.load(f)

@app.post("/")
async def telemetry_metrics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold_ms = data.get("threshold_ms", 0)

    response = {}
    for region in regions:
        latencies = telemetry_data.get(region, [])
        if latencies:
            response[region] = {
                "avg_latency": float(np.mean(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": float(np.mean([r.get("uptime", 100) for r in latencies])),
                "breaches": int(sum(l > threshold_ms for l in latencies))
            }
        else:
            response[region] = {}
    return response
