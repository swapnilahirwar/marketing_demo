import os

import numpy as np
import pandas as pd


def generate_marketing_data(n_rows: int = 500, export_path: str | None = None) -> pd.DataFrame:
    """Generate a realistic marketing dataset and optionally export it to Excel."""
    np.random.seed(42)

    platforms = ["Meta", "Google", "LinkedIn"]
    audience_segments = [
        "Tech Bros 25-34",
        "Soccer Moms",
        "Fitness Enthusiasts",
        "Luxury Shoppers",
        "B2B Decision Makers",
        "Eco-Conscious Millennials",
        "Budget Travelers",
        "Urban Creatives",
        "Parents with Toddlers",
        "Home Improvement DIYers",
    ]
    ad_creatives = [
        "Spring Sale", "Product Launch", "Limited Offer", "Customer Testimonial",
        "Free Webinar", "Instant Savings", "New Collection", "Case Study Ad"
    ]

    data = []
    for i in range(n_rows):
        campaign_id = f"CMP-{1000 + i}"
        platform = np.random.choice(platforms, p=[0.45, 0.40, 0.15])
        audience = np.random.choice(audience_segments)
        creative = np.random.choice(ad_creatives)

        base_spend = np.random.normal(1200, 520)
        spend = max(100, base_spend + np.random.normal(0, 150))
        impressions = int(max(5000, np.random.normal(65000, 22000)))

        # Use platform and audience segment to influence performance
        if audience in ["Tech Bros 25-34", "Soccer Moms", "Budget Travelers"]:
            ctr = np.random.normal(0.004, 0.0015)
            if audience == "Soccer Moms":
                ctr *= 0.7
            conversions = int(max(1, np.random.poisson(14)))
        else:
            ctr = np.random.normal(0.008, 0.002)
            conversions = int(max(2, np.random.poisson(28)))

        # intentionally skew a few segments to poor performance
        if audience == "Tech Bros 25-34":
            ctr = np.random.normal(0.0025, 0.0008)
            conversions = int(max(1, np.random.poisson(8)))
        elif audience == "Soccer Moms":
            ctr = np.random.normal(0.0018, 0.0007)
            conversions = int(max(1, np.random.poisson(6)))
        elif audience == "Budget Travelers":
            ctr = np.random.normal(0.003, 0.001)
            conversions = int(max(1, np.random.poisson(10)))

        clicks = int(max(10, impressions * max(0.0005, ctr)))
        conversion_rate = np.random.uniform(0.03, 0.12)
        if audience in ["Tech Bros 25-34", "Soccer Moms", "Budget Travelers"]:
            conversion_rate *= 0.7
        conversions = min(clicks, int(max(1, clicks * conversion_rate)))

        spend = round(spend, 2)
        ctr = round(clicks / impressions, 4)
        cpa = round(spend / max(1, conversions), 2)
        roas = round(np.random.normal(3.5, 1.1) if conversions > 0 else 0, 2)

        data.append({
            "Campaign ID": campaign_id,
            "Platform": platform,
            "Audience Segment": audience,
            "Ad Creative Name": creative,
            "Spend ($)": spend,
            "Impressions": impressions,
            "Clicks": clicks,
            "Conversions": conversions,
            "CTR": ctr,
            "CPA ($)": cpa,
            "ROAS": roas,
        })

    df = pd.DataFrame(data)

    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        df.to_excel(export_path, index=False)

    return df


if __name__ == "__main__":
    df = generate_marketing_data(export_path=os.path.join(os.path.dirname(__file__), "marketing_data.xlsx"))
    print(f"Generated {len(df)} rows of marketing data and exported to data/marketing_data.xlsx")
