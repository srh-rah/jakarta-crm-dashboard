import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Jakarta CRM Dashboard", layout="wide")

THEMES = {
    "Navy (Default)": {
        "primary":    "#1a1a68",
        "text":       "#dadae7",
        "bar_scale":  ["#A8C8E8", "#1a1a68"],
        "line_2019":  "#4A90D9",
        "line_2020":  "#1a1a68",
        "sidebar_bg": "#F0F5FA",
        "metric_val": "#1a1a68",
    },
    "Forest Green": {
        "primary":    "#1a4a2e",
        "text":       "#e0ead5",
        "bar_scale":  ["#a8d5b5", "#1a4a2e"],
        "line_2019":  "#4a9d6f",
        "line_2020":  "#1a4a2e",
        "sidebar_bg": "#f0f5f1",
        "metric_val": "#1a4a2e",
    },
    "Slate Gray": {
        "primary":    "#2d3748",
        "text":       "#e2e8f0",
        "bar_scale":  ["#a0aec0", "#2d3748"],
        "line_2019":  "#718096",
        "line_2020":  "#2d3748",
        "sidebar_bg": "#f7fafc",
        "metric_val": "#2d3748",
    },
    "Maroon": {
        "primary":    "#6b1a1a",
        "text":       "#f0dada",
        "bar_scale":  ["#e8a8a8", "#6b1a1a"],
        "line_2019":  "#c05252",
        "line_2020":  "#6b1a1a",
        "sidebar_bg": "#fdf5f5",
        "metric_val": "#6b1a1a",
    },
}

with st.sidebar:
    st.markdown("## Filter Data")
    st.markdown("---")
    sel_tema = st.selectbox("Tema Warna", list(THEMES.keys()))

T = THEMES[sel_tema]
P = T["primary"]
TX = T["text"]

st.markdown(f"""
<style>
[data-testid="metric-container"] {{
    background: #ffffff;
    border: 1px solid #D0DCE8;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}}
[data-testid="metric-container"] label {{
    color: #5A7A9A !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {P} !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
}}
.section-header {{
    background: {P};
    color: {TX};
    padding: 9px 16px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 700;
    margin: 12px 0;
}}
section[data-testid="stSidebar"] {{ background-color: {T["sidebar_bg"]}; }}
.stMultiSelect span[data-baseweb="tag"] {{
    background-color: {P} !important;
    color: {TX} !important;
}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('crm_jakarta_cleaned.csv',
                     parse_dates=['tanggal_masuk', 'tanggal_selesai'])
    df['tahun']      = df['tanggal_masuk'].dt.year.astype(str)
    df['nama_bulan'] = df['tanggal_masuk'].dt.month_name()
    df['bulan']      = df['tanggal_masuk'].dt.month
    return df

df_full = load_data()

BULAN_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

with st.sidebar:
    st.markdown("---")
    sel_tahun = st.multiselect(
        "Tahun", sorted(df_full['tahun'].unique()),
        default=sorted(df_full['tahun'].unique())
    )
    sel_kategori = st.multiselect(
        "Kategori", sorted(df_full['kategori'].unique()),
        default=sorted(df_full['kategori'].unique())
    )
    sel_bulan = st.slider("Rentang Bulan", 1, 12, (1, 12))
    st.markdown("---")
    st.caption("Data: data.jakarta.go.id · 2019–2020")

df = df_full[
    df_full['tahun'].isin(sel_tahun) &
    df_full['kategori'].isin(sel_kategori) &
    df_full['bulan'].between(sel_bulan[0], sel_bulan[1])
].copy()

st.markdown(f"""
<div style="background:{P}; padding:20px 28px; border-radius:12px; margin-bottom:20px;">
  <h1 style="color:{TX}; margin:0; font-size:1.6rem;">Jakarta CRM Complaint Dashboard</h1>
  <p style="color:{TX}; margin:4px 0 0; font-size:0.88rem; opacity:0.8;">
    Analisis pengaduan warga · Diskominfotik DKI Jakarta · 2019–2020
  </p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Total Pengaduan",        f"{len(df):,}")
c2.metric("Rata-rata Waktu Respon", f"{df['response_time'].mean():.1f} hari")
c3.metric("Jumlah SKPD",           f"{df['skpd'].nunique()}")

st.markdown("---")
st.markdown('<div class="section-header">Complaint Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Kategori Pengaduan")
    top_kat = df['kategori'].value_counts().head(10).reset_index()
    top_kat.columns = ['kategori', 'jumlah']
    fig = px.bar(top_kat.sort_values('jumlah'),
                 x='jumlah', y='kategori', orientation='h',
                 color='jumlah', color_continuous_scale=T["bar_scale"],
                 labels={'jumlah':'Jumlah','kategori':''})
    fig.update_layout(coloraxis_showscale=False, height=420,
                      margin=dict(l=0,r=0,t=10,b=0),
                      paper_bgcolor='white', plot_bgcolor='#F7F9FC')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Tren Pengaduan per Bulan")
    tren = df.groupby(['tahun','nama_bulan']).size().reset_index(name='jumlah')
    tren['nama_bulan'] = pd.Categorical(tren['nama_bulan'],
                                        categories=BULAN_ORDER, ordered=True)
    tren = tren.sort_values(['tahun','nama_bulan'])
    fig2 = px.line(tren, x='nama_bulan', y='jumlah', color='tahun', markers=True,
                   color_discrete_map={'2019': T["line_2019"], '2020': T["line_2020"]},
                   labels={'nama_bulan':'','jumlah':'Jumlah','tahun':'Tahun'})
    fig2.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor='white', plot_bgcolor='#F7F9FC')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown('<div class="section-header">SKPD Performance</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 SKPD by Volume")
    top_skpd = df['skpd'].value_counts().head(10).reset_index()
    top_skpd.columns = ['skpd', 'jumlah']
    fig3 = px.bar(top_skpd.sort_values('jumlah'),
                  x='jumlah', y='skpd', orientation='h',
                  color='jumlah', color_continuous_scale=T["bar_scale"],
                  labels={'jumlah':'Jumlah','skpd':''})
    fig3.update_layout(coloraxis_showscale=False, height=420,
                       margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor='white', plot_bgcolor='#F7F9FC')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Kategori Waktu Respon Terlama")
    resp_kat = (df[df['response_time'] > 0]
                .groupby('kategori')['response_time']
                .agg(['mean','count']).reset_index())
    resp_kat.columns = ['kategori','avg_response','jumlah']
    resp_kat = resp_kat[resp_kat['jumlah'] >= 10]
    resp_kat['avg_response'] = resp_kat['avg_response'].round(1)
    top_lambat = resp_kat.nlargest(10,'avg_response').sort_values('avg_response')
    fig4 = px.bar(top_lambat, x='avg_response', y='kategori', orientation='h',
                  color='avg_response',
                  color_continuous_scale=[T["bar_scale"][0], '#E05252'],
                  labels={'avg_response':'Rata-rata Hari','kategori':''})
    fig4.update_layout(coloraxis_showscale=False, height=420,
                       margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor='white', plot_bgcolor='#F7F9FC')
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown('<div class="section-header">Analisis Waktu Respon</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.subheader("Kecepatan Penyelesaian Pengaduan")
    bins = pd.cut(df['response_time'],
                  bins=[-1,0,1,7,30,9999],
                  labels=['0 hari','1 hari','2–7 hari','8–30 hari','> 30 hari'])
    resp_bins = bins.value_counts().sort_index().reset_index()
    resp_bins.columns = ['kategori_waktu','jumlah']
    fig5 = px.bar(resp_bins, x='kategori_waktu', y='jumlah',
                  color='kategori_waktu',
                  color_discrete_sequence=[P, T["line_2019"], T["line_2020"],
                                           '#E8B84B', '#E05252'],
                  labels={'kategori_waktu':'','jumlah':'Jumlah Pengaduan'},
                  text='jumlah')
    fig5.update_traces(textposition='outside')
    fig5.update_layout(showlegend=False, height=420,
                       margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor='white', plot_bgcolor='#F7F9FC')
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("Heatmap Pengaduan: Bulan x Kategori")
    top8 = df['kategori'].value_counts().head(8).index.tolist()
    df_hm = df[df['kategori'].isin(top8)].copy()
    pivot = (df_hm.groupby(['nama_bulan','kategori'])
                  .size().reset_index(name='jumlah')
                  .pivot(index='nama_bulan', columns='kategori', values='jumlah')
                  .fillna(0)
                  .reindex(BULAN_ORDER))
    fig6 = px.imshow(pivot, color_continuous_scale='Blues',
                     labels=dict(x='Kategori', y='Bulan', color='Jumlah'),
                     aspect='auto', text_auto=True)
    fig6.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor='white')
    fig6.update_xaxes(tickangle=30)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.markdown(
    f"<div style='text-align:center; color:#8A9BB0; font-size:0.8rem;'>"
    f"Jakarta CRM Dashboard · Data: "
    f"<a href='https://data.jakarta.go.id' style='color:{P};'>data.jakarta.go.id</a>"
    f" · Built with Streamlit"
    f"</div>",
    unsafe_allow_html=True
)
