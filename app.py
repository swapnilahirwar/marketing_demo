import time

import streamlit as st
import plotly.express as px

from data.data_generation import generate_marketing_data


st.set_page_config(
    page_title="Agentic Campaign Optimization Engine",
    page_icon="🚀",
    layout="wide",
)

st.markdown(
    """
    <style>
    .page-title {font-size: 2.8rem; font-weight: 800; color: #0f172a; margin-bottom: 0.1rem;}
    .page-subtitle {font-size: 1rem; color: #475569; margin-top: 0; margin-bottom: 1.4rem;}
    .section-card {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 22px 24px; margin-bottom: 24px;}
    .metric-card {background: #f8fafc; border-radius: 18px; padding: 18px;}
    .stApp {background-color: #f8fafc;}
    .streamlit-expanderHeader {font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def load_data() -> None:
    """Load or generate the dataset into Streamlit session state."""
    if "marketing_df" not in st.session_state:
        st.session_state.marketing_df = generate_marketing_data(
            n_rows=500,
            export_path="data/marketing_data.xlsx",
        )


def analyze_segment_performance(df, segment: str) -> dict:
    """Return summary metrics for a selected audience segment."""
    segment_df = df[df["Audience Segment"] == segment]
    return {
        "Platform": segment_df["Platform"].mode().iloc[0],
        "Spend": segment_df["Spend ($)"].sum(),
        "Impressions": segment_df["Impressions"].sum(),
        "Clicks": segment_df["Clicks"].sum(),
        "Conversions": segment_df["Conversions"].sum(),
        "CTR": segment_df["CTR"].mean(),
        "CPA": segment_df["CPA ($)"].mean(),
        "ROAS": segment_df["ROAS"].mean(),
    }


def create_ad_copy_variants(segment: str, platform: str) -> list[dict]:
    """Generate plausible ad copy variants for an underperforming segment."""
    templates = [
        {
            "headline": f"{segment} deserves smarter savings.",
            "text": (
                f"Stop wasting ad budget on generic copy. This offer is built for {segment} with a clear benefit, "
                "strong social proof, and an urgent call to action."
            ),
        },
        {
            "headline": f"More impact for {segment} on {platform}.",
            "text": (
                "Speak directly to what matters most to this audience: relevance, convenience, and trust. "
                "Use benefit-first language and a single strong CTA."
            ),
        },
        {
            "headline": "Turn attention into action with better messaging.",
            "text": (
                f"Highlight the exact value {segment} cares about, remove friction, and invite them to act now with a compelling offer."
            ),
        },
    ]
    return templates


def campaign_dashboard(df):
    render_page_header(
        "Campaign Dashboard",
        "A polished executive view of the campaign landscape with the metrics and charts the agent uses to detect risk and prioritize optimization.",
    )

    total_spend = df["Spend ($)"].sum()
    total_conversions = df["Conversions"].sum()
    avg_cpa = df["CPA ($)"].mean()
    avg_roas = df["ROAS"].mean()
    avg_ctr = df["CTR"].mean()

    top_segment = (
        df.groupby("Audience Segment").agg(Conversions=("Conversions", "sum"))
        .sort_values(by="Conversions", ascending=False)
        .head(1)
        .index[0]
    )
    worst_platform = (
        df.groupby("Platform").agg(CPA=("CPA ($)", "mean"))
        .sort_values(by="CPA", ascending=False)
        .head(1)
        .index[0]
    )

    with st.container():
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Spend", f"${total_spend:,.0f}")
        kpi2.metric("Total Conversions", f"{total_conversions:,}")
        kpi3.metric("Average CPA", f"${avg_cpa:,.2f}")
        kpi4.metric("Average CTR", f"{avg_ctr:.2%}")

        kpi5, kpi6 = st.columns([1, 1])
        kpi5.metric("Top-Converting Segment", top_segment)
        kpi6.metric("Highest CPA Platform", worst_platform)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.1, 1])
    with col1:
        fig_spend_conv = px.scatter(
            df,
            x="Spend ($)",
            y="Conversions",
            color="Platform",
            size="Impressions",
            title="Spend vs Conversions",
            template="plotly_white",
            hover_data=["Audience Segment", "CPA ($)", "ROAS"],
        )
        st.plotly_chart(fig_spend_conv, use_container_width=True)
    with col2:
        platform_summary = df.groupby("Platform").agg(
            CPA=("CPA ($)", "mean"),
            ROAS=("ROAS", "mean"),
            Spend=("Spend ($)", "sum"),
        ).reset_index()
        fig_cpa = px.bar(
            platform_summary,
            x="Platform",
            y="CPA",
            title="Average CPA by Platform",
            text="CPA",
            template="plotly_white",
        )
        fig_cpa.update_layout(yaxis_title="CPA ($)")
        st.plotly_chart(fig_cpa, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Top Audience Segment Performance")
    segment_history = (
        df.groupby(["Platform", "Audience Segment"]).agg(
            Spend=("Spend ($)", "sum"),
            Conversions=("Conversions", "sum"),
            CTR=("CTR", "mean"),
            CPA=("CPA ($)", "mean"),
        )
        .reset_index()
    )
    top_segments = segment_history.sort_values(by="Conversions", ascending=False).head(6)
    chart = px.bar(
        top_segments,
        x="Audience Segment",
        y="Conversions",
        color="Platform",
        title="Top 6 Audience Segments by Conversions",
        template="plotly_white",
        text="Conversions",
    )
    chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Platform Spend Efficiency")
    efficiency = df.groupby("Platform").agg(
        Spend=("Spend ($)", "sum"),
        Conversions=("Conversions", "sum"),
    ).reset_index()
    efficiency["Spend per Conversion"] = efficiency["Spend"] / efficiency["Conversions"]
    fig_efficiency = px.bar(
        efficiency,
        x="Platform",
        y="Spend per Conversion",
        title="Spend per Conversion by Platform",
        template="plotly_white",
        text="Spend per Conversion",
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("How the agent uses this dashboard"):
        st.write(
            "The agent watches spend, conversions, CTR, and CPA across platforms and segments. "
            "It uses these patterns to identify which creatives need rewriting and where budget should shift."
        )


def anomaly_detection(df):
    render_page_header(
        "Anomaly Detection",
        "A focused view of the segments the agent has flagged for urgent creative and budget intervention.",
    )

    thresholds = {
        "CPA ($)": 50,
        "CTR": 0.005,
    }
    segment_summary = (
        df.groupby("Audience Segment")
        .agg(
            Spend=("Spend ($)", "sum"),
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
            Conversions=("Conversions", "sum"),
            CTR=("CTR", "mean"),
            CPA=("CPA ($)", "mean"),
            ROAS=("ROAS", "mean"),
        )
        .reset_index()
    )

    segment_summary["Status"] = segment_summary.apply(
        lambda row: "Underperforming" if (row["CPA"] > thresholds["CPA ($)"] or row["CTR"] < thresholds["CTR"]) else "Healthy",
        axis=1,
    )

    underperformers = segment_summary[segment_summary["Status"] == "Underperforming"].sort_values(
        by=["CPA", "CTR"], ascending=[False, True]
    )

    if underperformers.empty:
        st.success("No underperforming segments were detected. All campaigns are within the healthy range.")
        return

    top_risks = underperformers.head(3)
    col1, col2, col3 = st.columns(3)
    col1.metric("Underperforming Segments", len(underperformers))
    col2.metric("Highest CPA", f"${top_risks.iloc[0]['CPA']:,.2f}")
    col3.metric("Lowest CTR", f"{top_risks.iloc[-1]['CTR']:.2%}")

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Underperforming Segment Details")
    st.caption("Thresholds: CPA > $50 or CTR < 0.5%")
    st.dataframe(underperformers, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    fig_underperformers = px.bar(
        underperformers,
        x="Audience Segment",
        y="CPA",
        color="CTR",
        title="Underperformers by CPA and CTR",
        template="plotly_white",
        text="CPA",
    )
    fig_underperformers.update_layout(xaxis_tickangle=-40)
    st.plotly_chart(fig_underperformers, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Why these segments matter"):
        st.write(
            "The agent focuses on segments where cost per acquisition is too high or click-through rate is too low. "
            "Optimizing these audiences typically unlocks the most immediate ROI gains."
        )


def creative_optimization(df):
    render_page_header(
        "Agentic Creative Optimization",
        "A workshop-ready creative lab where the AI agent diagnoses a weak audience and proposes new ad copy variants.",
    )

    segments = df[(df["CPA ($)"] > 50) | (df["CTR"] < 0.005)]["Audience Segment"].unique().tolist()
    if not segments:
        st.warning("No underperforming segments were found in this dataset.")
        return

    selection_col, advice_col = st.columns([1, 1.4])
    with selection_col:
        selected_segment = st.selectbox("Choose an underperforming segment", segments)
        segment_metrics = analyze_segment_performance(df, selected_segment)
        st.markdown("**Current segment performance**")
        st.write(
            f"- **Platform:** {segment_metrics['Platform']}  \
            - **Spend:** ${segment_metrics['Spend']:,.0f}  \
            - **Impressions:** {segment_metrics['Impressions']:,}  \
            - **Clicks:** {segment_metrics['Clicks']:,}  \
            - **Conversions:** {segment_metrics['Conversions']:,}  \
            - **CTR:** {segment_metrics['CTR']:.2%}  \
            - **CPA:** ${segment_metrics['CPA']:.2f}  \
            - **ROAS:** {segment_metrics['ROAS']:.2f}x"
        )

    with advice_col:
        st.info(
            "The AI agent evaluates CTR, CPA, and audience intent. It will recommend more targeted headlines, benefit-led messaging, and a clearer call to action."
        )

    run_button = st.button("Run AI Agent")
    if run_button:
        with st.spinner("Agent is analyzing performance and generating ad copy..."):
            st.progress(0.2)
            time.sleep(0.5)
            st.progress(0.55)
            time.sleep(0.5)
            st.progress(0.85)
            time.sleep(0.35)
            st.progress(1.0)

        st.success("AI Agent completed its analysis!")
        agent_recommendations = create_ad_copy_variants(
            selected_segment,
            segment_metrics["Platform"],
        )

        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Agent Diagnosis")
        st.write(
            "The agent found that this segment's existing creative performance is held back by generic messaging and unclear value. "
            "It recommends more emotion-led headlines, stronger relevance cues, and an action-driving offer."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        for idx, copy in enumerate(agent_recommendations, start=1):
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown(f"### Variant {idx}")
            st.markdown(f"**Headline:** {copy['headline']}")
            st.markdown(f"**Primary Text:** {copy['text']}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.balloons()


def budget_reallocation(df):
    render_page_header(
        "Budget Reallocation Engine",
        "A high-impact view of the agent's budget shift recommendation, tying reallocation to expected conversion uplift.",
    )

    summary = df.groupby("Audience Segment").agg(
        Spend=("Spend ($)", "sum"),
        Conversions=("Conversions", "sum"),
        CPA=("CPA ($)", "mean"),
    )
    summary = summary.sort_values(by="CPA", ascending=True).reset_index()

    current = summary.copy()
    recommended = current.copy()
    poor_segments = current[current["CPA"] > 50]["Audience Segment"].tolist()[:2]
    top_segments = current.head(3)["Audience Segment"].tolist()

    shift_amount = current[current["Audience Segment"].isin(poor_segments)]["Spend"].sum() * 0.20
    distribute = shift_amount / max(1, len(top_segments))

    recommended.loc[recommended["Audience Segment"].isin(poor_segments), "Spend"] *= 0.8
    recommended.loc[recommended["Audience Segment"].isin(top_segments), "Spend"] += distribute

    expected_delta = int(shift_amount * 0.14)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Reallocation Summary")
    st.write(
        "The agent identifies the weakest segment budgets and moves 20% of that spend to the best-performing audiences. "
        "This keeps overall campaign scale intact while improving efficiency."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Budget Shift", f"${shift_amount:,.0f}")
    c2.metric("Top Beneficiaries", ", ".join(top_segments))
    c3.metric("Projected Conversions", f"+{expected_delta}")

    chart_data = (
        current.head(6)
        .merge(recommended.head(6), on="Audience Segment", suffixes=("_Current", "_Recommended"))
    )
    chart_frame = chart_data.melt(
        id_vars=["Audience Segment"],
        value_vars=["Spend_Current", "Spend_Recommended"],
        var_name="Allocation",
        value_name="Spend",
    )
    chart_frame["Allocation"] = chart_frame["Allocation"].replace({
        "Spend_Current": "Current",
        "Spend_Recommended": "Recommended",
    })

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Budget Allocation")
        st.dataframe(current.head(10), use_container_width=True)
    with col2:
        st.subheader("Agent Recommended Allocation")
        st.dataframe(recommended.head(10), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    fig_budget_compare = px.bar(
        chart_frame,
        x="Audience Segment",
        y="Spend",
        color="Allocation",
        barmode="group",
        title="Current vs Recommended Budget Allocation",
        template="plotly_white",
        text="Spend",
    )
    fig_budget_compare.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_budget_compare, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("What the agent recommended"):
        st.write(
            "By shifting budget away from the weakest segments and into the strongest performers, the agent can create a more efficient spend mix. "
            "This is a simple, actionable recommendation for a live marketing optimization workshop."
        )


def main():
    load_data()
    df = st.session_state.marketing_df

    page = st.sidebar.selectbox(
        "Navigation",
        [
            "Campaign Dashboard",
            "Anomaly Detection",
            "Agentic Creative Optimization",
            "Budget Reallocation Engine",
        ],
    )

    if page == "Campaign Dashboard":
        campaign_dashboard(df)
    elif page == "Anomaly Detection":
        anomaly_detection(df)
    elif page == "Agentic Creative Optimization":
        creative_optimization(df)
    else:
        budget_reallocation(df)


if __name__ == "__main__":
    main()
