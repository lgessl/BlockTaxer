import os
import tempfile
import pytest
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
