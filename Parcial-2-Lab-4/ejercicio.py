import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

# URL de la aplicación (actualiza según tu implementación)
# app_url = 'https://mi-aplicacion-ventas.streamlit.app/'

def mostrar_Informacion_alumno():
    with st.container(border=True):
        st.markdown('**Legajo:** 58.899')
        st.markdown('**Nombre:** Villagra Juan Gabriel')
        st.markdown('**Comision:** C5')

st.set_page_config(page_title="Análisis Comercial", layout="wide")

st.markdown("""
    <style>
    .positivo { color: #198754; }
    .negativo { color: #dc3545; }
    .contenedor-indicador {
        display: flex;
        flex-direction: column;
        margin-bottom: 1.5rem;
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    .valor-indicador { 
        font-size: 2.5rem; 
        font-weight: bold;
        margin: 0.5rem 0;
        color: white;
    }
    .etiqueta-indicador { 
        font-size: 1rem; 
        color: #b0b0b0;
        margin-bottom: 0.25rem;
    }
    .variacion-indicador {
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)

def calcular_indicadores(tabla, item, tabla_anterior=None):
    datos_item = tabla[tabla['Producto'] == item]
    
    ingresos_totales = datos_item['Ingreso_total'].sum()
    unidades_vendidas = datos_item['Unidades_vendidas'].sum()
    precio_promedio = ingresos_totales / unidades_vendidas if unidades_vendidas > 0 else 0
    
    costos_totales = datos_item['Costo_total'].sum()
    margen_porcentaje = ((ingresos_totales - costos_totales) / ingresos_totales * 100) if ingresos_totales > 0 else 0
    
    if tabla_anterior is not None:
        datos_previos = tabla_anterior[tabla_anterior['Producto'] == item]
        ingresos_previos = datos_previos['Ingreso_total'].sum()
        unidades_previas = datos_previos['Unidades_vendidas'].sum()
        precio_anterior = ingresos_previos / unidades_previas if unidades_previas > 0 else 0
        margen_anterior = ((ingresos_previos - datos_previos['Costo_total'].sum()) / ingresos_previos * 100) if ingresos_previos > 0 else 0
        
        variacion_precio = ((precio_promedio - precio_anterior) / precio_anterior * 100) if precio_anterior > 0 else 0
        variacion_margen = margen_porcentaje - margen_anterior
        variacion_unidades = ((unidades_vendidas - unidades_previas) / unidades_previas * 100) if unidades_previas > 0 else 0
    else:
        variacion_precio = variacion_margen = variacion_unidades = 0
    
    return precio_promedio, margen_porcentaje, unidades_vendidas, variacion_precio, variacion_margen, variacion_unidades

def mostrar_indicador(etiqueta, valor, variacion, tipo_formato="numero"):
    if tipo_formato == "moneda":
        valor_formateado = f"${valor:,.0f}"
    elif tipo_formato == "porcentaje":
        valor_formateado = f"{valor:.0f}%"
    else:
        valor_formateado = f"{valor:,.0f}"
    
    clase_variacion = 'positivo' if variacion >= 0 else 'negativo'
    flecha = '↑' if variacion > 0 else '↓'
    signo = '+' if variacion > 0 else '-'
    variacion_formateada = f"{signo}{abs(variacion):.2f}%"
    
    st.markdown(f"""
    <div class="contenedor-indicador">
        <div class="etiqueta-indicador">{etiqueta}</div>
        <div class="valor-indicador">{valor_formateado}</div>
        <div class="variacion-indicador {clase_variacion}">
            {flecha} {variacion_formateada}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.title("Subir Datos")
st.sidebar.write("Cargar archivo CSV")
archivo_subido = st.sidebar.file_uploader("Selecciona un archivo", type=['csv'])
zonas = ["Todas", "Norte", "Centro", "Sur"]
zona_seleccionada = st.sidebar.selectbox("Selecciona una Zona", zonas)

if not archivo_subido:
    st.title("Por favor, carga un archivo CSV desde el panel lateral.")
else:
    tabla = pd.read_csv(archivo_subido)
    
    año_actual = tabla['Año'].max()
    año_anterior = año_actual - 1
    
    datos_actuales = tabla[tabla['Año'] == año_actual]
    datos_previos = tabla[tabla['Año'] == año_anterior]
    
    if zona_seleccionada != "Todas":
        datos_actuales = datos_actuales[datos_actuales['Sucursal'] == zona_seleccionada]
        datos_previos = datos_previos[datos_previos['Sucursal'] == zona_seleccionada]
    
    st.markdown(f"""
        <h1 style="color: white; margin-bottom: 2rem;">
            Información de {'Todas las Zonas' if zona_seleccionada == 'Todas' else zona_seleccionada}
        </h1>
    """, unsafe_allow_html=True)
    
    for producto in datos_actuales['Producto'].unique():
        col_metricas, col_grafico = st.columns([1, 2])

        with col_metricas:
            st.header(producto)
            precio_prom, margen_prom, unidades_totales, variacion_precio, variacion_margen, variacion_unidades = calcular_indicadores(datos_actuales, producto, datos_previos)
            
            mostrar_indicador("Precio Promedio", precio_prom, variacion_precio, "moneda")
            mostrar_indicador("Margen (%)", margen_prom, variacion_margen, "porcentaje")
            mostrar_indicador("Unidades Vendidas", unidades_totales, variacion_unidades)

        with col_grafico:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            
            serie_tiempo = tabla[tabla['Producto'] == producto].groupby(['Año', 'Mes'])['Unidades_vendidas'].sum().reset_index()
            serie_tiempo['Fecha'] = pd.to_datetime(serie_tiempo['Año'].astype(str) + '-' + 
                                                   serie_tiempo['Mes'].astype(str).str.zfill(2) + '-01')
            serie_tiempo = serie_tiempo.sort_values('Fecha')
            
            x = np.arange(len(serie_tiempo))
            pendiente, intercepcion, _, _, _ = stats.linregress(x, serie_tiempo['Unidades_vendidas'])
            linea_tendencia = pendiente * x + intercepcion
            
            grafico = go.Figure()
            
            grafico.add_trace(go.Scatter(
                x=serie_tiempo['Fecha'],
                y=serie_tiempo['Unidades_vendidas'],
                mode='lines',
                name=producto,
                line=dict(color='#1f77b4', width=2)
            ))
            
            grafico.add_trace(go.Scatter(
                x=serie_tiempo['Fecha'],
                y=linea_tendencia,
                mode='lines',
                name='Tendencia',
                line=dict(color='#ff7f0e', width=2, dash='dot')
            ))
            
            grafico.update_layout(
                title="Ventas Mensuales",
                xaxis_title="Fecha",
                yaxis_title="Unidades",
                showlegend=True,
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(grafico, use_container_width=True)

mostrar_Informacion_alumno()
