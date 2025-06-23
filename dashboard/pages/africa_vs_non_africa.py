import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import qualitative
import os

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
      .large-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
      }
      .subtitle {
        font-size: 1.25rem;
        color: #CCCCCC;
        margin-bottom: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="large-title">Litigation Cases by Continent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'This dashboard is aimed at uncovering patterns of refusal rates across '
    'continents to evaluate potential Anti-African/Black racism in litigation outcomes.'
    '</div>',
    unsafe_allow_html=True
)

path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")

@st.cache_data
def load_data():
    return pd.read_excel(path,
                         skiprows=5, skipfooter=7)

df = load_data()
df['LIT Leave Decision Desc'] = (
    df['LIT Leave Decision Desc']
      .replace(r'^Discontinued.*', 'Discontinued', regex=True)
      .replace(r'^Dismissed.*',    'Dismissed',    regex=True)
      .replace(r'^Allowed.*',      'Allowed',      regex=True)
)

continent_map = {
    'India': 'Asia', 'Fiji': 'Oceania', 'Russia': 'Asia', 'Republic of Indonesia': 'Asia',
    'Georgia': 'Asia', 'Nigeria': 'Africa', 'United States of America': 'North America',
    'Lebanon': 'Asia', 'Croatia': 'Europe', 'Egypt': 'Africa', "People's Republic of China": 'Asia',
    'Albania': 'Europe', 'Colombia': 'South America', 'Somalia, Democratic Republic of': 'Africa',
    'Iraq': 'Asia', 'Italy': 'Europe', 'Rwanda': 'Africa', 
    'United Kingdom and Overseas Territories': 'Europe', 'Bulgaria': 'Europe', 
    'Ukraine': 'Europe', 'Kenya': 'Africa', 'Stateless': 'Unspecified', 'Greece': 'Europe',
    'Syria': 'Asia', 'Jamaica': 'North America', 'Hungary': 'Europe', 'Turkey': 'Asia',
    'Pakistan': 'Asia', 'Socialist Republic of Vietnam': 'Asia', 'Kazakhstan': 'Asia',
    'Mexico': 'North America', 'Federal Republic of Cameroon': 'Africa',
    'Congo, Democratic Republic of the': 'Africa', 'Namibia': 'Africa', 'Iran': 'Asia',
    'Cambodia': 'Asia', "Korea, People's Democratic Republic of": 'Asia',
    'Trinidad and Tobago, Republic of': 'North America', 'Peru': 'South America',
    'Palestinian Authority (Gaza/West Bank)': 'Asia', 'St. Kitts-Nevis': 'North America',
    'Republic of Ivory Coast': 'Africa', 'Ghana': 'Africa', 'Republic of South Africa': 'Africa',
    'El Salvador': 'North America', 'Bangladesh': 'Asia', 'Kosovo, Republic of': 'Europe',
    'Guinea, Republic of': 'Africa', 'Sri Lanka': 'Asia', 'Latvia': 'Europe',
    'Hong Kong SAR': 'Asia', 'Jordan': 'Asia', 'Slovak Republic': 'Europe', 'Zimbabwe': 'Africa',
    'St. Lucia': 'North America', 'Honduras': 'North America', 'United Republic of Tanzania': 'Africa',
    'Nepal': 'Asia', 'St. Vincent and the Grenadines': 'North America', 'Philippines': 'Asia',
    'Sierra Leone': 'Africa', 'Tunisia': 'Africa', 'Federal Republic of Germany': 'Europe',
    'Togo, Republic of': 'Africa', 'Spain': 'Europe', 'Malawi': 'Africa', 'France': 'Europe',
    'Afghanistan': 'Asia', 'Guyana': 'South America', 'Haiti': 'North America', 'Belgium': 'Europe',
    'Kuwait': 'Asia', 'Eritrea': 'Africa', 'Algeria': 'Africa', 'Uganda': 'Africa',
    'Democratic Republic of Sudan': 'Africa', 'Gabon Republic': 'Africa',
    'Korea, Republic of': 'Asia', 'Chad, Republic of': 'Africa', 'Saudi Arabia': 'Asia',
    'Brazil': 'South America', 'Mauritius': 'Africa', 'Israel': 'Asia', 'Azerbaijan': 'Asia',
    'Argentina': 'South America', 'Portugal': 'Europe', 'Dominican Republic': 'North America',
    'Libya': 'Africa', 'Senegal': 'Africa', 'Romania': 'Europe', 'Venezuela': 'South America',
    'Poland': 'Europe', 'Belarus': 'Europe', 'Panama, Republic of': 'North America',
    'Gambia': 'Africa', 'Norway': 'Europe', 'Ethiopia': 'Africa', 'Swaziland': 'Africa',
    'Costa Rica': 'North America', 'Barbados': 'North America', 'Malaysia': 'Asia',
    'The Netherlands': 'Europe', 'Liberia': 'Africa', 'Taiwan': 'Asia', 'Switzerland': 'Europe',
    'Mozambique': 'Africa', 'Nicaragua': 'North America', 'Republic of Ireland': 'Europe',
    'Burkina-Faso': 'Africa', 'Madagascar': 'Africa', 'Ecuador': 'South America',
    'Morocco': 'Africa', 'Peoples Republic of Benin': 'Africa', 'Burundi': 'Africa',
    'Chile': 'South America', 'Belize': 'North America', 'Republic of Djibouti': 'Africa',
    'Mali, Republic of': 'Africa', 'Uzbekistan': 'Asia', 'Montenegro, Republic of': 'Europe',
    'Mauritania': 'Africa', 'Angola': 'Africa', 'Armenia': 'Asia', 'Moldova': 'Europe',
    'Yemen, Republic of': 'Asia', 'Bahama Islands, The': 'North America', 'Grenada': 'North America',
    "Congo, People's Republic of the": 'Africa', 'Sweden': 'Europe', 'Czech Republic': 'Europe',
    'Guinea-Bissau': 'Africa', 'Kyrgyzstan': 'Asia', 'Antigua and Barbuda': 'North America',
    'Equatorial Guinea': 'Africa', 'Japan': 'Asia', 'Cuba': 'North America', 'Lesotho': 'Africa',
    'Bosnia-Hercegovina': 'Europe', 'Serbia, Republic of': 'Europe', 'Guatemala': 'North America',
    'Austria': 'Europe', 'Vanuatu': 'Oceania', 'Turkmenistan': 'Asia', 
    'Serbia and Montenegro': 'Europe', 'Lithuania': 'Europe',
    "Mongolia, People's Republic of": 'Asia', 'Republic of the Niger': 'Africa', 'Thailand': 'Asia',
    'Botswana, Republic of': 'Africa', 'New Zealand': 'Oceania', 'Myanmar (Burma)': 'Asia',
    'Unspecified': 'Unspecified', 'Bahrain': 'Asia', 'Macedonia': 'Europe', 'Singapore': 'Asia',
    'United Arab Emirates': 'Asia', 'Surinam': 'South America', 'Bolivia': 'South America',
    'Uruguay': 'South America', 'Australia': 'Oceania', 'Comoros': 'Africa', 'Paraguay': 'South America',
    'Zambia': 'Africa', 'Tadjikistan': 'Asia', 'Cyprus': 'Europe', 'Qatar': 'Asia',
    'Dominica': 'North America', 'Central African Republic': 'Africa', 'Denmark': 'Europe',
    'Macao SAR': 'Asia', 'South Sudan, Republic Of': 'Africa', 'Estonia': 'Europe',
    'Bhutan': 'Asia', 'Slovenia': 'Europe', 'Oman': 'Asia', 'Luxembourg': 'Europe',
    'Solomons, The': 'Oceania', 'Laos': 'Asia', 'Finland': 'Europe', 'Iceland': 'Europe'
}

caribbean_countries = {
    'Antigua and Barbuda': 'Caribbean',
    'Bahamas': 'Caribbean',
    'Barbados': 'Caribbean',
    'Cuba': 'Caribbean',
    'Dominica': 'Caribbean',
    'Dominican Republic': 'Caribbean',
    'Grenada': 'Caribbean',
    'Haiti': 'Caribbean',
    'Jamaica': 'Caribbean',
    'Saint Kitts and Nevis': 'Caribbean',
    'Saint Lucia': 'Caribbean',
    'Saint Vincent and the Grenadines': 'Caribbean',
    'Trinidad and Tobago': 'Caribbean',
    'Puerto Rico': 'Caribbean',
    'Saint Martin': 'Caribbean',
    'Montserrat': 'Caribbean',
    'Anguilla': 'Caribbean',
    'British Virgin Islands': 'Caribbean',
    'US Virgin Islands': 'Caribbean',
    'Cayman Islands': 'Caribbean',
    'Aruba': 'Caribbean',
    'Saint Barthelemy': 'Caribbean',
    'Saint Pierre and Miquelon': 'Caribbean',
    'Guadeloupe': 'Caribbean',
    'Martinique': 'Caribbean'
}
continent_map.update(caribbean_countries)
df['continent'] = df["Country of Citizenship"].map(continent_map)

st.header("1.Total Litigation Cases vs Dismissed Rate by Continent")
st.markdown("""  
- Africa handles the second-highest volume (~13 400 cases) but its refusal rate (56.5 %) is well above the global average.
- Caribbean jurisdictions, despite a moderate caseload (~2 560), see the highest refusal rate (67.7 %).
- South America and Europe both have mid-range volumes but lower refusal rates (~47.5 – 49.9 %), highlighting that African and Caribbean cases are treated more punitively.
""")
total = (
    df
    .groupby('continent', as_index=False)['LIT Litigation Count']
    .sum()
    .rename(columns={'LIT Litigation Count':'total_cases'})
)
dismissed = (
    df[df['LIT Leave Decision Desc']=='Dismissed']
    .groupby('continent', as_index=False)['LIT Litigation Count']
    .sum()
    .rename(columns={'LIT Litigation Count':'dismissed_cases'})
)
cont_df = total.merge(dismissed, on='continent', how='left').fillna(0)
cont_df['refusal_rate'] = cont_df['dismissed_cases'] / cont_df['total_cases'] * 100
cont_df = cont_df.sort_values('total_cases', ascending=False).reset_index(drop=True)

palette   = qualitative.Plotly
color_map = {c: palette[i % len(palette)] for i, c in enumerate(cont_df['continent'])}
bar_colors = cont_df['continent'].map(color_map)

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=cont_df['continent'],
        y=cont_df['total_cases'],
        name='Decisioned Cases',
        marker_color=bar_colors,
        text=cont_df['total_cases'],
        textposition='inside'
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=cont_df['continent'],
        y=cont_df['refusal_rate'],
        mode='lines+markers+text',
        name='Refusal Rate (%)',
        text=cont_df['refusal_rate'].round(1).astype(str) + '%',
        textposition='top center',
        line=dict(color='white')
    ),
    secondary_y=True
)

fig.update_layout(
    xaxis_title="Continent",
    bargap=0.2,
    legend=dict(y=0.5, traceorder='reversed')
)
fig.update_yaxes(title_text="Decisioned Cases", secondary_y=False)
fig.update_yaxes(title_text="Refusal Rate (%)", secondary_y=True, ticksuffix='%')
fig.update_xaxes(categoryorder='array', categoryarray=cont_df['continent'])
fig.update_yaxes(showgrid=False, secondary_y=False)
fig.update_yaxes(showgrid=False, secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

st.header("2. Overall Dismissed Rate Difference vs Global")
st.markdown("""
- Caribbean refusal rates exceed the world average by +16.3 pp, the largest gap of any region.
- North America is +8.6 pp and Africa +5.1 pp above global, confirming a systematic elevation.
- By contrast, Asia, Europe and South America fall below global (–5.6 pp to –1.5 pp), underscoring the specific disadvantage faced by Black-majority regions.
""")

tot = (
    df
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='cont_total')
)
dis = (
    df[df['LIT Leave Decision Desc'] == 'Dismissed']
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='cont_dismissed')
)

cont_all = tot.merge(dis, on='continent', how='left').fillna(0)
cont_all['cont_rate'] = cont_all['cont_dismissed'] / cont_all['cont_total'] * 100
global_rate = cont_all['cont_dismissed'].sum() / cont_all['cont_total'].sum() * 100

cont_all['delta_pct'] = cont_all['cont_rate'] - global_rate
cont_all_sorted = cont_all.sort_values('delta_pct', ascending=False)

fig = px.bar(
    cont_all_sorted,
    x='continent',
    y='delta_pct',
    text=cont_all_sorted['delta_pct'].round(1).astype(str) + '%',
    labels={'delta_pct':'Δ Refusal Rate (%)','continent':'Continent'},
    category_orders={'continent': cont_all_sorted['continent'].tolist()}
)

fig.update_traces(textposition='inside')
fig.update_layout(
    yaxis_ticksuffix='%',
    yaxis_title='Δ Refusal Rate (%)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig, use_container_width=True)

st.header("3. Leave Decision % Δ vs Global by Continent")
st.markdown("""
- Dismissed decisions are elevated by Caribbean +16.3 pp, North America +8.6 pp, Africa +5.1 pp versus global.
- Discontinued cases are correspondingly lower (Caribbean –13.4 pp, North America –12.8 pp, Africa –6.0 pp), indicating Black applicants are far more likely to be outright refused rather than see cases dropped.
- Allowed rates are only slightly above global in North America (+4.2 pp) and Africa (+0.9 pp) and actually lower in the Caribbean (–2.9 pp).
""")
counts = (
    df
    .groupby(['continent','LIT Leave Decision Desc'])['LIT Litigation Count']
    .sum()
    .reset_index(name='count')
)

tot = (
    df
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='total')
)

cont = counts.merge(tot, on='continent')
cont['pct_cont'] = cont['count'] / cont['total'] * 100

glob = (
    df
    .groupby('LIT Leave Decision Desc')['LIT Litigation Count']
    .sum()
    .reset_index(name='global_count')
)
glob['pct_global'] = glob['global_count'] / glob['global_count'].sum() * 100

cont = cont.merge(
    glob[['LIT Leave Decision Desc','pct_global']],
    on='LIT Leave Decision Desc'
)
cont['diff'] = cont['pct_cont'] - cont['pct_global']

sel = cont[cont['continent'].isin(['Africa','North America','Caribbean'])]

sel = sel[~sel['LIT Leave Decision Desc'].isin([
    'Not Started at Leave',
    'No Leave Required',
    'Leave Exception'
])]

fig = px.bar(
    sel,
    x='diff',
    y='LIT Leave Decision Desc',
    color='continent',
    barmode='group',
    text=sel['diff'].round(1).astype(str) + '%',
    labels={
        'diff':'Δ % (continent vs global)',
        'LIT Leave Decision Desc':'Leave Decision',
        'continent':'Continent'
    },
    category_orders={
        'LIT Leave Decision Desc': ['Allowed','Discontinued','Dismissed']
    }
)
fig.update_traces(textposition='inside')
fig.update_layout(
    xaxis=dict(ticksuffix='%')
)
st.plotly_chart(fig, use_container_width=True)

st.header("4. Annual Case-Share & Refusal Rates for Select Continents")
st.markdown("""
- Across every year, Africa, North America and the Caribbean exhibit refusal rates well above the global average (dashed black line), indicating persistent regional disparities in outcomes.
- The Caribbean’s refusal rate peaks highest rising from 73.9% in 2018 to 76.3% in 2019,before steadily declining to 43.2% by 2022, then rebounding to 48.7% in 2023.
- Africa’s refusal rate steadily falls from 67.0% in 2018 to 50.1% in 2021, before upticking to 52.4% in 2023, even as its share of total cases fluctuates around one-third of all decisions.
""")
year_col  = 'LIT Leave Decision Date - Year'
cont_col  = 'continent'
dec_col   = 'LIT Leave Decision Desc'
count_col = 'LIT Litigation Count'
keep_conts = ['Africa', 'North America', 'Caribbean']

glob_tot = (
    df
    .groupby(year_col)[count_col]
    .sum()
    .reset_index(name='global_total')
)
glob_dis = (
    df[df[dec_col]=='Dismissed']
    .groupby(year_col)[count_col]
    .sum()
    .reset_index(name='global_dismissed')
)
glob = glob_tot.merge(glob_dis, on=year_col)
glob['global_rate'] = glob['global_dismissed'] / glob['global_total'] * 100

cont_tot = (
    df
    .groupby([year_col, cont_col])[count_col]
    .sum()
    .reset_index(name='cont_total')
)
cont_dis = (
    df[df[dec_col]=='Dismissed']
    .groupby([year_col, cont_col])[count_col]
    .sum()
    .reset_index(name='cont_dismissed')
)
cont = cont_tot.merge(cont_dis, on=[year_col, cont_col], how='left').fillna(0)
cont['cont_rate'] = cont['cont_dismissed'] / cont['cont_total'] * 100

cmp = (
    cont
    .merge(glob[[year_col, 'global_rate', 'global_total']], on=year_col)
    .query("continent in @keep_conts")
    .sort_values([cont_col, year_col])
)

cmp['share_pct']     = cmp['cont_total']   / cmp['global_total'] * 100
cmp['remainder_pct'] = 100 - cmp['share_pct']

n    = len(keep_conts)
cols = 3
rows = (n + cols - 1) // cols

fig = make_subplots(
    rows=rows, cols=cols,
    subplot_titles=keep_conts,
    specs=[[{"secondary_y": True}]*cols for _ in range(rows)],
    vertical_spacing=0.15,
    horizontal_spacing=0.05
)

for i, cont_name in enumerate(keep_conts):
    sub = cmp[cmp[cont_col] == cont_name]
    sub = sub.sort_values(year_col)
    row, col = i//cols + 1, i%cols + 1

    fig.add_trace(
        go.Bar(
            x=sub[year_col],
            y=sub['share_pct'],
            name=f'{cont_name} share',
            marker_color='steelblue',
            text=sub['cont_total'],
            texttemplate='%{text}',
            textposition='inside',
            showlegend=(i==0),
            legendgroup='share'
        ),
        row=row, col=col, secondary_y=False
    )
    fig.add_trace(
        go.Bar(
            x=sub[year_col],
            y=sub['remainder_pct'],
            name='Other share',
            marker_color='lightgray',
            showlegend=(i==0),
            legendgroup='share'
        ),
        row=row, col=col, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=sub[year_col],
            y=sub['cont_rate'],
            name=f'{cont_name} refusal',
            mode='lines+markers+text',
            text=sub['cont_rate'].round(1).astype(str) + '%',
            textposition='top center',
            marker=dict(color='firebrick'),
            showlegend=(i==0),
            legendgroup='cont_rate'
        ),
        row=row, col=col, secondary_y=True
    )

    fig.add_trace(
        go.Scatter(
            x=sub[year_col],
            y=sub['global_rate'],
            name='Global refusal',
            mode='lines+markers+text',
            text=sub['global_rate'].round(1).astype(str) + '%',
            textposition='bottom center',
            line=dict(color='black', dash='dash'),
            showlegend=(i==0),
            legendgroup='glob_rate'
        ),
        row=row, col=col, secondary_y=True
    )

    fig.update_xaxes(title_text='Year', row=row, col=col)
    fig.update_yaxes(
        secondary_y=False,
        row=row, col=col,
        ticksuffix='%',
        range=[0, 100]
    )
    fig.update_yaxes(
        title_text='Refusal rate (%)',
        secondary_y=True,
        row=row, col=col,
        ticksuffix='%',
        range=[0, 100]
    )

fig.update_xaxes(tickangle=-45)
fig.update_layout(
    barmode='stack',
    bargap=0.1,
    height=400*rows,
    width=1200,
    margin=dict(t=100, b=80)
)
fig.update_yaxes(range=[0,100], ticksuffix='%', secondary_y=False)
fig.update_yaxes(autorange=True, secondary_y=True, showticklabels=False)
fig.update_yaxes(title_text='Refusal rate (%)', secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

st.header("5. Top 5 Case Types Over Years by Continent")
st.markdown("""
- AD Decisions dominate all three regions (≈50 – 70 % of cases), showing “refugee appeal” is the principal pathway.
- Africa and North America have more variety (e.g. HC decisions, visa-officer refusals), whereas the Caribbean relies almost entirely on RAD.
- RAD share peaked during 2020–2021, reflecting pandemic-era backlogs and expedited dismissals.
""")
agg = df.groupby(
    ['continent','LIT Case Type Group Desc','LIT Leave Decision Date - Year'],
    as_index=False
)['LIT Litigation Count'].sum()

top5 = (
    agg.groupby(['continent','LIT Case Type Group Desc'])['LIT Litigation Count']
    .sum()
    .reset_index()
    .sort_values(['continent','LIT Litigation Count'], ascending=[True,False])
    .groupby('continent').head(5)
)

agg_f = agg.merge(
    top5[['continent','LIT Case Type Group Desc']],
    on=['continent','LIT Case Type Group Desc']
)

selected = ['Africa','North America','Caribbean']
palette = px.colors.qualitative.Plotly
case_types = sorted(agg_f[agg_f['continent'].isin(selected)]['LIT Case Type Group Desc'].unique())
color_map = {ct: palette[i % len(palette)] for i,ct in enumerate(case_types)}

fig = make_subplots(
    rows=1, cols=3,
    shared_yaxes=True,
    subplot_titles=selected
)

for i, cont in enumerate(selected):
    sub = agg_f[agg_f['continent']==cont]
    pivot = sub.pivot_table(
        index='LIT Leave Decision Date - Year',
        columns='LIT Case Type Group Desc',
        values='LIT Litigation Count',
        fill_value=0
    )
    years = pivot.index.tolist()
    for ct in case_types:
        if ct not in pivot.columns:
            continue
        fig.add_trace(
            go.Bar(
                y=years,
                x=pivot[ct],
                orientation='h',
                name=ct,
                legendgroup=ct,
                showlegend=(i==0),
                marker_color=color_map[ct],
                text=pivot[ct],
                textposition='inside'
            ),
            row=1, col=i+1
        )
    fig.update_xaxes(title_text='Litigation Count', row=1, col=i+1)
    fig.update_yaxes(title_text='Year' if i==0 else '', row=1, col=i+1)

fig.update_layout(
    barmode='stack',
    height=600, width=1200
)
st.plotly_chart(fig, use_container_width=True)

st.header("6. Top 10 Countries by Case Volume")
st.markdown("""
- In Africa, Nigeria alone accounts for ~73 % of the region’s cases. The next largest,DR Congo is only ~4 %.
- In North America, Mexico (50.2 %) and the United States (22.6 %) together account for over 70 % of the region’s cases,
""")
for cont in ['Africa', 'North America']:
    dfc = df[df['continent'] == cont]
    pc = (
        dfc
        .groupby('Country of Citizenship', as_index=False)['LIT Litigation Count']
        .sum()
        .sort_values('LIT Litigation Count', ascending=False)
        .head(10)
    )
    fig = px.pie(
        pc,
        names='Country of Citizenship',
        values='LIT Litigation Count',
        title=f'{cont}: Top 10 Countries by Case Volume',
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)



