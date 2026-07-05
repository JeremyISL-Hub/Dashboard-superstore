import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Superstore", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    df = pd.read_csv('Superstore_clean.csv')
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    if 'Ship Date' in df.columns:
        df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    return df

df = cargar_datos()
PALETA_COLORES = px.colors.qualitative.Safe

if 'Order Date' in df.columns and not df['Order Date'].isna().all():
    min_date_global = df['Order Date'].min().date()
    max_date_global = df['Order Date'].max().date()
else:
    min_date_global = None
    max_date_global = None

def reset_filtros():
    claves_filtros = ['f_country', 'f_region', 'f_state', 'f_city', 'f_category', 'f_subcat', 'f_segment', 'f_shipmode']
    for key in claves_filtros:
        if key in st.session_state:
            st.session_state[key] = []
    
    if 'f_date' in st.session_state and min_date_global and max_date_global:
        st.session_state['f_date'] = (min_date_global, max_date_global)

st.sidebar.title("Panel de Filtros")
st.sidebar.button("Restablecer Filtros", on_click=reset_filtros)

if min_date_global and max_date_global:
    fechas = st.sidebar.date_input(
        "Rango de Fechas (Order Date):",
        value=(min_date_global, max_date_global),
        min_value=min_date_global,
        max_value=max_date_global,
        key='f_date'
    )
else:
    fechas = []

with st.sidebar.expander("📍 Ubicación", expanded=True):
    paises = df['Country'].dropna().unique().tolist() if 'Country' in df.columns else []
    pais_sel = st.multiselect("País:", options=paises, key='f_country', placeholder="Elegir...")
    
    regiones = df['Region'].dropna().unique().tolist() if 'Region' in df.columns else []
    region_sel = st.multiselect("Región:", options=regiones, key='f_region', placeholder="Elegir...")
    
    estados = df['State'].dropna().unique().tolist() if 'State' in df.columns else []
    estado_sel = st.multiselect("Estado:", options=estados, key='f_state', placeholder="Elegir...")
    
    ciudades = df['City'].dropna().unique().tolist() if 'City' in df.columns else []
    ciudad_sel = st.multiselect("Ciudad:", options=ciudades, key='f_city', placeholder="Elegir...")

with st.sidebar.expander("📦 Producto y Categoría", expanded=False):
    categorias = df['Category'].dropna().unique().tolist() if 'Category' in df.columns else []
    categoria_sel = st.multiselect("Categoría:", options=categorias, key='f_category', placeholder="Elegir...")
    
    subcategorias = df['Sub-Category'].dropna().unique().tolist() if 'Sub-Category' in df.columns else []
    subcat_sel = st.multiselect("Sub-Categoría:", options=subcategorias, key='f_subcat', placeholder="Elegir...")

with st.sidebar.expander("👥 Cliente y Envío", expanded=False):
    segmentos = df['Segment'].dropna().unique().tolist() if 'Segment' in df.columns else []
    segmento_sel = st.multiselect("Segmento:", options=segmentos, key='f_segment', placeholder="Elegir...")
    
    envios = df['Ship Mode'].dropna().unique().tolist() if 'Ship Mode' in df.columns else []
    envio_sel = st.multiselect("Modo de Envío:", options=envios, key='f_shipmode', placeholder="Elegir...")

df_filtrado = df.copy()

if len(fechas) == 2:
    df_filtrado = df_filtrado[(df_filtrado['Order Date'].dt.date >= fechas[0]) & (df_filtrado['Order Date'].dt.date <= fechas[1])]
if pais_sel:
    df_filtrado = df_filtrado[df_filtrado['Country'].isin(pais_sel)]
if region_sel:
    df_filtrado = df_filtrado[df_filtrado['Region'].isin(region_sel)]
if estado_sel:
    df_filtrado = df_filtrado[df_filtrado['State'].isin(estado_sel)]
if ciudad_sel:
    df_filtrado = df_filtrado[df_filtrado['City'].isin(ciudad_sel)]
if categoria_sel:
    df_filtrado = df_filtrado[df_filtrado['Category'].isin(categoria_sel)]
if subcat_sel:
    df_filtrado = df_filtrado[df_filtrado['Sub-Category'].isin(subcat_sel)]
if segmento_sel:
    df_filtrado = df_filtrado[df_filtrado['Segment'].isin(segmento_sel)]
if envio_sel:
    df_filtrado = df_filtrado[df_filtrado['Ship Mode'].isin(envio_sel)]

st.title("🛒 Dashboard Ejecutivo de Ventas - Superstore")

t_ventas = df_filtrado['Sales'].sum() if 'Sales' in df_filtrado.columns else 0
t_ganancias = df_filtrado['Profit'].sum() if 'Profit' in df_filtrado.columns else 0
t_cantidad = df_filtrado['Quantity'].sum() if 'Quantity' in df_filtrado.columns else 0
t_descuento = df_filtrado['Discount'].mean() * 100 if 'Discount' in df_filtrado.columns else 0
t_clientes = df_filtrado['Customer ID'].nunique() if 'Customer ID' in df_filtrado.columns else 0

if not df_filtrado.empty and 'Product Name' in df_filtrado.columns and 'Quantity' in df_filtrado.columns:
    p_estrella = str(df_filtrado.groupby('Product Name')['Quantity'].sum().idxmax())
    p_estrella = p_estrella[:14] + "..." if len(p_estrella) > 14 else p_estrella
else:
    p_estrella = "N/A"

def crear_tarjeta(titulo, valor, color_borde):
    return f"""
    <div style="background-color: #1e2130; border-left: 5px solid {color_borde}; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
        <p style="color: #a1a5b7; font-size: 12px; font-weight: 600; text-transform: uppercase; margin: 0 0 5px 0;">{titulo}</p>
        <p style="color: #ffffff; font-size: 18px; font-weight: bold; margin: 0;">{valor}</p>
    </div>
    """

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

kpi1.markdown(crear_tarjeta("Ventas Totales", f"${t_ventas:,.0f}", "#00c0f2"), unsafe_allow_html=True)
kpi2.markdown(crear_tarjeta("Ganancia Total", f"${t_ganancias:,.0f}", "#00e396"), unsafe_allow_html=True)
kpi3.markdown(crear_tarjeta("Unidades", f"{t_cantidad:,.0f}", "#feb019"), unsafe_allow_html=True)
kpi4.markdown(crear_tarjeta("Desc. Prom.", f"{t_descuento:,.2f}%", "#ff4560"), unsafe_allow_html=True)
kpi5.markdown(crear_tarjeta("Clientes Únicos", f"{t_clientes:,}", "#775dd0"), unsafe_allow_html=True)
kpi6.markdown(crear_tarjeta("Prod. Estrella", p_estrella, "#4caf50"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

r1c1, r1c2 = st.columns(2)

with r1c1:
    st.subheader("Tendencia de Ventas (Área)")
    if not df_filtrado.empty and 'Order Date' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        df_tiempo = df_filtrado.groupby(df_filtrado['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
        df_tiempo['Order Date'] = df_tiempo['Order Date'].dt.to_timestamp()
        fig_area = px.area(
            df_tiempo, 
            x='Order Date', 
            y='Sales', 
            color_discrete_sequence=[PALETA_COLORES[0]]
        )
        fig_area.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Fecha", yaxis_title="Ventas (USD)")
        st.plotly_chart(fig_area, width="stretch")

with r1c2:
    st.subheader("Jerarquía: Categorías vs Ventas")
    if not df_filtrado.empty and 'Category' in df_filtrado.columns and 'Sub-Category' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        fig_tree = px.treemap(
            df_filtrado, 
            path=[px.Constant("Productos"), 'Category', 'Sub-Category'], 
            values='Sales',
            color='Profit' if 'Profit' in df_filtrado.columns else 'Sales',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=0 if 'Profit' in df_filtrado.columns else None
        )
        fig_tree.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_tree, width="stretch")

st.markdown("---")

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.subheader("Rendimiento por Sub-Categoría")
    if not df_filtrado.empty and 'Sub-Category' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        df_subcat = df_filtrado.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
        fig_barras = px.bar(
            df_subcat, 
            x='Sub-Category', 
            y='Sales', 
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_barras.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(l=20, r=20, t=20, b=20), xaxis_tickangle=-45)
        st.plotly_chart(fig_barras, width="stretch")

with r2c2:
    st.subheader("Relación: Ventas vs Ganancias")
    if not df_filtrado.empty and 'Sales' in df_filtrado.columns and 'Profit' in df_filtrado.columns:
        fig_scatter = px.scatter(
            df_filtrado, 
            x='Sales', 
            y='Profit', 
            color='Category' if 'Category' in df_filtrado.columns else None,
            hover_data=['Product Name'] if 'Product Name' in df_filtrado.columns else None,
            opacity=0.7,
            color_discrete_sequence=PALETA_COLORES
        )
        fig_scatter.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Ventas (USD)", yaxis_title="Ganancias (USD)")
        st.plotly_chart(fig_scatter, width="stretch")

st.markdown("---")

c3, c4, c5 = st.columns([1.5, 1, 1])

with c3:
    st.subheader("Top 10 Ciudades por Ingresos")
    if not df_filtrado.empty and 'City' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        df_ciudad = df_filtrado.groupby('City')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
        fig_ciudad = px.bar(
            df_ciudad, 
            x='Sales', 
            y='City', 
            orientation='h',
            color='Sales',
            color_continuous_scale='Teal'
        )
        fig_ciudad.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_ciudad, width="stretch")

with c4:
    st.subheader("Distribución por Segmento")
    if not df_filtrado.empty and 'Segment' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        fig_seg = px.pie(
            df_filtrado, 
            names='Segment', 
            values='Sales', 
            hole=0.4,
            color_discrete_sequence=PALETA_COLORES
        )
        fig_seg.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_seg, width="stretch")

with c5:
    st.subheader("Distribución por Modo de Envío")
    if not df_filtrado.empty and 'Ship Mode' in df_filtrado.columns and 'Sales' in df_filtrado.columns:
        fig_ship = px.pie(
            df_filtrado, 
            names='Ship Mode', 
            values='Sales', 
            hole=0.4,
            color_discrete_sequence=PALETA_COLORES[::-1]
        )
        fig_ship.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_ship, width="stretch")
