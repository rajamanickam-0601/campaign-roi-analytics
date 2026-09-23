import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder

campaigns = pd.read_csv("campaigns.csv", parse_dates=["start_date", "end_date"])
customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
conversions = pd.read_csv("conversions.csv", parse_dates=["lead_date", "conversion_date"])

df = customers.merge(campaigns[["campaign_id", "channel", "campaign_cost", "impressions", "clicks"]], on="campaign_id")
df = df.merge(conversions[["customer_id", "revenue"]], on="customer_id", how="left")
df["converted"] = df["revenue"].notnull().astype(int)
df["revenue"] = df["revenue"].fillna(0)

# Feature engineering
df["ctr"] = df["clicks"] / df["impressions"]
df["signup_month"] = df["signup_date"].dt.month

le_channel = LabelEncoder()
le_segment = LabelEncoder()
df["channel_enc"] = le_channel.fit_transform(df["channel"])
df["segment_enc"] = le_segment.fit_transform(df["segment"])

feature_cols = ["channel_enc", "segment_enc", "ctr", "signup_month", "campaign_cost"]
X = df[feature_cols]
y = df["converted"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
print("ROC-AUC:", round(roc_auc_score(y_test, y_proba), 3))
print("\nClassification report:\n", classification_report(y_test, y_pred, target_names=["Not Converted", "Converted"]))

importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nFeature importances:\n", importances)

# Save a results summary for the report
with open("ml_results.txt", "w") as f:
    f.write(f"Accuracy: {round(accuracy_score(y_test, y_pred), 3)}\n")
    f.write(f"ROC-AUC: {round(roc_auc_score(y_test, y_proba), 3)}\n\n")
    f.write(classification_report(y_test, y_pred, target_names=["Not Converted", "Converted"]))
    f.write("\nFeature importances:\n")
    f.write(importances.to_string())
