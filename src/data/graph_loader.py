
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import torch
from torch_geometric.data import Data
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

load_dotenv()

class GraphLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def close(self):
        self.driver.close()

    def get_ring_scores(self):
        with self.driver.session() as session:
            # How many users share each device
            device_result = session.run("""
                MATCH (u:User)-[:MADE]->(t:Transaction)-[:USED_DEVICE]->(d:Device)
                WITH d, count(DISTINCT u) AS user_count, count(t) AS tx_count
                RETURN d.deviceId AS device_id, user_count, tx_count
            """)
            device_scores = {}
            device_user_counts = {}
            for r in device_result:
                score = min(r["user_count"] / 10.0, 1.0)
                device_scores[r["device_id"]] = score
                device_user_counts[r["device_id"]] = r["user_count"]

            # How many users share each IP
            ip_result = session.run("""
                MATCH (u:User)-[:MADE]->(t:Transaction)-[:FROM_IP]->(ip:IP)
                WITH ip, count(DISTINCT u) AS user_count, count(t) AS tx_count
                RETURN ip.address AS ip_address, user_count, tx_count
            """)
            ip_scores = {}
            ip_user_counts = {}
            for r in ip_result:
                score = min(r["user_count"] / 10.0, 1.0)
                ip_scores[r["ip_address"]] = score
                ip_user_counts[r["ip_address"]] = r["user_count"]

        print(f"📍 Device ring scores: {len(device_scores)} devices")
        print(f"📍 IP ring scores: {len(ip_scores)} IPs")
        print(f"🚨 High-risk devices (>10 users): {sum(1 for v in device_user_counts.values() if v > 10)}")
        print(f"🚨 High-risk IPs (>10 users): {sum(1 for v in ip_user_counts.values() if v > 10)}")
        return device_scores, ip_scores

    def load_graph(self):
        with self.driver.session() as session:
            # Only use properties that actually exist in Neo4j
            tx_result = session.run("""
                MATCH (t:Transaction)
                OPTIONAL MATCH (u:User)-[:MADE]->(t)
                OPTIONAL MATCH (t)-[:AT]->(m:Merchant)
                OPTIONAL MATCH (t)-[:USED_DEVICE]->(d:Device)
                OPTIONAL MATCH (t)-[:FROM_IP]->(ip:IP)
                RETURN 
                    t.transactionId AS tx_id,
                    t.amount AS amount,
                    t.isFraud AS is_fraud,
                    t.country AS country,
                    t.cardType AS card_type,
                    u.userId AS user_id,
                    m.merchantId AS merchant_id,
                    d.deviceId AS device_id,
                    ip.address AS ip_address
            """)
            rows = [dict(r) for r in tx_result]

            # User→Transaction edges
            user_edges = session.run("""
                MATCH (u:User)-[:MADE]->(t:Transaction)
                RETURN u.userId AS user_id, t.transactionId AS tx_id
            """)
            user_edge_list = [dict(r) for r in user_edges]

            # Device edges — only HIGH RISK devices (shared by >5 users)
            device_edges = session.run("""
                MATCH (t:Transaction)-[:USED_DEVICE]->(d:Device)
                WITH d, count{(u:User)-[:MADE]->(:Transaction)-[:USED_DEVICE]->(d)} AS user_count
                WHERE user_count > 5
                MATCH (t2:Transaction)-[:USED_DEVICE]->(d)
                RETURN t2.transactionId AS tx_id, d.deviceId AS device_id
            """)
            device_edge_list = [dict(r) for r in device_edges]

            # IP edges — only HIGH RISK IPs (shared by >5 users)
            ip_edges = session.run("""
                MATCH (t:Transaction)-[:FROM_IP]->(ip:IP)
                WITH ip, count{(u:User)-[:MADE]->(:Transaction)-[:FROM_IP]->(ip)} AS user_count
                WHERE user_count > 5
                MATCH (t2:Transaction)-[:FROM_IP]->(ip)
                RETURN t2.transactionId AS tx_id, ip.address AS ip_address
            """)
            ip_edge_list = [dict(r) for r in ip_edges]

        df = pd.DataFrame(rows).fillna("unknown")
        print(f"📊 Loaded {len(df)} transactions")
        print(f"🔍 Fraud rate: {df['is_fraud'].astype(float).mean():.3f}")

        # ── Ring scores ───────────────────────────────────────
        device_scores, ip_scores = self.get_ring_scores()

        df["device_ring_score"]   = df["device_id"].map(device_scores).fillna(0.0)
        df["ip_ring_score"]       = df["ip_address"].map(ip_scores).fillna(0.0)
        df["combined_ring_score"] = df["device_ring_score"] * 0.5 + df["ip_ring_score"] * 0.5
        df["is_high_risk_device"] = (df["device_ring_score"] > 0.5).astype(float)
        df["is_high_risk_ip"]     = (df["ip_ring_score"] > 0.5).astype(float)

        # ── Encode categoricals ───────────────────────────────
        user_enc    = LabelEncoder()
        merch_enc   = LabelEncoder()
        device_enc  = LabelEncoder()
        ip_enc      = LabelEncoder()
        country_enc = LabelEncoder()
        card_enc    = LabelEncoder()

        df["user_enc"]    = user_enc.fit_transform(df["user_id"].astype(str))
        df["merch_enc"]   = merch_enc.fit_transform(df["merchant_id"].astype(str))
        df["device_enc"]  = device_enc.fit_transform(df["device_id"].astype(str))
        df["ip_enc"]      = ip_enc.fit_transform(df["ip_address"].astype(str))
        df["country_enc"] = country_enc.fit_transform(df["country"].astype(str))
        df["card_enc"]    = card_enc.fit_transform(df["card_type"].astype(str))

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["is_fraud_num"] = pd.to_numeric(df["is_fraud"], errors="coerce").fillna(0)

        # ── Normalize amount ──────────────────────────────────
        scaler = StandardScaler()
        df["amount_scaled"] = scaler.fit_transform(df[["amount"]])

        # ── User-level aggregated stats ───────────────────────
        user_stats = df.groupby("user_enc").agg(
            user_tx_count=("tx_id", "count"),
            user_avg_amount=("amount", "mean"),
            user_fraud_rate=("is_fraud_num", "mean"),
            user_max_amount=("amount", "max")
        ).reset_index()
        df = df.merge(user_stats, on="user_enc", how="left")

        # ── Final feature matrix (15 features) ───────────────
        feature_cols = [
            "amount_scaled",        # normalized amount
            "user_enc",             # user identity
            "merch_enc",            # merchant identity
            "device_enc",           # device identity
            "ip_enc",               # IP identity
            "country_enc",          # country
            "card_enc",             # card type
            "device_ring_score",    # 🔑 device fraud ring score
            "ip_ring_score",        # 🔑 IP fraud ring score
            "combined_ring_score",  # 🔑 combined ring score
            "is_high_risk_device",  # 🔑 binary high risk device
            "is_high_risk_ip",      # 🔑 binary high risk IP
            "user_tx_count",        # user transaction count
            "user_avg_amount",      # user average amount
            "user_fraud_rate",      # user historical fraud rate
        ]

        x = torch.tensor(df[feature_cols].values, dtype=torch.float)
        y = torch.tensor(df["is_fraud_num"].values, dtype=torch.long)

        # ── Build edges ───────────────────────────────────────
        tx_to_idx = {tx: i for i, tx in enumerate(df["tx_id"].astype(str))}
        src_list, dst_list = [], []

        # 1) User transaction chains
        user_to_txs = {}
        for e in user_edge_list:
            uid = str(e["user_id"])
            tid = str(e["tx_id"])
            if tid in tx_to_idx:
                user_to_txs.setdefault(uid, []).append(tx_to_idx[tid])

        for uid, tx_indices in user_to_txs.items():
            for i in range(len(tx_indices) - 1):
                src_list += [tx_indices[i], tx_indices[i+1]]
                dst_list += [tx_indices[i+1], tx_indices[i]]

        print(f"🔗 User→Tx chain edges: {len(src_list)}")

        # 2) High-risk device ring edges
        device_to_txs = {}
        for e in device_edge_list:
            did = str(e["device_id"])
            tid = str(e["tx_id"])
            if tid in tx_to_idx:
                device_to_txs.setdefault(did, []).append(tx_to_idx[tid])

        before = len(src_list)
        for did, tx_indices in device_to_txs.items():
            # Cap at 20 connections per device to avoid over-connection
            tx_indices = tx_indices[:20]
            for i in range(len(tx_indices) - 1):
                src_list += [tx_indices[i], tx_indices[i+1]]
                dst_list += [tx_indices[i+1], tx_indices[i]]

        print(f"🔗 Device ring edges: {len(src_list) - before}")

        # 3) High-risk IP ring edges
        ip_to_txs = {}
        for e in ip_edge_list:
            ip  = str(e["ip_address"])
            tid = str(e["tx_id"])
            if tid in tx_to_idx:
                ip_to_txs.setdefault(ip, []).append(tx_to_idx[tid])

        before = len(src_list)
        for ip, tx_indices in ip_to_txs.items():
            # Cap at 20 connections per IP
            tx_indices = tx_indices[:20]
            for i in range(len(tx_indices) - 1):
                src_list += [tx_indices[i], tx_indices[i+1]]
                dst_list += [tx_indices[i+1], tx_indices[i]]

        print(f"🔗 IP ring edges: {len(src_list) - before}")

        # 4) Self loops
        n = len(df)
        src_list += list(range(n))
        dst_list += list(range(n))

        edge_index = torch.tensor([src_list, dst_list], dtype=torch.long)
        print(f"🔗 Total edges: {len(src_list)}")

        data = Data(x=x, edge_index=edge_index, y=y)
        print(f"✅ Graph: {data.num_nodes} nodes | {data.num_edges} edges | {int(y.sum())} fraud")
        return data
