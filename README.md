Prerequisites

## 📦 Prerequisites

```bash
  pip install -r requirements.txt
```

Input Files Required

impressions_log.csv – Ad impression requests

click_log.csv – User clicks on ads

revenue_log.csv – Revenue from clicks

keyword_blacklist.csv – Keywords to exclude

```bash
  python3 main.py
```

Output Files Generated

campaign_keyword_report.csv – Detailed metrics per campaign-keyword-country-device

campaign_summary.csv – Summary per campaign

Key Metrics Calculated
CTR (Click-through rate): clicks / impressions

Fill Rate: filled_impressions / total_impressions

Profit Margin (%): (Revenue - Cost) / Cost × 100

Anomaly Flags: Outliers detected using 5th and 95th percentiles



campaign_keyword_report.csv:
campaign_id,keyword_id,country,device,total_impressions,filled_impressions,total_clicks,total_cost,total_revenue,gross_profit,profit_margin %,CTR,Fill Rate,is_ctr_anomaly,is_fillrate_anomaly
1,5,US,desktop,1250,980,45,12.50,18.75,6.25,50.0,0.0459,0.784,False,False
campaign_summary.csv:
campaign_id,total_impressions,filled_impressions,total_clicks,total_cost,total_revenue,gross_profit,profit_margin %,num_ctr_anomalies,num_fillrate_anomalies
1,15420,12050,456,145.67,234.89,89.22,61.25,3,1
