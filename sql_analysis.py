import sqlite3
import pandas as pd

conn = sqlite3.connect(":memory:")
campaigns = pd.read_csv("campaigns.csv")
customers = pd.read_csv("customers.csv")
conversions = pd.read_csv("conversions.csv")

campaigns.to_sql("campaigns", conn, index=False, if_exists="replace")
customers.to_sql("customers", conn, index=False, if_exists="replace")
conversions.to_sql("conversions", conn, index=False, if_exists="replace")

print("=== Campaign performance & ROI by channel ===")
q1 = """
SELECT c.channel,
       ROUND(SUM(c.campaign_cost),2) AS total_cost,
       ROUND(SUM(cv.revenue),2) AS total_revenue,
       ROUND((SUM(cv.revenue) - SUM(c.campaign_cost)) * 1.0 / SUM(c.campaign_cost), 3) AS roi,
       COUNT(DISTINCT cv.conversion_id) AS conversions
FROM campaigns c
LEFT JOIN conversions cv ON c.campaign_id = cv.campaign_id
GROUP BY c.channel
ORDER BY roi DESC;
"""
df1 = pd.read_sql(q1, conn)
print(df1.to_string(index=False))
df1.to_csv("sql_campaign_roi_by_channel.csv", index=False)

print("\n=== Customer conversion rate by segment ===")
q2 = """
SELECT cu.segment,
       COUNT(DISTINCT cu.customer_id) AS total_customers,
       COUNT(DISTINCT cv.customer_id) AS converted_customers,
       ROUND(COUNT(DISTINCT cv.customer_id) * 1.0 / COUNT(DISTINCT cu.customer_id), 3) AS conversion_rate,
       ROUND(AVG(cv.revenue), 2) AS avg_revenue_per_conversion
FROM customers cu
LEFT JOIN conversions cv ON cu.customer_id = cv.customer_id
GROUP BY cu.segment
ORDER BY conversion_rate DESC;
"""
df2 = pd.read_sql(q2, conn)
print(df2.to_string(index=False))
df2.to_csv("sql_conversion_by_segment.csv", index=False)

print("\n=== Channel comparison: cost-per-lead & cost-per-conversion ===")
q3 = """
SELECT c.channel,
       SUM(c.leads) AS total_leads,
       COUNT(DISTINCT cv.conversion_id) AS total_conversions,
       ROUND(SUM(c.campaign_cost) * 1.0 / NULLIF(SUM(c.leads),0), 2) AS cost_per_lead,
       ROUND(SUM(c.campaign_cost) * 1.0 / NULLIF(COUNT(DISTINCT cv.conversion_id),0), 2) AS cost_per_conversion
FROM campaigns c
LEFT JOIN conversions cv ON c.campaign_id = cv.campaign_id
GROUP BY c.channel
ORDER BY cost_per_conversion ASC;
"""
df3 = pd.read_sql(q3, conn)
print(df3.to_string(index=False))
df3.to_csv("sql_channel_comparison.csv", index=False)
