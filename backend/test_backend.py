import os
import tempfile
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SAMPLE_CSV = '''ID,Timestamp,Transaction Type,Asset,Quantity Transacted,Price Currency,Price at Transaction,Subtotal,Total (inclusive of fees and/or spread),Fees and/or Spread,Notes
1,2025-01-15 12:00:00 UTC,Staking Income,ETH,0.01,EUR,€2000,€20,€20,€0.00,
2,2025-02-10 12:00:00 UTC,Staking Income,ETH,0.02,EUR,€2500,€50,€50,€0.00,
3,2025-02-20 12:00:00 UTC,Staking Income,ETH,0.01,EUR,€2600,€26,€26,€0.00,
4,2024-03-10 12:00:00 UTC,Staking Income,ETH,0.01,EUR,€1800,€18,€18,€0.00,
5,2025-01-15 12:00:00 UTC,Buy,ETH,0.01,EUR,€2000,€20,€20,€0.00,
'''

def make_file(data: str):
    f = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    f.write(data.encode())
    f.close()
    return f.name

def test_staking_rewards_sum_2025():
    file_path = make_file(SAMPLE_CSV)
    with open(file_path, 'rb') as f:
        response = client.post(
            "/staking-rewards-sum",
            files={"file": ("test.csv", f, "text/csv")},
            data={"year": "2025"}
        )
    os.unlink(file_path)
    assert response.status_code == 200
    data = response.json()
    assert data["staking_rewards_eur"] == 96.0  # 20 + 50 + 26
    assert data["monthly_rewards_eur"]["1"] == 20.0
    assert data["monthly_rewards_eur"]["2"] == 76.0
    assert data["monthly_rewards_eur"]["3"] == 0.0
    # Realized gains: Only one Buy (0.01 ETH at €20), but no Sell in sample, so gains should be 0
    assert data["realized_gains_eur"] == 0.0
    assert data["taxable_gains_eur"] == 0.0

def test_staking_rewards_sum_2024():
    file_path = make_file(SAMPLE_CSV)
    with open(file_path, 'rb') as f:
        response = client.post(
            "/staking-rewards-sum",
            files={"file": ("test.csv", f, "text/csv")},
            data={"year": "2024"}
        )
    os.unlink(file_path)
    assert response.status_code == 200
    data = response.json()
    assert data["staking_rewards_eur"] == 18.0
    assert data["monthly_rewards_eur"]["3"] == 18.0
    assert data["monthly_rewards_eur"]["1"] == 0.0
    # No sells in 2024, so realized and taxable gains should be 0
    assert data["realized_gains_eur"] == 0.0
    assert data["taxable_gains_eur"] == 0.0

def test_staking_rewards_sum_no_staking():
    csv = '''ID,Timestamp,Transaction Type,Asset,Quantity Transacted,Price Currency,Price at Transaction,Subtotal,Total (inclusive of fees and/or spread),Fees and/or Spread,Notes\n1,2025-01-15 12:00:00 UTC,Buy,ETH,0.01,EUR,€2000,€20,€20,€0.00,\n'''
    file_path = make_file(csv)
    with open(file_path, 'rb') as f:
        response = client.post(
            "/staking-rewards-sum",
            files={"file": ("test.csv", f, "text/csv")},
            data={"year": "2025"}
        )
    os.unlink(file_path)
    assert response.status_code == 200
    data = response.json()
    assert data["staking_rewards_eur"] == 0.0
    assert all(v == 0.0 for v in data["monthly_rewards_eur"].values())
    assert data["realized_gains_eur"] == 0.0
    assert data["taxable_gains_eur"] == 0.0

# Realized and taxable gains with a sell
SELL_SAMPLE_CSV = '''ID,Timestamp,Transaction Type,Asset,Quantity Transacted,Price Currency,Price at Transaction,Subtotal,Total (inclusive of fees and/or spread),Fees and/or Spread,Notes\n
1,2023-01-01 12:00:00 UTC,Buy,ETH,0.5,EUR,€1000,€500,€500,€0.00,\n
2,2024-01-09 12:00:00 UTC,Staking Income,ETH,0.5,EUR,€2000,€1000,€1000,€0.00,\n
3,2025-01-01 12:00:00 UTC,Sell,ETH,-0.3,EUR,€4000,€1200,€1200,€0.00,\n
4,2025-01-02 12:00:00 UTC,Sell,ETH,-0.5,EUR,€8000,€4000,€4000,€0.00,\n'''
def test_realized_and_taxable_gains():
    file_path = make_file(SELL_SAMPLE_CSV)
    with open(file_path, 'rb') as f:
        response = client.post(
            "/staking-rewards-sum",
            files={"file": ("test.csv", f, "text/csv")},
            data={"year": "2025"}
        )
    os.unlink(file_path)
    assert response.status_code == 200
    data = response.json()
    # First sell (0.3 ETH at €1200): Uses 0.3 from Buy 2023-01-01 (partial lot)
    # Cost: €500 * (0.3/0.5) = €300, Proceeds: €1200, Gain: €900 (held >1 year, tax-free)
    # Second sell (0.5 ETH at €4000): Uses remaining 0.2 from Buy + 0.3 from Staking
    # - 0.2 ETH from Buy: cost €200, proceeds €1600, gain €1400 (held >1 year, tax-free)
    # - 0.3 ETH from Staking: cost €600, proceeds €2400, gain €1800 (held <1 year, taxable)
    # Total realized: 900 + 1400 + 1800 = 4100
    # Taxable: 1800 - 1000 exemption = 800
    assert data["realized_gains_eur"] == 4100.0
    assert data["taxable_gains_eur"] == 800.0

# Previous year sell consumes FIFO lots
PREVIOUS_YEAR_SELL_CSV = '''ID,Timestamp,Transaction Type,Asset,Quantity Transacted,Price Currency,Price at Transaction,Subtotal,Total (inclusive of fees and/or spread),Fees and/or Spread,Notes\n
1,2023-01-01 12:00:00 UTC,Buy,ETH,0.5,EUR,€1000,€500,€500,€0.00,\n
2,2024-01-01 12:00:00 UTC,Buy,ETH,0.5,EUR,€2000,€1000,€1000,€0.00,\n
3,2024-06-01 12:00:00 UTC,Sell,ETH,-0.3,EUR,€3000,€900,€900,€0.00,\n
4,2025-03-01 12:00:00 UTC,Sell,ETH,-0.4,EUR,€4000,€1600,€1600,€0.00,\n'''
def test_previous_year_sell_consumes_fifo_lots():
    file_path = make_file(PREVIOUS_YEAR_SELL_CSV)
    with open(file_path, 'rb') as f:
        response = client.post(
            "/staking-rewards-sum",
            files={"file": ("test.csv", f, "text/csv")},
            data={"year": "2025"}
        )
    os.unlink(file_path)
    assert response.status_code == 200
    data = response.json()
    # 2024 sell consumed 0.3 ETH from the first FIFO lot (0.5 ETH from 2023-01-01), leaving 0.2 ETH
    # 2025 sell (0.4 ETH) should consume:
    # - Remaining 0.2 ETH from first lot (2023-01-01): cost €200, proceeds €800, gain €600 (held >1 year, tax-free)
    # - 0.2 ETH from second lot (2024-01-01): cost €400, proceeds €800, gain €400 (held <1 year, taxable)
    # Total realized: 600 + 400 = 1000
    # Taxable: 400 - 1000 exemption = 0
    assert data["realized_gains_eur"] == 1000.0
    assert data["taxable_gains_eur"] == 0.0
