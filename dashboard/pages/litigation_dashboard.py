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
st.title("Country-Level Case Type & Outcome Analysis")

# ===== Section 1 =====
st.header("Overview of Top Countries and Litigation Trends")
st.markdown("##### **Nigeria** consistently leads in litigation cases, while **India** and **Iran** surged post-2021.")

# Top countries by count
top_lit = lit.groupby("Country of Citizenship")[["LIT Litigation Count"]].sum().reset_index()
top_lit = top_lit.sort_values("LIT Litigation Count", ascending=False).head(10)
fig_lit = px.bar(top_lit, x="Country of Citizenship", y="LIT Litigation Count", 
                 title="Top 10 Countries by Litigation Count", 
                 color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig_lit, use_container_width=True)

# Total litigation count by year
st.markdown("##### **Litigation volume** has stayed high since **2021**, showing persistent legal contestation.")
top_year = lit.groupby("Year")["LIT Litigation Count"].sum()
top_year = top_year[top_year.index.astype(str).str.isnumeric()]
top_year.index = top_year.index.astype(int)

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(x=top_year.index, y=top_year.values, mode='lines+markers', name='Total'))
for i, value in enumerate(top_year.values):
    fig_total.add_annotation(x=top_year.index[i], y=value, text=f"{int(value)}", showarrow=False, yshift=10)
fig_total.update_layout(title="Total Litigation Count by Year",
                        xaxis_title="Year", yaxis_title="Total Litigation Count",
                        plot_bgcolor='white', font=dict(size=16))
st.plotly_chart(fig_total, use_container_width=True)

# Litigation trends for top 4 countries
st.markdown("##### **India and Iran** show sharp increases after **2020**, while **Nigeria** remains high throughout.")
top4 = ["Nigeria", "India", "Iran", "People's Republic of China"]
trend_df = lit[lit["Country of Citizenship"].isin(top4)]
trend_df = trend_df.groupby(["Country of Citizenship", "Year"])["LIT Litigation Count"].sum().reset_index()
fig_trend = px.line(trend_df, x="Year", y="LIT Litigation Count", color="Country of Citizenship", 
                    title="Litigation Trends (2018–2023)", color_discrete_map=COUNTRY_COLOR_MAP)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("**Note:** _Iran & India_: a sharp raise in volume since 2020. _Nigeria_: consistently high in volume, dropped sharply since 2021. _China_: relatively stable over the years.")


# ===== Section 2 =====
st.header("Case Type Breakdown Over Time for Top 4 Countries")
st.markdown("##### **Mandamus surges** in China, **Visa Refusals** dominate Iran, **RAD peaks** in Nigeria.")

valid_case_types = list(CASE_TYPE_COLOR_MAP.keys())
countries = {"People's Republic of China": "China", "India": "India", "Iran": "Iran", "Nigeria": "Nigeria"}

fig = make_subplots(rows=2, cols=4, shared_xaxes=False, shared_yaxes=True, vertical_spacing=0.1, 
                    horizontal_spacing=0.03, subplot_titles=list(countries.values()), row_heights=[0.2, 0.8])

for col_idx, (country_key, country_name) in enumerate(countries.items(), start=1):
    df_country = lit[(lit["Country of Citizenship"] == country_key) & 
                     (lit["LIT Case Type Group Desc"].isin(valid_case_types))]
    grouped = df_country.groupby(["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"])["LIT Litigation Count"].sum().reset_index()
    pivot_df = grouped.pivot(index="LIT Leave Decision Date - Year", columns="LIT Case Type Group Desc", 
                              values="LIT Litigation Count").fillna(0).sort_index()

    for case_type in valid_case_types:
        if case_type in pivot_df.columns:
            fig.add_trace(go.Bar(x=pivot_df[case_type].astype(str), y=pivot_df.index, orientation="h",
                                 name=case_type, text=pivot_df[case_type], textposition="outside",
                                 marker_color=CASE_TYPE_COLOR_MAP[case_type], showlegend=(col_idx == 1)),
                          row=2, col=col_idx)

fig.update_layout(height=800, width=1200, barmode="stack", plot_bgcolor="white", 
                  title_text="Case Type Breakdown Over Time (2018–2023)", font=dict(size=14), 
                  legend_title_text="Case Types")
st.plotly_chart(fig, use_container_width=True)
st.markdown("**Note:** _Nigeria & India_: Dominated by RAD Decisions. Nigeria peaked in 2021, then declined. _Iran_: Driven almost entirely by Visa Officer Refusal cases, peaking near 1,900 in 2023. _China_: Shows a sharp rise in Mandamus applications in 2023 with over 300 cases.")


# ===== Section 3 =====
st.header("Decision Type by Case Category Dumbbell Chart")
st.markdown("##### **Mandamus** cases are **more likely to be allowed**, while **Visa Refusals** are more often **dismissed**.")

# Step 1: Compute global totals for each decision type
global_total = lit.groupby("LIT Leave Decision Desc")["LIT Litigation Count"].sum().reset_index()
global_total["Total_Percentage"] = (global_total["LIT Litigation Count"] / global_total["LIT Litigation Count"].sum() * 100).round(2)

# Step 2: Group by case type and decision
grouped_df = lit.groupby(["LIT Case Type Group Desc", "LIT Leave Decision Desc"])["LIT Litigation Count"].sum().reset_index()

# Step 3: Filter for specific case types
specific_case_types = list(CASE_TYPE_COLOR_MAP.keys())
filtered_df = grouped_df[grouped_df["LIT Case Type Group Desc"].isin(specific_case_types)]

# Step 4: Compute percentages within case type
filtered_df["Percentage"] = (
    filtered_df.groupby("LIT Case Type Group Desc")["LIT Litigation Count"]
    .transform(lambda x: (x / x.sum()) * 100)
).round(2)

# Step 5: Merge with global percentages
merged = pd.merge(filtered_df, global_total[["LIT Leave Decision Desc", "Total_Percentage"]], on="LIT Leave Decision Desc")
merged["Difference"] = merged["Percentage"] - merged["Total_Percentage"]

# Step 6: Plot dumbbell chart
fig = go.Figure()
dismissed_case_types = set(merged[merged['LIT Leave Decision Desc'] == 'Dismissed']['LIT Case Type Group Desc'])
for decision in merged['LIT Leave Decision Desc'].unique():
    subset = merged[merged['LIT Leave Decision Desc'] == decision]
    for i, (_, row) in enumerate(subset.iterrows()):
        fig.add_trace(go.Scatter(x=[0, row['Difference']], y=[decision, decision], mode='lines', line=dict(color='gray', width=2), showlegend=False))
        fig.add_trace(go.Scatter(x=[row['Difference']], y=[decision], mode='markers', marker=dict(size=16, color=CASE_TYPE_COLOR_MAP[row['LIT Case Type Group Desc']]), showlegend=(row['LIT Case Type Group Desc'] in dismissed_case_types and decision == 'Dismissed'), name=row['LIT Case Type Group Desc']))
        fig.add_annotation(x=row['Difference'], y=decision, text=f"{row['Difference']:.2f}%", showarrow=False, font=dict(size=14, color='white'), align='center', bgcolor=CASE_TYPE_COLOR_MAP[row['LIT Case Type Group Desc']], borderpad=4, yshift=12 if i % 2 == 0 else -12)

fig.update_layout(xaxis=dict(title="Difference in % (case type - total)", zeroline=True),
                  yaxis=dict(title="Decision", autorange='reversed', gridcolor='white'),
                  height=800, width=1500, plot_bgcolor='white', hovermode="closest",
                  font=dict(family='Arial', size=20),
                  legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))
st.plotly_chart(fig, use_container_width=True)
st.markdown("**Note:** _China, India, and Nigeria_: Outcomes are mostly Dismissed. _Iran_: Most cases are Discontinued, especially since 2020.")


# ===== Section 4 =====
st.header("Dismissed & Discontinued Cases Increasing Over Years")
st.markdown("##### **India** and **Iran** have seen the sharpest rise in **dismissed** and **discontinued** cases since 2021.")

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

fig.update_layout(height=500, width=1200, title_text="Decision Group Trends", showlegend=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown("**Note:** _Allowed_: Remain consistently low across all countries. _Discontinued_: Iran shows a steep increase from 2020, peaking in 2023 with nearly 1,000 cases. _Dismissed_: India and Iran show sharp increases. Nigeria shows a decline since 2021 across all outcome types.")
