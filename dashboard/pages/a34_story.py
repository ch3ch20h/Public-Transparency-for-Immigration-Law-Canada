import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title(" Grounds for Refusal of Immigration Applications")

@st.cache_data
def load_data():
    """Load and cache the CSV data"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "a34_1_refused_cleaned.csv")
    try:
        df = pd.read_csv(data_path)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at: {data_path}")
        return pd.DataFrame()

# Load data
ref = load_data()

# --- Top 10 Countries by Total Refusals ---

st.header("Top 10 Countries by Total Refusals")
st.markdown("""

**Ukraine** (176) and **Syria** (101) lead the list

⚠️ *Note: Due to the small refusal counts in general, strong conclusions should be avoided.*
""")
country_counts = ref.groupby("country")["count"].sum().nlargest(10).reset_index()
fig1 = px.bar(
    country_counts,
    x="country",
    y="count",
    text_auto=True
)
st.plotly_chart(fig1, use_container_width=True)

# --- Heatmap: Yearly Trends for Top 5 Countries ---
st.header("Yearly Refusal Trends (Top 5 Countries)")
st.markdown("""
**Observations**:
- **Ukraine** had a large spike in **2024** with **131** refusals.
- **Syria** led in **2019** and **2022**.
- **Iran** has steady refusals across multiple years.
""")
top_countries = country_counts.head(5)['country'].tolist()
df_top = ref[ref['country'].isin(top_countries)]
heatmap_data = df_top.pivot_table(index='country', columns='year', values='count', aggfunc='sum', fill_value=0)
fig2 = px.imshow(
    heatmap_data,
    text_auto=True,
    color_continuous_scale='Blues',
    labels=dict(x="Year", y="Country", color="Refusals")
)
st.plotly_chart(fig2, use_container_width=True)


# --- Treemap: Grounds for Refusal ---
st.header("Refusal Breakdown by Inadmissibility Grounds")
st.markdown("""
**Breakdown of Grounds**:
- **Ukraine** and **Bangladesh**: Mostly A34(1)(f) (around 80–90%).
- **Iran** and **Syria**: Refusals spread across multiple clauses (f, d, b, c).
- **China**: Primarily A34(1)(f) with some under (a) and (c).
These patterns may suggest different risk categorizations per country, but more data would be needed to confirm.
""")
fig3 = px.treemap(
    df_top,
    path=["country", "inadmissibility_grounds"],
    values="count",
    hover_data=["count"]
)
fig3.update_traces(textinfo="label+value")
fig3.update_layout(
    width=1400,
    height=800
)
st.plotly_chart(fig3, use_container_width=True)


st.info("""
**⚠️ Disclaimer:** Refusal numbers under A34(1) are quite low overall. While some patterns emerge, these are not sufficient for conclusive inferences. More contextual data—like total applications or approval rates—is essential for robust analysis.
""")