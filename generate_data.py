import pandas as pd
import numpy as np

np.random.seed(42)

channels = ["Email", "Social Media", "Google Ads", "Referral", "Organic"]
segments = ["New", "Returning", "High-value"]

# ---- Campaigns table ----
n_campaigns = 20
campaign_ids = [f"C{100+i}" for i in range(n_campaigns)]
campaigns = pd.DataFrame({
    "campaign_id": campaign_ids,
    "channel": np.random.choice(channels, n_campaigns, p=[0.25, 0.25, 0.2, 0.15, 0.15]),
})
# channel-specific cost/impression/click ranges to create realistic ROI spread
channel_cost_mult = {"Email": 300, "Social Media": 800, "Google Ads": 1500, "Referral": 200, "Organic": 100}
channel_ctr = {"Email": 0.08, "Social Media": 0.04, "Google Ads": 0.06, "Referral": 0.15, "Organic": 0.1}

campaigns["campaign_cost"] = campaigns["channel"].map(lambda c: round(np.random.uniform(0.7, 1.3) * channel_cost_mult[c] * np.random.randint(3, 10), 2))
campaigns["impressions"] = campaigns["channel"].map(lambda c: int(np.random.uniform(5000, 50000)))
campaigns["clicks"] = campaigns.apply(lambda r: int(r["impressions"] * channel_ctr[r["channel"]] * np.random.uniform(0.8, 1.2)), axis=1)
campaigns["start_date"] = pd.to_datetime("2026-01-01") + pd.to_timedelta(np.random.randint(0, 200, n_campaigns), unit="D")
campaigns["end_date"] = campaigns["start_date"] + pd.to_timedelta(np.random.randint(14, 45, n_campaigns), unit="D")

# ---- Customers table ----
n_customers = 3000
customers = pd.DataFrame({
    "customer_id": [f"CUST{1000+i}" for i in range(n_customers)],
    "campaign_id": np.random.choice(campaign_ids, n_customers),
    "segment": np.random.choice(segments, n_customers, p=[0.5, 0.35, 0.15]),
})
customers = customers.merge(campaigns[["campaign_id", "start_date"]], on="campaign_id")
customers["signup_date"] = customers["start_date"] + pd.to_timedelta(np.random.randint(0, 10, n_customers), unit="D")
customers = customers.drop(columns=["start_date"])

# ---- Conversions table (not every customer converts) ----
channel_conv_rate = {"Email": 0.22, "Social Media": 0.12, "Google Ads": 0.18, "Referral": 0.30, "Organic": 0.20}
segment_boost = {"New": 0.9, "Returning": 1.1, "High-value": 1.4}

merged = customers.merge(campaigns[["campaign_id", "channel"]], on="campaign_id")
merged["conv_prob"] = merged.apply(
    lambda r: min(channel_conv_rate[r["channel"]] * segment_boost[r["segment"]], 0.95), axis=1
)
merged["converted"] = np.random.binomial(1, merged["conv_prob"])

conv_rows = merged[merged["converted"] == 1].copy()
conv_rows["lead_date"] = conv_rows["signup_date"] + pd.to_timedelta(np.random.randint(0, 5, len(conv_rows)), unit="D")
conv_rows["conversion_date"] = conv_rows["lead_date"] + pd.to_timedelta(np.random.randint(1, 20, len(conv_rows)), unit="D")

revenue_base = {"New": 80, "Returning": 150, "High-value": 400}
conv_rows["revenue"] = conv_rows["segment"].map(lambda s: round(np.random.uniform(0.7, 1.5) * revenue_base[s], 2))

conversions = conv_rows[["customer_id", "campaign_id", "lead_date", "conversion_date", "revenue"]].reset_index(drop=True)
conversions.insert(0, "conversion_id", [f"CV{5000+i}" for i in range(len(conversions))])

# leads = anyone with a lead_date, even if they never converted further (here we treat converted rows as also being leads)
# To make "Leads" a distinct funnel stage, mark ~40% extra as leads-only (no conversion)
leads_only = merged[merged["converted"] == 0].sample(frac=0.35, random_state=1).copy()
leads_only["lead_date"] = leads_only["signup_date"] + pd.to_timedelta(np.random.randint(0, 5, len(leads_only)), unit="D")
leads_count_by_campaign = pd.concat([conv_rows[["campaign_id"]], leads_only[["campaign_id"]]]).groupby("campaign_id").size()
campaigns["leads"] = campaigns["campaign_id"].map(leads_count_by_campaign).fillna(0).astype(int)

campaigns.to_csv("campaigns.csv", index=False)
customers.to_csv("customers.csv", index=False)
conversions.to_csv("conversions.csv", index=False)

print("campaigns:", campaigns.shape)
print("customers:", customers.shape)
print("conversions:", conversions.shape)
print(campaigns.head())
