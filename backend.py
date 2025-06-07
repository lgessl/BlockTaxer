from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
from io import StringIO
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_eur(value):
    # Remove euro sign and commas, convert to float
    return float(value.replace('€', '').replace(',', '').strip())

@app.post("/staking-rewards-sum")
async def staking_rewards_sum(
    file: UploadFile = File(...),
    year: int = Form(...)
):
    content = await file.read()
    s = StringIO(content.decode())
    reader = csv.DictReader(s)
    total = 0.0
    monthly = {i: 0.0 for i in range(1, 13)}
    for row in reader:
        if row.get('Transaction Type') != 'Staking Income':
            continue
        ts = datetime.strptime(row['Timestamp'], "%Y-%m-%d %H:%M:%S UTC")
        if ts.year != year:
            continue
        eur = parse_eur(row['Subtotal'])
        total += eur
        monthly[ts.month] += eur
    # Remove months with 0 for a cleaner frontend, or keep all 12 for chart
    return JSONResponse({
        "staking_rewards_eur": round(total, 2),
        "monthly_rewards_eur": {m: round(monthly[m], 2) for m in monthly}
    })
