import pandas as pd
import numpy as np


def load_and_filter_data():
    """Load all CSV files and filter blacklisted keywords."""
    impressions = pd.read_csv('impressions_log.csv')
    clicks = pd.read_csv('click_log.csv')
    revenue = pd.read_csv('revenue_log.csv')
    blacklist = pd.read_csv('keyword_blacklist.csv')['keyword_id'].tolist()

    impressions = impressions[~impressions['keyword_id'].isin(blacklist)]
    clicks = clicks[~clicks['keyword_id'].isin(blacklist)]

    return impressions, clicks, revenue


def compute_metrics():
    """Compute all performance metrics using vectorized operations."""
    impressions, clicks, revenue = load_and_filter_data()

    imp_metrics = impressions.groupby(['campaign_id', 'keyword_id', 'country', 'device']).agg({
        'request_id': 'count',
        'is_filled': 'sum'
    }).rename(columns={'request_id': 'total_impressions', 'is_filled': 'filled_impressions'})
    click_metrics = clicks.groupby(['campaign_id', 'keyword_id', 'country', 'device']).agg({
        'click_id': 'count',
        'cpc': 'sum'
    }).rename(columns={'click_id': 'total_clicks', 'cpc': 'total_cost'})

    clicks_revenue = clicks.merge(revenue, on='click_id', how='left')
    rev_metrics = clicks_revenue.groupby(['campaign_id', 'keyword_id', 'country', 'device'])['revenue'].sum()
    metrics = imp_metrics.join(click_metrics, how='left').join(rev_metrics, how='left').fillna(0).reset_index()

    metrics['gross_profit'] = metrics['revenue'] - metrics['total_cost']
    metrics['profit_margin_pct'] = np.where(metrics['total_cost'] > 0,
                                            metrics['gross_profit'] / metrics['total_cost'] * 100, 0)
    metrics['ctr'] = np.where(metrics['filled_impressions'] > 0,
                              metrics['total_clicks'] / metrics['filled_impressions'], 0)
    metrics['fill_rate'] = np.where(metrics['total_impressions'] > 0,
                                    metrics['filled_impressions'] / metrics['total_impressions'], 0)

    return metrics


def detect_anomalies(metrics):
    """Add anomaly flags based on campaign-level percentiles."""
    percentiles = metrics.groupby('campaign_id')[['ctr', 'fill_rate']].agg([
        lambda x: np.percentile(x, 5),
        lambda x: np.percentile(x, 95)
    ])
    percentiles.columns = ['ctr_p5', 'ctr_p95', 'fill_rate_p5', 'fill_rate_p95']

    metrics_with_p = metrics.merge(percentiles, on='campaign_id')
    metrics_with_p['is_ctr_anomaly'] = ((metrics_with_p['ctr'] < metrics_with_p['ctr_p5']) |
                                        (metrics_with_p['ctr'] > metrics_with_p['ctr_p95']))
    metrics_with_p['is_fillrate_anomaly'] = ((metrics_with_p['fill_rate'] < metrics_with_p['fill_rate_p5']) |
                                             (metrics_with_p['fill_rate'] > metrics_with_p['fill_rate_p95']))

    return metrics_with_p[['campaign_id', 'keyword_id', 'country', 'device', 'total_impressions',
                           'filled_impressions', 'total_clicks', 'total_cost', 'revenue',
                           'gross_profit', 'profit_margin_pct', 'ctr', 'fill_rate',
                           'is_ctr_anomaly', 'is_fillrate_anomaly']].rename(columns={
        'revenue': 'total_revenue',
        'profit_margin_pct': 'profit_margin %',
        'ctr': 'CTR',
        'fill_rate': 'Fill Rate'
    })


def generate_campaign_summary(campaign_keyword_report):
    """Generate campaign-level summary."""
    summary = campaign_keyword_report.groupby('campaign_id').agg({
        'total_impressions': 'sum',
        'filled_impressions': 'sum',
        'total_clicks': 'sum',
        'total_cost': 'sum',
        'total_revenue': 'sum',
        'gross_profit': 'sum',
        'is_ctr_anomaly': 'sum',
        'is_fillrate_anomaly': 'sum'
    }).rename(columns={'is_ctr_anomaly': 'num_ctr_anomalies',
                       'is_fillrate_anomaly': 'num_fillrate_anomalies'})

    summary['profit_margin %'] = np.where(summary['total_cost'] > 0,
                                          summary['gross_profit'] / summary['total_cost'] * 100, 0)

    return summary.reset_index()


def main():
    """Execute the complete pipeline."""
    print("Computing campaign metrics")
    metrics = compute_metrics()

    print("Detecting anomalies")
    campaign_keyword_report = detect_anomalies(metrics)

    print("Generating campaign summary")
    campaign_summary = generate_campaign_summary(campaign_keyword_report)

    campaign_keyword_report.round(4).to_csv('campaign_keyword_report.csv', index=False)
    campaign_summary.round(4).to_csv('campaign_summary.csv', index=False)

    print(f"Generated reports for {len(campaign_summary)} campaigns")
    print(f"{len(campaign_keyword_report)} keyword combinations analyzed")
    print(f"{campaign_keyword_report['is_ctr_anomaly'].sum()} CTR anomalies detected")
    print(f"{campaign_keyword_report['is_fillrate_anomaly'].sum()} fill rate anomalies detected")


if __name__ == "__main__":
    main()
