from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import torch
import torch.nn.functional as F
import sys, os, math
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.model.graphsage import GraphSAGE

app = FastAPI(title="Fraud Detection GNN API", version="2.0")

# ── Load model ────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/graphsage_fraud.pt")
checkpoint = torch.load(MODEL_PATH, map_location="cpu")
model = GraphSAGE(
    in_channels=checkpoint["in_channels"],
    hidden_channels=checkpoint["hidden_channels"],
    out_channels=checkpoint["out_channels"]
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
THRESHOLD = checkpoint.get("threshold", 0.38)

# Max amount seen during training — used for log-normalization
# Matches the value used in graph_loader.py during feature engineering
AMOUNT_MAX = checkpoint.get("amount_max", 50000.0)

print(f"✅ Model loaded | AUC: {checkpoint.get('auc', 'N/A')} | Threshold: {THRESHOLD:.4f}")

# ── Neo4j ─────────────────────────────────────────────────────
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

# ── Schemas ───────────────────────────────────────────────────
class TransactionRequest(BaseModel):
    transaction_id: str
    amount: float
    user_enc: int = 0
    merchant_enc: int = 0
    device_enc: int = 0
    device_ring_score: float = 0.0
    ip_ring_score: float = 0.0
    combined_ring_score: float = 0.0
    user_tx_count: float = 1.0
    user_avg_amount: float = 0.0
    merch_tx_count: float = 1.0
    merch_fraud_rate: float = 0.0
    is_new_device: float = 0.0
    is_high_risk: float = 0.0
    is_foreign: float = 0.0

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    prediction: int
    label: str
    threshold_used: float
    ring_risk: str

# ── Helper ────────────────────────────────────────────────────
def scale_amount(amount: float) -> float:
    """
    Normalize amount using log1p scaling — must match graph_loader.py exactly.
    If your loader used StandardScaler, replace this with:
        (amount - mean) / std
    using the same mean/std from training.
    """
    return math.log1p(amount) / math.log1p(AMOUNT_MAX)

# ── Endpoints ─────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "GraphSAGE v2",
        "auc": checkpoint.get("auc", "N/A"),
        "threshold": THRESHOLD
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(req: TransactionRequest):
    try:
        amount_scaled = scale_amount(req.amount)

        # Feature vector — 15 features matching training exactly:
        # [amount, user_enc, merchant_enc, device_enc, device_ring_score,
        #  ip_ring_score, combined_ring_score, user_tx_count, user_avg_amount,
        #  merch_tx_count, merch_fraud_rate, is_new_device, is_high_risk,
        #  is_foreign, amount_scaled]
        x = torch.tensor([[
            req.amount,               # raw amount
            req.user_enc,             # encoded user id
            req.merchant_enc,         # encoded merchant id
            req.device_enc,           # encoded device id
            req.device_ring_score,    # fraction of device users who are fraudsters
            req.ip_ring_score,        # fraction of IP users who are fraudsters
            req.combined_ring_score,  # max(device_ring, ip_ring)
            req.user_tx_count,        # user's total historical tx count
            req.user_avg_amount,      # user's historical avg amount
            req.merch_tx_count,       # merchant's total tx count
            req.merch_fraud_rate,     # merchant's historical fraud rate
            req.is_new_device,        # 1.0 if first time using this device
            req.is_high_risk,         # 1.0 if high-risk country
            req.is_foreign,           # 1.0 if foreign transaction
            amount_scaled,            # ✅ FIX: properly log-normalized amount
        ]], dtype=torch.float)

        # Self-loop edge — single node inference (no neighbors)
        # The model still applies the learned transformation, just without
        # neighbor aggregation. Ring scores in the feature vector compensate.
        edge_index = torch.tensor([[0], [0]], dtype=torch.long)

        with torch.no_grad():
            out = model(x, edge_index)
            probs = F.softmax(out, dim=1)
            fraud_prob = probs[0][1].item()
            prediction = int(fraud_prob >= THRESHOLD)

        # Ring risk label from combined score
        ring_score = req.combined_ring_score
        if ring_score > 0.7:
            ring_risk = "HIGH"
        elif ring_score > 0.4:
            ring_risk = "MEDIUM"
        else:
            ring_risk = "LOW"

        return PredictionResponse(
            transaction_id=req.transaction_id,
            fraud_probability=round(fraud_prob, 4),
            prediction=prediction,
            label="FRAUD" if prediction == 1 else "LEGITIMATE",
            threshold_used=THRESHOLD,
            ring_risk=ring_risk
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rings/devices")
def get_device_rings(min_users: int = 10, limit: int = 20):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User)-[:MADE]->(t:Transaction)-[:USED_DEVICE]->(d:Device)
            WITH d,
                 collect(DISTINCT u.userId) AS users,
                 collect(DISTINCT t.transactionId) AS txns,
                 sum(CASE WHEN t.isFraud = true THEN 1 ELSE 0 END) AS fraud_count
            WHERE size(users) >= $min_users
            RETURN d.deviceId AS device_id,
                   size(users) AS user_count,
                   size(txns) AS tx_count,
                   fraud_count,
                   round(100.0 * fraud_count / size(txns), 1) AS fraud_rate
            ORDER BY user_count DESC
            LIMIT $limit
        """, min_users=min_users, limit=limit)
        rings = [dict(r) for r in result]
    return {"device_rings": rings, "count": len(rings)}

@app.get("/rings/ips")
def get_ip_rings(min_users: int = 10, limit: int = 20):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User)-[:MADE]->(t:Transaction)-[:FROM_IP]->(ip:IP)
            WITH ip,
                 collect(DISTINCT u.userId) AS users,
                 collect(DISTINCT t.transactionId) AS txns,
                 sum(CASE WHEN t.isFraud = true THEN 1 ELSE 0 END) AS fraud_count
            WHERE size(users) >= $min_users
            RETURN ip.address AS ip_address,
                   size(users) AS user_count,
                   size(txns) AS tx_count,
                   fraud_count,
                   round(100.0 * fraud_count / size(txns), 1) AS fraud_rate
            ORDER BY user_count DESC
            LIMIT $limit
        """, min_users=min_users, limit=limit)
        rings = [dict(r) for r in result]
    return {"ip_rings": rings, "count": len(rings)}

@app.get("/rings/transactions/{device_or_ip}")
def get_ring_transactions(device_or_ip: str, limit: int = 50):
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Transaction)-[:USED_DEVICE]->(d:Device {deviceId: $id})
            OPTIONAL MATCH (u:User)-[:MADE]->(t)
            RETURN t.transactionId AS tx_id,
                   t.amount AS amount,
                   t.isFraud AS is_fraud,
                   u.userId AS user_id,
                   'device' AS ring_type
            LIMIT $limit
        """, id=device_or_ip, limit=limit)
        txns = [dict(r) for r in result]

        if not txns:
            result = session.run("""
                MATCH (t:Transaction)-[:FROM_IP]->(ip:IP {address: $id})
                OPTIONAL MATCH (u:User)-[:MADE]->(t)
                RETURN t.transactionId AS tx_id,
                       t.amount AS amount,
                       t.isFraud AS is_fraud,
                       u.userId AS user_id,
                       'ip' AS ring_type
                LIMIT $limit
            """, id=device_or_ip, limit=limit)
            txns = [dict(r) for r in result]

    return {
        "identifier": device_or_ip,
        "transactions": txns,
        "total": len(txns),
        "fraud_count": sum(1 for t in txns if t.get("is_fraud"))
    }

@app.get("/stats")
def get_stats():
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Transaction)
            RETURN count(t) AS total,
                   sum(CASE WHEN t.isFraud = true THEN 1 ELSE 0 END) AS fraud_count,
                   avg(t.amount) AS avg_amount,
                   max(t.amount) AS max_amount
        """)
        stats = dict(result.single())

        device_rings = session.run("""
            MATCH (u:User)-[:MADE]->(t:Transaction)-[:USED_DEVICE]->(d:Device)
            WITH d, collect(DISTINCT u) AS users
            WHERE size(users) >= 10
            RETURN count(d) AS high_risk_devices
        """).single()["high_risk_devices"]

        ip_rings = session.run("""
            MATCH (u:User)-[:MADE]->(t:Transaction)-[:FROM_IP]->(ip:IP)
            WITH ip, collect(DISTINCT u) AS users
            WHERE size(users) >= 10
            RETURN count(ip) AS high_risk_ips
        """).single()["high_risk_ips"]

    return {
        "total_transactions": stats["total"],
        "fraud_count": stats["fraud_count"],
        "fraud_rate": round(stats["fraud_count"] / stats["total"] * 100, 2),
        "avg_amount": round(stats["avg_amount"], 2),
        "max_amount": round(stats["max_amount"], 2),
        "high_risk_devices": device_rings,
        "high_risk_ips": ip_rings,
        "model_auc": checkpoint.get("auc", "N/A")
    }