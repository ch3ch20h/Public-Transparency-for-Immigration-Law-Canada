import streamlit as st

st.set_page_config(layout="wide")
pages = {
    "Dashboard": [
        st.Page("litigation_dashboard.py", title="Top 4 Countries Litigation Application"),
        st.Page("africa_vs_non_africa.py", title="Region Litigation Application"),
        st.Page("A34_Refused_Data.py", title="A34(1) Inadmissibility Refusal"),
        st.Page("litigation_interactive.py", title="Litigation Applications Dashboard"),
        st.Page("A34_Refused_Data.py", title="A34 Refused Data"),
        st.Page("Africa_vs_non_africa.py", title="Litigation by Continent"),
        st.Page("litigation_dashboard.py", title="Litigation by Country"),
        st.Page("litigation_interactive.py", title="Litigation Interactive"),
    ],

}
pg = st.navigation(pages)
pg.run()
