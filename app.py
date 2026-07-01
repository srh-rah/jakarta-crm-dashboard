import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Jakarta CRM Dashboard",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="metric-container"] {
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
[data-testid="metric-container"] label {
    color: inherit !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: inherit !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
}
.section-header {
    background: #1a1a68;
    color: #dadae7;
    padding: 9px 16px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 700;
    margin: 12px 0;
}
.stMultiSelect span[data-baseweb="tag"] {
    background-color: #1a1a68 !important;
    color: #dadae7 !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}
h2 a, h3 a, h4 a { display: none !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel('crm_jakarta_cleaned.xlsx',
                       parse_dates=['tanggal_masuk', 'tanggal_selesai'])
    df['tahun']      = df['tanggal_masuk'].dt.year.astype(str)
    df['nama_bulan'] = df['tanggal_masuk'].dt.month_name()
    df['bulan']      = df['tanggal_masuk'].dt.month
    return df

df_full = load_data()

BULAN_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

def make_layout(height=420):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

PLOTLY_CONFIG = dict(
    displaylogo=False,
    modeBarButtonsToRemove=[
        'pan2d','select2d','lasso2d','autoScale2d',
        'hoverClosestCartesian','hoverCompareCartesian',
        'toggleSpikelines','sendDataToCloud'
    ],
)

with st.sidebar:
    st.markdown("## Filter Data")
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
    st.caption("Data: satudata.jakarta.go.id · 2019–2020")

df = df_full[
    df_full['tahun'].isin(sel_tahun) &
    df_full['kategori'].isin(sel_kategori) &
    df_full['bulan'].between(sel_bulan[0], sel_bulan[1])
].copy()

st.markdown("""
<div style="background:#1a1a68; padding:20px 28px; border-radius:12px; margin-bottom:20px;">
  <h1 style="color:#dadae7; margin:0; font-size:1.6rem;">Jakarta CRM Complaint Dashboard</h1>
  <p style="color:#dadae7; margin:4px 0 0; font-size:0.88rem; opacity:0.8;">
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
    st.markdown("#### Top 10 Kategori Pengaduan")
    top_kat = df['kategori'].value_counts().head(10).reset_index()
    top_kat.columns = ['kategori', 'jumlah']
    fig1 = px.bar(top_kat.sort_values('jumlah'),
                  x='jumlah', y='kategori', orientation='h',
                  color='jumlah',
                  color_continuous_scale=['#A8C8E8','#1a1a68'],
                  labels={'jumlah':'Jumlah','kategori':''})
    fig1.update_layout(coloraxis_showscale=False, **make_layout())
    st.plotly_chart(fig1, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    st.markdown("#### Tren Pengaduan per Bulan")
    tren = df.groupby(['tahun','nama_bulan']).size().reset_index(name='jumlah')
    tren['nama_bulan'] = pd.Categorical(tren['nama_bulan'],
                                        categories=BULAN_ORDER, ordered=True)
    tren = tren.sort_values(['tahun','nama_bulan'])
    fig2 = px.line(tren, x='nama_bulan', y='jumlah', color='tahun',
                   markers=True,
                   color_discrete_map={'2019':'#4A90D9','2020':'#1a1a68'},
                   labels={'nama_bulan':'','jumlah':'Jumlah','tahun':'Tahun'})
    fig2.update_layout(**make_layout())
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")
st.markdown('<div class="section-header">SKPD Performance</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 10 SKPD dengan Jumlah Pengaduan Tertinggi")
    top_skpd = df['skpd'].value_counts().head(10).reset_index()
    top_skpd.columns = ['skpd', 'jumlah']
    fig3 = px.bar(top_skpd.sort_values('jumlah'),
                  x='jumlah', y='skpd', orientation='h',
                  color='jumlah',
                  color_continuous_scale=['#A8C8E8','#1a1a68'],
                  labels={'jumlah':'Jumlah','skpd':''})
    fig3.update_layout(coloraxis_showscale=False, **make_layout())
    st.plotly_chart(fig3, use_container_width=True, config=PLOTLY_CONFIG)

with col4:
    st.markdown("#### Kategori dengan Waktu Respon Terlama")
    resp_kat = (df[df['response_time'] > 0]
                .groupby('kategori')['response_time']
                .agg(['mean','count']).reset_index())
    resp_kat.columns = ['kategori','avg_response','jumlah']
    resp_kat = resp_kat[resp_kat['jumlah'] >= 10]
    resp_kat['avg_response'] = resp_kat['avg_response'].round(1)
    top_lambat = resp_kat.nlargest(10,'avg_response').sort_values('avg_response')
    fig4 = px.bar(top_lambat, x='avg_response', y='kategori', orientation='h',
                  color='avg_response',
                  color_continuous_scale=['#A8C8E8','#E05252'],
                  labels={'avg_response':'Rata-rata Hari','kategori':''})
    fig4.update_layout(coloraxis_showscale=False, **make_layout())
    st.plotly_chart(fig4, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")
st.markdown('<div class="section-header">Analisis Waktu Respon</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.markdown("#### Kecepatan Penyelesaian Pengaduan")
    bins = pd.cut(df['response_time'],
                  bins=[-1,0,1,7,30,9999],
                  labels=['0 hari','1 hari','2–7 hari','8–30 hari','> 30 hari'])
    resp_bins = bins.value_counts().sort_index().reset_index()
    resp_bins.columns = ['kategori_waktu','jumlah']
    fig5 = px.bar(resp_bins, x='kategori_waktu', y='jumlah',
                  color='kategori_waktu',
                  color_discrete_sequence=['#1a1a68','#2563A8','#4A90D9','#E8B84B','#E05252'],
                  labels={'kategori_waktu':'','jumlah':'Jumlah Pengaduan'},
                  text='jumlah')
    fig5.update_traces(textposition='outside')
    fig5.update_layout(showlegend=False, **make_layout())
    st.plotly_chart(fig5, use_container_width=True, config=PLOTLY_CONFIG)

with col6:
    st.markdown("#### Matriks Pengaduan Bulanan per Kategori")
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
    fig6.update_layout(**make_layout())
    fig6.update_xaxes(tickangle=30)
    st.plotly_chart(fig6, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.8rem;'>"
    "Jakarta CRM Dashboard · Data: "
    "<a href='https://satudata.jakarta.go.id' style='color:#1a1a68;'>satudata.jakarta.go.id</a>"
    " · Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
