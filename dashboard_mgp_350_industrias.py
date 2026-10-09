import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import io

# Page Configuration
st.set_page_config(
    page_title="MGP | Dashboard de Inteligência B2B - 350 Indústrias SP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MGP Branding
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Banner */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0284C7 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #94A3B8;
        font-size: 14px;
        margin-top: 4px;
        margin-bottom: 0;
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 20px;
        border-left: 5px solid #0284C7;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        font-weight: 600;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 11px;
        color: #10B981;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# City Coordinates Mapping
CITY_COORDS = {
    'São Paulo': (-23.5505, -46.6333),
    'Cotia': (-23.6039, -46.9192),
    'São Bernardo do Campo': (-23.6939, -46.5650),
    'Guarulhos': (-23.4542, -46.5333),
    'Barueri': (-23.5111, -46.8761),
    'Osasco': (-23.5325, -46.7917),
    'Suzano': (-23.5425, -46.3108),
    'Santos': (-23.9608, -46.3339),
    'Ribeirão Pires': (-23.7142, -46.4136),
    'Arujá': (-23.3964, -46.3203),
    'Mauá': (-23.6678, -46.4614),
    'Jandira': (-23.5275, -46.9025),
    'Itapevi': (-23.5489, -46.9342),
    'Mogi das Cruzes': (-23.5206, -46.1853),
    'Diadema': (-23.6861, -46.6228),
    'Itapecerica da Serra': (-23.7172, -46.8494),
    'Ferraz de Vasconcelos': (-23.5411, -46.3689),
    'Elias Fausto': (-23.0411, -47.3739),
    'Campinas': (-22.9099, -47.0626),
    'Pirassununga': (-21.9961, -47.4258),
    'Santa Cruz do Rio Pardo': (-22.8989, -49.6308),
    'Anápolis': (-16.3286, -48.9534),
    'Curitiba': (-25.4284, -49.2733),
    'Canoas': (-29.9178, -51.1836),
    'Nova Lima': (-19.9858, -43.8469),
    'Itaquiraí': (-23.4758, -54.1839),
    'Aracaju': (-10.9472, -37.0731),
    'Eldorado do Sul': (-30.0844, -51.3325),
    'São Vicente': (-23.9631, -46.3919),
    'Guarujá': (-23.9931, -46.2564),
    'Governador Valadares': (-18.8511, -41.9494),
    'Santana de Parnaíba': (-23.4439, -46.9178),
    'Uberlândia': (-18.9186, -48.2772),
    'Itaquaquecetuba': (-23.4861, -46.3483),
    'Taboão da Serra': (-23.6261, -46.7917),
    'São José dos Pinhais': (-25.5347, -49.2064),
    'Magé': (-22.6528, -43.0408)
}

@st.cache_data
def load_data():
    file_path = "industrias_alimentos_sp_350_v7.xlsx"
    if not os.path.exists(file_path):
        file_path = "/workspace/artifacts/industrias_alimentos_sp_350_v7.xlsx"
    
    df = pd.read_excel(file_path)
    
    # Assign Tiers based on criteria
    def assign_tier(row):
        cap = row['Capital Social (R$)']
        seg = row['Qtd Seguidores']
        nat = str(row['Natureza Jurídica'])
        
        if seg >= 24000 or cap >= 25000000 or "S.A." in nat:
            return "Tier 1 (Enterprise)"
        elif cap >= 3000000 or seg >= 5000:
            return "Tier 2 (Mid-Market)"
        else:
            return "Tier 3 (PMEs / Regionais)"
            
    df['Tier MGP'] = df.apply(assign_tier, axis=1)
    
    # Coordinates mapping with light jittering for map visualization
    np.random.seed(42)
    lats, lons = [], []
    for idx, row in df.iterrows():
        city = row['Cidade']
        base_lat, base_lon = CITY_COORDS.get(city, (-23.5505, -46.6333))
        # Add tiny jitter so overlapping points in São Paulo are visible
        jitter_lat = base_lat + np.random.uniform(-0.012, 0.012)
        jitter_lon = base_lon + np.random.uniform(-0.012, 0.012)
        lats.append(jitter_lat)
        lons.append(jitter_lon)
        
    df['lat'] = lats
    df['lon'] = lons
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Erro ao carregar a base de dados: {e}")
    st.stop()

# --- HEADER BANNER ---
st.markdown("""
<div class="main-header">
    <h1>MGP — Métodos, Gestão e Projetos</h1>
    <p>Dashboard Interativo B2B · Inteligência de Mercado & Prospecção das 350 Indústrias de Alimentos (SP)</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filtros de Inteligência")

# Search Bar
search_query = st.sidebar.text_input("🔎 Buscar Empresa / CNPJ / Marca", "").strip().lower()

# Tier Filter
tiers_available = sorted(df_raw['Tier MGP'].unique())
selected_tiers = st.sidebar.multiselect("🎯 Tier de Priorização", options=tiers_available, default=tiers_available)

# Region/Polo Filter
polos_available = sorted(df_raw['Polo Industrial / Região'].unique())
selected_polos = st.sidebar.multiselect("📍 Polo Regional / Cluster", options=polos_available, default=polos_available)

# Segment / CNAE Filter
cnaes_available = sorted(df_raw['CNAE / Atividade Principal'].astype(str).unique())
selected_cnaes = st.sidebar.multiselect("🏭 Segmento Industrial (CNAE)", options=cnaes_available, default=cnaes_available)

# Capital Social Range Filter
min_cap = float(df_raw['Capital Social (R$)'].min())
max_cap = float(df_raw['Capital Social (R$)'].max())
selected_cap_range = st.sidebar.slider(
    "💰 Capital Social (R$)",
    min_value=0.0,
    max_value=max_cap,
    value=(0.0, max_cap),
    format="R$ %.0f"
)

# Apply Filters
df_filtered = df_raw.copy()

if selected_tiers:
    df_filtered = df_filtered[df_filtered['Tier MGP'].isin(selected_tiers)]
if selected_polos:
    df_filtered = df_filtered[df_filtered['Polo Industrial / Região'].isin(selected_polos)]
if selected_cnaes:
    df_filtered = df_filtered[df_filtered['CNAE / Atividade Principal'].astype(str).isin(selected_cnaes)]

df_filtered = df_filtered[
    (df_filtered['Capital Social (R$)'] >= selected_cap_range[0]) & 
    (df_filtered['Capital Social (R$)'] <= selected_cap_range[1])
]

if search_query:
    df_filtered = df_filtered[
        df_filtered['Nome da Empresa'].astype(str).str.lower().str.contains(search_query) |
        df_filtered['Razão Social Oficial'].astype(str).str.lower().str.contains(search_query) |
        df_filtered['CNPJ'].astype(str).str.contains(search_query) |
        df_filtered['Cidade'].astype(str).str.lower().str.contains(search_query)
    ]

# --- TOP KPI METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)

total_emp = len(df_filtered)
total_cap = df_filtered['Capital Social (R$)'].sum()
avg_idh = df_filtered['IDH Municipal (PNUD)'].mean()
avg_seg = df_filtered['Qtd Seguidores'].mean()

cap_fmt = f"R$ {total_cap/1e9:.2f} Bi" if total_cap >= 1e9 else f"R$ {total_cap/1e6:.1f} Mi"

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Empresas Filtradas</div>
        <div class="metric-value">{total_emp} <span style="font-size:14px;color:#64748B;">/ 350</span></div>
        <div class="metric-sub">100% CNPJs Ativos</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #10B981;">
        <div class="metric-label">Capital Social Total</div>
        <div class="metric-value">{cap_fmt}</div>
        <div class="metric-sub">Média R$ {df_filtered['Capital Social (R$)'].mean()/1e6:.1f}M por empresa</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #F59E0B;">
        <div class="metric-label">IDH-M Médio Polos</div>
        <div class="metric-value">{avg_idh:.3f}</div>
        <div class="metric-sub">Muito Alto (Padrão PNUD)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #6366F1;">
        <div class="metric-label">Seguidores Médios</div>
        <div class="metric-value">{avg_seg:,.0f}</div>
        <div class="metric-sub">Engajamento LinkedIn</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- INTERACTIVE TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Mapa Cartográfico & Geográfico", 
    "📊 Analytics & Indicadores B2B", 
    "🏢 Ficha do Lead & Pitch MGP", 
    "📥 Exportação & De-Para CRM"
])

# --- TAB 1: GEOGRAPHIC MAP ---
with tab1:
    st.subheader("📍 Mapeamento Geográfico das Indústrias por Cluster")
    st.caption("Visualização georreferenciada da densidade industrial no Estado de SP e Região Metropolitana.")
    
    if len(df_filtered) > 0:
        map_kwargs = dict(
            data_frame=df_filtered,
            lat="lat",
            lon="lon",
            color="Tier MGP",
            size="Capital Social (R$)",
            size_max=30,
            hover_name="Nome da Empresa",
            hover_data={
                "Cidade": True,
                "CNPJ": True,
                "Capital Social (R$)": ":,.0f",
                "Qtd Seguidores": ":,.0f",
                "Tier MGP": True,
                "lat": False,
                "lon": False
            },
            color_discrete_map={
                "Tier 1 (Enterprise)": "#DC2626",
                "Tier 2 (Mid-Market)": "#D97706",
                "Tier 3 (PMEs / Regionais)": "#2563EB"
            },
            zoom=8,
            center={"lat": -23.5505, "lon": -46.6333},
            height=600
        )
        
        try:
            if hasattr(px, 'scatter_map'):
                fig_map = px.scatter_map(map_style="open-street-map", **map_kwargs)
            elif hasattr(px, 'scatter_mapbox'):
                fig_map = px.scatter_mapbox(mapbox_style="open-street-map", **map_kwargs)
            else:
                fig_map = px.scatter_geo(fitbounds="locations", **map_kwargs)
        except Exception:
            try:
                fig_map = px.scatter_map(**map_kwargs)
            except Exception:
                fig_map = px.scatter_mapbox(mapbox_style="carto-positron", **map_kwargs)

        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Nenhuma empresa encontrada com os filtros selecionados.")

# --- TAB 2: ANALYTICS & B2B KPIs ---
with tab2:
    st.subheader("📈 Análise de Atratividade & Inteligência de Mercado")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Distribuição das Empresas por Tier MGP**")
        tier_counts = df_filtered['Tier MGP'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Quantidade']
        fig_tier = px.pie(
            tier_counts, 
            names='Tier', 
            values='Quantidade', 
            hole=0.4,
            color='Tier',
            color_discrete_map={
                "Tier 1 (Enterprise)": "#DC2626",
                "Tier 2 (Mid-Market)": "#D97706",
                "Tier 3 (PMEs / Regionais)": "#2563EB"
            }
        )
        fig_tier.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_tier, use_container_width=True)
        
    with col_b:
        st.write("**Capital Social Consolidado por Polo Regional**")
        polo_cap = df_filtered.groupby('Polo Industrial / Região')['Capital Social (R$)'].sum().reset_index()
        polo_cap['Capital_Mi'] = polo_cap['Capital Social (R$)'] / 1e6
        polo_cap = polo_cap.sort_values('Capital_Mi', ascending=True)
        fig_polo = px.bar(
            polo_cap, 
            y='Polo Industrial / Região', 
            x='Capital_Mi', 
            orientation='h',
            labels={'Capital_Mi': 'Capital Social (R$ Milhões)', 'Polo Industrial / Região': ''},
            color_discrete_sequence=['#0284C7']
        )
        fig_polo.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_polo, use_container_width=True)
        
    st.markdown("---")
    
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.write("**Matriz de Atratividade: Capital Social vs. Seguidores (LinkedIn)**")
        fig_scatter = px.scatter(
            df_filtered,
            x="Qtd Seguidores",
            y="Capital Social (R$)",
            color="Tier MGP",
            hover_name="Nome da Empresa",
            log_x=True,
            log_y=True,
            color_discrete_map={
                "Tier 1 (Enterprise)": "#DC2626",
                "Tier 2 (Mid-Market)": "#D97706",
                "Tier 3 (PMEs / Regionais)": "#2563EB"
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_d:
        st.write("**Top 10 Municípios em Densidade de Indústrias**")
        top_cities = df_filtered['Cidade'].value_counts().head(10).reset_index()
        top_cities.columns = ['Cidade', 'Qtd Indústrias']
        fig_city = px.bar(
            top_cities, 
            x='Cidade', 
            y='Qtd Indústrias',
            color_discrete_sequence=['#0F172A']
        )
        st.plotly_chart(fig_city, use_container_width=True)

# --- TAB 3: LEAD DETAIL & MGP PITCH ---
with tab3:
    st.subheader("🏢 Ficha do Lead & Roteiro de Abordagem MGP")
    
    if len(df_filtered) > 0:
        company_names = sorted(df_filtered['Nome da Empresa'].unique())
        selected_company = st.selectbox("Selecione uma empresa para visualizar a Ficha Completa:", company_names)
        
        lead = df_filtered[df_filtered['Nome da Empresa'] == selected_company].iloc[0]
        
        st.markdown("---")
        
        f_col1, f_col2 = st.columns([1, 2])
        
        with f_col1:
            tier_badge = lead['Tier MGP']
            st.markdown(f"### **{lead['Nome da Empresa']}**")
            st.markdown(f"**Tier:** `{tier_badge}`")
            st.markdown(f"**Razão Social:** {lead['Razão Social Oficial']}")
            st.markdown(f"**CNPJ:** `{lead['CNPJ']}` (Status: {lead['Situação Cadastral']})")
            st.markdown(f"**Capital Social:** R$ {lead['Capital Social (R$)']:,.2f}")
            st.markdown(f"**Cidade/UF:** {lead['Cidade']} / {lead['UF']}")
            st.markdown(f"**Polo:** {lead['Polo Industrial / Região']}")
            st.markdown(f"**Seguidores LinkedIn:** {lead['Qtd Seguidores']:,}")
            if pd.notna(lead['Site Oficial']):
                st.markdown(f"🌐 [Acessar Website Oficial]({lead['Site Oficial']})")
                
        with f_col2:
            st.markdown("#### 📝 Resumo Institucional & Mapeamento de Conexões")
            st.info(lead['Resumo Institucional'])
            
            st.markdown("#### 🎯 Roteiro de Abordagem Comercial Recomendado MGP")
            
            if "Tier 1" in tier_badge:
                st.success("""
                **Estratégia Tier 1 (Enterprise - Multicanal C-Level):**
                * **Decisor Alvo:** CEO, COO, Diretor Industrial, VP de Suprimentos.
                * **Abordagem:** LinkedIn InMail + Cold Mail consultivo.
                * **Gancho de Warm Outbound:** Utilize a informação de conexões em comum e porte para abrir o contato.
                * **Pitch MGP:** "Otimização de processos fabris em larga escala, governança e redução de custos de produção sem interromper a planta."
                """)
            elif "Tier 2" in tier_badge:
                st.warning("""
                **Estratégia Tier 2 (Mid-Market - Cadência Outbound SDR):**
                * **Decisor Alvo:** Gerente de Planta, Gerente de Operações, P&D / Qualidade.
                * **Abordagem:** Cadência de 14 dias (Cold Mail + LinkedIn Direct + Telefone SDR).
                * **Gancho de Warm Outbound:** Cite a presença regional e o segmento exato da empresa.
                * **Pitch MGP:** "Eliminação de gargalos na linha, ganho de OEE e adequação rápida às normas da ANVISA/MAPA."
                """)
            else:
                st.info("""
                **Estratégia Tier 3 (PMEs / Regionais - Vendas Diretas):**
                * **Decisor Alvo:** Sócio-Fundador, Diretor Geral.
                * **Abordagem:** WhatsApp Business + Ligação Direta.
                * **Pitch MGP:** "Aumento de margem operacional e profissionalização da gestão para suportar o crescimento."
                """)
    else:
        st.warning("Nenhuma empresa disponível para exibição.")

# --- TAB 4: EXPORT & CRM MAPPING ---
with tab4:
    st.subheader("📥 Exportação de Dados & Integração com CRM")
    st.write("Exporte a lista de empresas filtradas ou consulte a tabela de correspondência para importação no CRM.")
    
    # Export Button
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='Base_Filtrada_MGP')
    buffer.seek(0)
    
    st.download_button(
        label="📥 Baixar Base Filtrada em Excel (.xlsx)",
        data=buffer,
        file_name="base_mgp_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("---")
    st.subheader("📋 Tabela dos Dados Filtrados")
    
    display_cols = ['ID', 'Nome da Empresa', 'Razão Social Oficial', 'CNPJ', 'Tier MGP', 'Cidade', 'Capital Social (R$)', 'Qtd Seguidores', 'CNAE / Atividade Principal']
    st.dataframe(df_filtered[display_cols], use_container_width=True)

# Footer
st.markdown("---")
st.caption("CONFIDENCIAL — MGP Consultoria & Inteligência de Mercado © 2026")
