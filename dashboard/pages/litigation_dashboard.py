import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Set page layout
st.set_page_config(layout="wide")

# Global color maps
COUNTRY_COLOR_MAP = {
    "India": "#1f77b4",
    "Iran": "#aec7e8",
    "Nigeria": "#d62728",
    "People's Republic of China": "#ff9896"
}

CASE_TYPE_COLOR_MAP = {
    "RAD Decisions": "#1f77b4",
    "Visa Officer Refusal": "#aec7e8",
    "Mandamus": "#d62728"
}

# Load data
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")
    lit = pd.read_excel(path, sheet_name="Final", skiprows=5)
    lit["Year"] = lit["LIT Leave Decision Date - Year"]

    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Discontinued.*', value='Discontinued', regex=True)
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Dismissed.*', value='Dismissed', regex=True)
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Allowed.*', value='Allowed', regex=True)

    lit = lit[~lit["LIT Leave Decision Desc"].isin(["Not Started at Leave", "No Leave Required", "Leave Exception"])]
    return lit

lit = load_data()


st.set_page_config(layout="wide")
st.markdown('# Country-Level Case Type & Outcome Analysis', unsafe_allow_html=True)


# ===== Section 1 =====
st.markdown("### Nigeria consistently leads in litigation cases, while India and Iran surged post-2021.")

# Top countries by count
top_lit = lit.groupby("Country of Citizenship")[["LIT Litigation Count"]].sum().reset_index()
top_lit = top_lit.sort_values("LIT Litigation Count", ascending=False).head(10)
fig_lit = px.bar(top_lit, x="Country of Citizenship", y="LIT Litigation Count",
                 color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig_lit, use_container_width=True)

# Total litigation count by year
st.markdown("### **Litigation volume** has stayed high since **2021**, showing persistent legal contestation.")
top_year = lit.groupby("Year")["LIT Litigation Count"].sum()
top_year = top_year[top_year.index.astype(str).str.isnumeric()]
top_year.index = top_year.index.astype(int)

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(x=top_year.index, y=top_year.values, mode='lines+markers', name='Total'))
for i, value in enumerate(top_year.values):
    fig_total.add_annotation(x=top_year.index[i], y=value, text=f"{int(value)}", showarrow=False, yshift=10)
fig_total.update_layout(
                        xaxis_title="Year", yaxis_title="Total Litigation Count",
                        plot_bgcolor='white', font=dict(size=16))
st.plotly_chart(fig_total, use_container_width=True)

# Litigation trends for top 4 countries
st.markdown("""
### <b><span style='color:#1f77b4'>India</span></b> and <b><span style='color:#aec7e8'>Iran</span></b> show sharp increases after 2020, while <b><span style='color:#d62728'>Nigeria</span></b> litigations increase up to 2021 and then decrease
""", unsafe_allow_html=True)
st.markdown("""
- <i><span style='color:#aec7e8'>Iran</span></i> & <i><span style='color:#1f77b4'>India</span></i>: a sharp rise in volume since 2020. 
- <i><span style='color:#d62728'>Nigeria</span></i>: consistently high in volume, dropped sharply since 2021. 
- <i><span style='color:#ff9896'>China</span></i>: relatively stable over the years.
""", unsafe_allow_html=True)
top4 = ["Nigeria", "India", "Iran", "People's Republic of China"]
trend_df = lit[lit["Country of Citizenship"].isin(top4)]
trend_df = trend_df.groupby(["Country of Citizenship", "Year"])["LIT Litigation Count"].sum().reset_index()
fig_trend = px.line(trend_df, x="Year", y="LIT Litigation Count", color="Country of Citizenship", 
                    color_discrete_map=COUNTRY_COLOR_MAP)
st.plotly_chart(fig_trend, use_container_width=True)


# ===== Section 2 =====
st.markdown("""
### <b><span style='color:{mandamus}'>Mandamus surges</span></b> in China, <b><span style='color:{visa}'>Visa Refusals</span></b> dominate Iran, <b><span style='color:{rad}'>RAD peaks</span></b> in Nigeria.
""".format(
    mandamus=CASE_TYPE_COLOR_MAP["Mandamus"],
    visa=CASE_TYPE_COLOR_MAP["Visa Officer Refusal"],
    rad=CASE_TYPE_COLOR_MAP["RAD Decisions"]
), unsafe_allow_html=True)

st.markdown("""
- **Nigeria** and **India**: Dominated by <span style='color:#1f77b4'><b>RAD Decisions</b></span>. **Nigeria** peaked in 2021, then declined. 
- **Iran**: Driven almost entirely by <span style='color:#aec7e8'><b>Visa Officer Refusal</b></span> cases, peaking near 1,900 in 2023. 
- **China**: Shows a sharp rise in <span style='color:#d62728'><b>Mandamus</b></span> applications in 2023 with over 300 cases.
""", unsafe_allow_html=True)

valid_case_types = list(CASE_TYPE_COLOR_MAP.keys())
countries = {"People's Republic of China": "China", "India": "India", "Iran": "Iran", "Nigeria": "Nigeria"}

# Create a 1-row, 4-column subplot layout
fig = make_subplots(
    rows=1,
    cols=4,
    shared_yaxes=True,
    subplot_titles=list(countries.values()),
    horizontal_spacing=0.03
)

for col_idx, (country_key, country_name) in enumerate(countries.items(), start=1):
    df_country = lit[(lit["Country of Citizenship"] == country_key) & 
                     (lit["LIT Case Type Group Desc"].isin(valid_case_types))]
    
    grouped = df_country.groupby(["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"])["LIT Litigation Count"].sum().reset_index()
    
    pivot_df = grouped.pivot(index="LIT Leave Decision Date - Year", columns="LIT Case Type Group Desc", 
                              values="LIT Litigation Count").fillna(0).sort_index()

    for case_type in valid_case_types:
        if case_type in pivot_df.columns:
            fig.add_trace(
                go.Bar(
                    x=pivot_df[case_type],
                    y=pivot_df.index,
                    orientation='h',
                    name=case_type,
                    marker_color=CASE_TYPE_COLOR_MAP[case_type],
                    showlegend=False,  
                    text=pivot_df[case_type],
                    textposition='auto'
                ),
                row=1,
                col=col_idx
            )

# Layout styling
fig.update_layout(
    height=700,
    width=1400,
    barmode='stack',
    plot_bgcolor='white',
    font=dict(size=15),
)

# Remove x-axes
for i in range(1, 5):
    fig.update_xaxes(visible=False, row=1, col=i)

fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text}</b>", font_size=14))

st.plotly_chart(fig, use_container_width=True)

# ===== Section 3 =====
st.markdown("""
### Majority of <span style='color:#d62728'><b>Mandamus</b></span> and <span style='color:#aec7e8'><b>Visa Officer Refusal</b></span> litigation are discontinued, while <span style='color:#1f77b4'><b>RAD Decisions</b></span> are more often <b>dismissed</b>.
""", unsafe_allow_html=True)
# Step 1: Group by case type and decision
grouped_df = lit.groupby(["LIT Case Type Group Desc", "LIT Leave Decision Desc"])["LIT Litigation Count"].sum().reset_index()

# Step 2: Filter for relevant case types
specific_case_types = list(CASE_TYPE_COLOR_MAP.keys())
filtered_df = grouped_df[grouped_df["LIT Case Type Group Desc"].isin(specific_case_types)]

# Step 3: Calculate percentage of each decision within each case type
filtered_df["Percentage"] = (
    filtered_df.groupby("LIT Case Type Group Desc")["LIT Litigation Count"]
    .transform(lambda x: (x / x.sum()) * 100)
).round(2)

# Step 4: Plot dumbbell-style chart with actual percentages and connection lines
fig = go.Figure()

# Iterate by decision type
for decision in filtered_df["LIT Leave Decision Desc"].unique():
    subset = filtered_df[filtered_df["LIT Leave Decision Desc"] == decision]

    # Determine min/max percent to draw a connecting line
    min_percent = subset["Percentage"].min()
    max_percent = subset["Percentage"].max()

    # Draw gray line connecting min and max points
    fig.add_trace(go.Scatter(
        x=[min_percent, max_percent],
        y=[decision, decision],
        mode="lines",
        line=dict(color="lightgray", width=3),
        showlegend=False
    ))

    # Add markers + annotations for each case type's percentage
    for _, row in subset.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Percentage"]],
            y=[decision],
            mode="markers",
            marker=dict(size=18, color=CASE_TYPE_COLOR_MAP[row["LIT Case Type Group Desc"]]),
            name=row["LIT Case Type Group Desc"],
            showlegend=False
        ))

        fig.add_annotation(
            x=row["Percentage"],
            y=decision,
            text=f"{row['Percentage']}%",
            showarrow=False,
            font=dict(size=14, color='white'),
            align='center',
            bgcolor=CASE_TYPE_COLOR_MAP[row["LIT Case Type Group Desc"]],
            borderpad=4,
            yshift=12
        )

# Update layout
fig.update_layout(
    xaxis=dict(title="Percentage within Case Type", zeroline=False),
    yaxis=dict(title="Leave Decision", autorange="reversed", gridcolor="white"),
    height=700,
    width=1500,
    plot_bgcolor="white",
    hovermode="closest",
    font=dict(family="Arial", size=18),
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center")
)

st.plotly_chart(fig, use_container_width=True)

# ===== Section 4 =====
st.markdown("""
### <b><span style='color:#1f77b4'>India</span></b> and <b><span style='color:#aec7e8'>Iran</span></b> have seen the sharpest rise in <b>dismissed</b> and <b>discontinued</b> cases since 2021.
""", unsafe_allow_html=True)

st.markdown("""
- <b>Allowed</b>: Remain consistently low across all countries. 
- <b>Discontinued</b>: <span style='color:#aec7e8'>Iran</span> shows a steep increase from 2020, peaking in 2023 with nearly 1,000 cases. 
- <b>Dismissed</b>: <span style='color:#1f77b4'>India</span> and <span style='color:#aec7e8'>Iran</span> show sharp increases. 
- <span style='color:#d62728'>Nigeria</span> shows a decline since 2021 across all outcome types.
""", unsafe_allow_html=True)

df_filtered = lit[(lit['LIT Leave Decision Desc'].isin(['Discontinued', 'Dismissed', 'Allowed'])) &
                 (lit['Country of Citizenship'].isin(top4))]
grouped = df_filtered.groupby(['LIT Leave Decision Date - Year', 'Country of Citizenship', 'LIT Leave Decision Desc'])["LIT Litigation Count"].sum().reset_index()

fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=['Allowed', 'Discontinued', 'Dismissed'])

for i, case in enumerate(['Allowed', 'Discontinued', 'Dismissed']):
    for country in top4:
        df_subset = grouped[(grouped['LIT Leave Decision Desc'] == case) &
                            (grouped['Country of Citizenship'] == country)]
        fig.add_trace(go.Scatter(x=df_subset['LIT Leave Decision Date - Year'], y=df_subset['LIT Litigation Count'],
                                 mode='lines+markers', name=country if i == 0 else None, legendgroup=country,
                                 showlegend=(i == 0), line=dict(color=COUNTRY_COLOR_MAP[country])),
                      row=1, col=i+1)
    fig.update_xaxes(title_text="Year", row=1, col=i+1)
    if i == 0:
        fig.update_yaxes(title_text="Total Litigation Count", row=1, col=i+1)

fig.update_layout(height=500, width=1200, showlegend=True)
st.plotly_chart(fig, use_container_width=True)