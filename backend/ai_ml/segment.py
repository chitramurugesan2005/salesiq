import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from models import db
from sqlalchemy import text


def get_customer_data():
    # Use customers table instead of sales
    query = text("""
        SELECT 
            id,
            name,
            total_spend,
            total_orders,
            avg_spend,
            ltv
        FROM customers
        WHERE total_spend > 0
    """)
    return db.session.execute(query).fetchall()


def run_segmentation():
    rows = get_customer_data()

    if len(rows) < 3:
        return None, "Not enough customer data to segment."

    # Use customer id and name
    customer_ids   = [row.id   for row in rows]
    customer_names = [row.name for row in rows]

    # Features for clustering
    features = np.array([
        [
            float(row.total_spend),
            float(row.total_orders),
            float(row.avg_spend),
            float(row.ltv)
        ]
        for row in rows
    ])

    # Scale features
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    # Run K-Means with k=3
    k      = min(3, len(rows))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)

    # Sort clusters by average spend
    # so cluster 0=Low, 1=Mid, 2=High
    cluster_means = {}
    for i in range(k):
        mask = labels == i
        cluster_means[i] = features[mask, 0].mean() \
            if mask.sum() > 0 else 0

    sorted_clusters = sorted(
        cluster_means, key=cluster_means.get
    )
    remap = {
        old: new 
        for new, old in enumerate(sorted_clusters)
    }

    cluster_names = {
        0: "One-Time",
        1: "Regular",
        2: "Champions"
    }

    # Build result list
    result = [
        {
            "customer_id"    : customer_ids[i],
            "name"           : customer_names[i],
            "total_spend"    : round(features[i][0], 2),
            "total_orders"   : int(features[i][1]),
            "avg_spend"      : round(features[i][2], 2),
            "ltv"            : round(features[i][3], 2),
            "cluster"        : remap[int(labels[i])],
            "segment"        : cluster_names[remap[int(labels[i])]]
        }
        for i in range(len(rows))
    ]

    # Build summary
    summary = {
        cluster_names[v]: sum(
            1 for r in result if r["cluster"] == v
        )
        for v in range(k)
    }

    # Cluster centers info
    centers = []
    for i in range(k):
        mask = np.array(labels) == i
        if mask.sum() > 0:
            centers.append({
                "cluster"      : remap[i],
                "segment"      : cluster_names[remap[i]],
                "avg_spend"    : round(
                    float(features[mask, 0].mean()), 2
                ),
                "avg_orders"   : round(
                    float(features[mask, 1].mean()), 1
                ),
                "customer_count": int(mask.sum())
            })

    return {
        "customers" : result,
        "summary"   : summary,
        "centers"   : centers,
        "k"         : k
    }, None