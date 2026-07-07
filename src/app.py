import streamlit as st
import pandas as pd
import plotly.express as px


import base64


st.set_page_config(
    page_title="Where Should You Open Your Next Business?",
    page_icon="images/maple-syrup.png",
    layout="wide"
)

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("images/stanley.jpg")

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
        background-image:
        linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)),
        url("data:image/jpg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

.stButton button {{
    background-color: white !important;
    color: #13344E !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    font-weight: 600 !important;
}}
.st-key-data_table_box, 
.st-key-compare_box, 
.st-key-scatter_box, 
.st-key-lookup_box, 
.st-key-builder_box {{
    background-color: rgba(255, 255, 255, 0.90) !important;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.5);
}}

h1 {{
    text-align: center;
    color: white !important;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.6);
}}

h3 {{
    color: #13344E !important;
}}

p {{
    color: #13344E  !important;
    font-size: 15px !important;
    font-weight: 500;
}}

label {{
    color: #1F2937 !important;
    font-weight: 600;
}}


.stSelectbox div[data-baseweb="select"] {{
    color: #1F2937 !important;
}}




</style>
""", unsafe_allow_html=True)


df = pd.read_csv("data/processed/opportunity_metrics_by_area.csv")


st.title("Where Should You Open Your Next Business?")


if "page" not in st.session_state:
    st.session_state.page = "Data Table"

# --- Menu buttons ---
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("Data Table", use_container_width=True):
    st.session_state.page = "Data Table"
if col2.button("Compare Metrics", use_container_width=True):
    st.session_state.page = "Compare Metrics"
if col3.button("Cost vs Traffic", use_container_width=True):
    st.session_state.page = "Cost vs Traffic"
if col4.button("Neighbourhood Lookup", use_container_width=True):
    st.session_state.page = "Neighbourhood Lookup"
if col5.button("Opportunity Builder", use_container_width=True):
    st.session_state.page = "Opportunity Builder"

st.divider()

descriptions = {
    "opportunity_score": "A combined score (0-100) blending all four metrics below: less competition, more traffic, lower cost, and more momentum all push this score higher. Higher is better.",
    "competitor_count": "Number of active restaurant/food licences in this neighbourhood. Fewer competitors generally means an easier market to enter.",
    "ticket_volume": "Number of parking tickets issued in this neighbourhood. Used as a rough proxy for how busy/active an area is — more tickets suggests more people and cars around.",
    "avg_property_value": "Average assessed property value (land + building) in this neighbourhood. Higher values generally mean higher costs to rent or buy a space here.",
    "recent_permit_count": "Number of building permits issued in the last 3 years. A higher count suggests the neighbourhood is actively developing and growing.",
}

# --- DATA TABLE ---
if st.session_state.page == "Data Table":
    with st.container(border=True, key="data_table_box"):
        st.subheader("Data Table")
        st.write("If you'd like access to the full underlying dataset, please email me at gemmaregan1902@gmail.com.")

# --- COMPARE METRICS ---
elif st.session_state.page == "Compare Metrics":
    with st.container(border=True, key="compare_box"):
        st.subheader("Compare Neighbourhoods by Metric")
        metric = st.selectbox(
            "Choose a metric to view:",
            options=["opportunity_score", "competitor_count", "ticket_volume", "avg_property_value", "recent_permit_count"]
        )
        st.caption(descriptions[metric])

        ascending = metric in ["competitor_count", "avg_property_value"]
        df_sorted = df.sort_values(metric, ascending=ascending)
        df_sorted["LocalArea"] = pd.Categorical(
            df_sorted["LocalArea"], categories=df_sorted["LocalArea"], ordered=True
        )
        # st.bar_chart(df_sorted.set_index("LocalArea")[metric])
        fig_bar = px.bar(
            df_sorted, x="LocalArea", y=metric,
            color_discrete_sequence=["#2A9D8F"] # change this hex code to any color you want
        )
        fig_bar.update_layout(
            plot_bgcolor="rgba(255,255,255,0.6)",   # chart area background
            paper_bgcolor="rgba(255,255,255,0)",    # area around the chart (transparent)
            xaxis_title=None,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# --- COST VS TRAFFIC ---
elif st.session_state.page == "Cost vs Traffic":
        with st.container(border=True, key="scatter_box"):
            st.subheader("Cost vs. Traffic, Sized and Colored by Opportunity Score")
            st.caption("Each dot is a neighbourhood. Bottom-right (low cost, high traffic) is generally the sweet spot. Bigger and greener dots = higher opportunity score. Hover over any dot to see its name and exact numbers.")

            fig = px.scatter(
                df, x="avg_property_value", y="ticket_volume",
                size="opportunity_score", color="opportunity_score",
                color_continuous_scale="Tealgrn", hover_name="LocalArea",
                hover_data={"avg_property_value": ":,.0f", "ticket_volume": ":,.0f", "opportunity_score": ":.1f"},
                labels={"avg_property_value": "Avg Property Value ($)", "ticket_volume": "Parking Ticket Volume"},
                size_max=40
            )

            fig.update_layout(
                plot_bgcolor="rgba(255,255,255,0.6)",
                paper_bgcolor="rgba(255,255,255,0)",
            )
            
            st.plotly_chart(fig, use_container_width=True)
# --- NEIGHBOURHOOD LOOKUP ---
elif st.session_state.page == "Neighbourhood Lookup":
    with st.container(border=True, key="lookup_box"):
        st.subheader("Look Up a Specific Neighbourhood")
        selected_area = st.selectbox("Pick a neighbourhood:", options=sorted(df["LocalArea"].unique()))
        area_data = df[df["LocalArea"] == selected_area].iloc[0]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Opportunity Score", f"{area_data['opportunity_score']:.1f}")
        c2.metric("Competitors", int(area_data['competitor_count']))
        c3.metric("Traffic (tickets)", f"{int(area_data['ticket_volume']):,}")
        c4.metric("Avg Property Value", f"${area_data['avg_property_value']:,.0f}")
        c5.metric("Recent Permits", int(area_data['recent_permit_count']))

        rank = int(df["opportunity_score"].rank(ascending=False)[df["LocalArea"] == selected_area].values[0])
        st.caption(f"{selected_area} ranks #{rank} out of {len(df)} neighbourhoods by overall opportunity score.")

# --- OPPORTUNITY BUILDER ---
elif st.session_state.page == "Opportunity Builder":
    with st.container(border=True, key="builder_box"):
        st.subheader("Build Your Own Opportunity Score")
        st.caption("Adjust how much each factor matters to you, and see the ranking change live.")

        w_competition = st.slider("Importance of LOW competition", 0, 100, 30)
        w_traffic = st.slider("Importance of HIGH traffic", 0, 100, 30)
        w_cost = st.slider("Importance of LOW cost", 0, 100, 20)
        w_momentum = st.slider("Importance of HIGH momentum", 0, 100, 20)

        total_weight = w_competition + w_traffic + w_cost + w_momentum

        if total_weight == 0:
            st.warning("Move at least one slider above 0 to see a ranking.")
        else:
            df["custom_score"] = (
                (100 - df["competitor_pctl"]) * (w_competition / total_weight) +
                df["traffic_pctl"] * (w_traffic / total_weight) +
                (100 - df["cost_pctl"]) * (w_cost / total_weight) +
                df["momentum_pctl"] * (w_momentum / total_weight)
            )

            custom_sorted = df.sort_values("custom_score", ascending=False)
            custom_sorted["LocalArea"] = pd.Categorical(
                custom_sorted["LocalArea"], categories=custom_sorted["LocalArea"], ordered=True
            )

            st.write(f"**Your #1 pick: {custom_sorted.iloc[0]['LocalArea']}**")
            fig_builder = px.bar(
                custom_sorted, x="LocalArea", y="custom_score",
                color_discrete_sequence=["#3D8B6E"]
            )       
            fig_builder.update_layout(
                plot_bgcolor="rgba(255,255,255,0.6)",
                paper_bgcolor="rgba(255,255,255,0)",
                xaxis_title=None,
            )
            st.plotly_chart(fig_builder, use_container_width=True)