
import torch
import torch.nn.functional as F
from torch_geometric.transforms import RandomNodeSplit
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
import numpy as np
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.data.graph_loader import GraphLoader
from src.model.graphsage import GraphSAGE

def focal_loss(logits, labels, gamma=2.0, alpha=0.85):
    ce = F.cross_entropy(logits, labels, reduction="none")
    pt = torch.exp(-ce)
    return (alpha * (1 - pt) ** gamma * ce).mean()

def find_best_threshold(y_true, y_probs):
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
    f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-8)
    best_idx = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    return best_threshold, f1_scores[best_idx]

def train():
    print("=" * 60)
    print("  FRAUD DETECTION GNN — Enhanced with Ring Detection")
    print("=" * 60)

    print("\nLoading graph from Neo4j...")
    loader = GraphLoader()
    data = loader.load_graph()
    loader.close()

    transform = RandomNodeSplit(split="train_rest", num_val=0.1, num_test=0.2)
    data = transform(data)

    model = GraphSAGE(
        in_channels=data.num_node_features,
        hidden_channels=256,
        out_channels=128
    )

    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n🧠 Model parameters: {total_params:,}")
    print(f"📐 Input features: {data.num_node_features}")
    print(f"📊 Train/Val/Test: {data.train_mask.sum()}/{data.val_mask.sum()}/{data.test_mask.sum()}")
    print(f"🚨 Fraud in train: {data.y[data.train_mask].sum().item()}")

    optimizer = torch.optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=20, factor=0.5, min_lr=1e-5
    )

    print("\nTraining...\n")
    best_val_auc = 0.0
    patience, patience_counter = 50, 0

    for epoch in range(1, 501):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = focal_loss(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_out  = model(data.x, data.edge_index)
            val_probs = F.softmax(val_out[data.val_mask], dim=1)[:, 1]
            val_loss  = focal_loss(val_out[data.val_mask], data.y[data.val_mask])
            try:
                val_auc = roc_auc_score(
                    data.y[data.val_mask].numpy(), val_probs.numpy()
                )
            except:
                val_auc = 0.0

        scheduler.step(val_loss)

        if epoch % 25 == 0:
            thresh, f1 = find_best_threshold(
                data.y[data.val_mask].numpy(), val_probs.numpy()
            )
            lr = optimizer.param_groups[0]["lr"]
            print(f"Epoch {epoch:03d} | Loss: {loss:.4f} | Val AUC: {val_auc:.4f} | F1: {f1:.4f} | Thresh: {thresh:.2f} | LR: {lr:.5f}")

        if val_auc > best_val_auc:
            best_val_auc = val_auc
            torch.save(model.state_dict(), "best_model.pt")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n⏹ Early stopping at epoch {epoch}")
                print(f"🏆 Best Val AUC: {best_val_auc:.4f}")
                break

    # ── Evaluation ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  EVALUATION")
    print("=" * 60)

    model.load_state_dict(torch.load("best_model.pt"))
    model.eval()

    with torch.no_grad():
        out        = model(data.x, data.edge_index)
        test_probs = F.softmax(out[data.test_mask], dim=1)[:, 1].numpy()
        test_true  = data.y[data.test_mask].numpy()
        val_probs  = F.softmax(out[data.val_mask], dim=1)[:, 1].numpy()
        val_true   = data.y[data.val_mask].numpy()

    best_thresh, _ = find_best_threshold(val_true, val_probs)
    print(f"\n🎯 Threshold: {best_thresh:.4f}")

    for thresh in [0.2, 0.3, best_thresh]:
        preds = (test_probs >= thresh).astype(int)
        print(f"\n── Threshold {thresh:.2f} ──")
        print(classification_report(
            test_true, preds,
            target_names=["Legit", "Fraud"],
            zero_division=0
        ))

    auc = roc_auc_score(test_true, test_probs)
    print(f"🎯 Final ROC-AUC: {auc:.4f}")

    # ── Save ──────────────────────────────────────────────────
    os.makedirs("models", exist_ok=True)
    torch.save({
        "model_state_dict": model.state_dict(),
        "in_channels":      data.num_node_features,
        "hidden_channels":  256,
        "out_channels":     128,
        "threshold":        float(best_thresh),
        "auc":              float(auc)
    }, "models/graphsage_fraud.pt")
    print(f"\n✅ Model saved | AUC: {auc:.4f} | Threshold: {best_thresh:.4f}")

if __name__ == "__main__":
    train()
