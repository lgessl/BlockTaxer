from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
from io import StringIO
from datetime import datetime
from collections import deque, defaultdict

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

def parse_csv_transactions(content):
    s = StringIO(content.decode())
    reader = csv.DictReader(s)
    txs = []
    for row in reader:
        ts = datetime.strptime(row['Timestamp'], "%Y-%m-%d %H:%M:%S UTC")
        txs.append({
            'type': row['Transaction Type'],
            'asset': row['Asset'],
            'amount': abs(float(row['Quantity Transacted'])), # Coinbase uses negative for sells
            'eur': parse_eur(row['Subtotal']),
            'timestamp': ts,
            'row': row
        })
    return txs

def calculate_gains_fifo(txs, year):
    # FIFO inventory per asset: list of lots (amount, buy_time, buy_eur, is_staking)
    inventory = defaultdict(deque)
    realized_gains = 0.0
    taxable_gains = 0.0
    for tx in sorted(txs, key=lambda x: x['timestamp']):
        if tx['type'] in ('Buy', 'Staking Income'):
            # For staking, use the EUR value as cost basis (already taxed as income)
            inventory[tx['asset']].append({
                'amount': tx['amount'],
                'buy_time': tx['timestamp'],
                'buy_eur': tx['eur'],
                'is_staking': tx['type'] == 'Staking Income',
            })
        elif tx['type'] == 'Sell':
            # Process ALL sells to maintain correct FIFO inventory state
            sell_amount = tx['amount']
            sell_time = tx['timestamp']
            sell_eur = tx['eur']
            is_target_year = tx['timestamp'].year == year
            # FIFO: consume from inventory
            while sell_amount > 0 and inventory[tx['asset']]:
                lot = inventory[tx['asset']][0]
                used = min(sell_amount, lot['amount'])
                holding_period = (sell_time - lot['buy_time']).days
                cost_basis = lot['buy_eur'] * (used / lot['amount']) if lot['buy_eur'] else 0.0
                proceeds = sell_eur * (used / tx['amount'])
                gain = proceeds - cost_basis
                # Only count gains for target year
                if is_target_year:
                    realized_gains += gain
                    # Taxable if gain > 0, holding period < 365 days, and total gains > 1000
                    if holding_period < 365:
                        taxable_gains += gain
                # Remove used from lot
                lot['amount'] -= used
                lot['buy_eur'] -= cost_basis
                if lot['amount'] == 0:
                    inventory[tx['asset']].popleft()
                sell_amount -= used
    # Apply 1000 EUR exemption
    taxable_gains = max(0.0, taxable_gains - 1000.0)
    return realized_gains, taxable_gains

@app.post("/staking-rewards-sum")
async def staking_rewards_sum(
    file: UploadFile = File(...),
    year: int = Form(...)
):
    content = await file.read()
    txs = parse_csv_transactions(content)
    # Calculate monthly staking rewards
    monthly = {i: 0.0 for i in range(1, 13)}
    for tx in txs:
        if tx['type'] == 'Staking Income' and tx['timestamp'].year == year:
            monthly[tx['timestamp'].month] += tx['eur']
    # Calculate realized and taxable gains
    realized_gains, taxable_gains = calculate_gains_fifo(txs, year)
    return JSONResponse({
        "monthly_rewards_eur": {m: round(monthly[m], 2) for m in monthly},
        "realized_gains_eur": round(realized_gains, 2),
        "taxable_gains_eur": round(taxable_gains, 2)
    })
