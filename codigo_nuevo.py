import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import json

st.set_page_config(page_title="Dashboard Inversión MOP", page_icon="📈", layout="wide")
st.title("📊 Dashboard de Inversión MOP 2021")

@st.cache_data
def cargar_datos_seguros(filas_a_saltar):
    url = "https://datos.gob.cl/dataset/104d1ebf-4d1b-4c3d-af9e-e85e5bbf1fc9/resource/e9d62fab-96d3-40e0-8b6f-faf7891cfd4e/download/resumen-inversion-mop-2021.xls"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    respuesta = requests.get(url, headers=headers, timeout=15)
    respuesta.raise_for_status() 
    
    archivo_memoria = io.BytesIO(respuesta.content)
    df = pd.read_excel(archivo_memoria, skiprows=filas_a_saltar)
    df = df.dropna(how='all')
    
    datos_json_str = df.to_json(orient="records", force_ascii=False)
    datos_json = json.loads(datos_json_str)
    
    return df, datos_json

with st.sidebar:
    st.header("⚙️ Ajustes de Datos")
    saltar_filas = st.number_input("Filas de encabezado a saltar", min_value=0, max_value=10, value=0)

with st.spinner('Descargando y procesando datos del gobierno...'):
    try:
        df_limpio, datos_en_json = cargar_datos_seguros(saltar_filas)
        
        tab1, tab2, tab3 = st.tabs(["📈 Visualización (Gráficos)", "📋 Tabla de Datos", "📦 Estructura JSON"])
        
        with tab1:
            if len(df_limpio.columns) >= 2 and not df_limpio.empty:
                
                # --- GRÁFICO 1: Datos de la primera fila ---
                st.subheader("📈 Gráfico 1: Análisis de la Primera Fila")
                primera_fila = df_limpio.iloc[0]
                nombre_fila = primera_fila.iloc[0]
                categorias_g1 = df_limpio.columns[1:].astype(str)
                valores_g1 = pd.to_numeric(primera_fila.iloc[1:], errors='coerce')
                
                fig1, ax1 = plt.subplots(figsize=(12, 5))
                ax1.bar(categorias_g1, valores_g1, color='#2c7fb8', edgecolor='black')
                ax1.set_title(f'Datos para: {nombre_fila}', fontsize=14)
                ax1.set_xlabel('Métricas', fontsize=10)
                ax1.set_ylabel('Monto', fontsize=10)
                ax1.tick_params(axis='x', labelrotation=45, labelsize=9)
                ax1.grid(axis='y', linestyle='--', alpha=0.7)
                
                fig1.tight_layout()
                st.pyplot(fig1)

                st.divider() # Línea separadora visual

                # --- GRÁFICO 2: Comparación por columna seleccionada ---
                st.subheader("📊 Gráfico 2: Comparación por Métrica")
                
                # Menú desplegable para que el usuario elija la columna a graficar
                columnas_disponibles = df_limpio.columns[1:].tolist()
                columna_elegida = st.selectbox("Selecciona la métrica que deseas comparar:", columnas_disponibles)
                
                # Eje X: Primera columna (nombres/categorías)
                categorias_g2 = df_limpio.iloc[:, 0].astype(str)
                # Eje Y: Columna elegida por el usuario
                valores_g2 = pd.to_numeric(df_limpio[columna_elegida], errors='coerce')

                fig2, ax2 = plt.subplots(figsize=(12, 5))
                # Usamos un color distinto para diferenciar los gráficos
                ax2.bar(categorias_g2, valores_g2, color='#31a354', edgecolor='black') 
                
                ax2.set_title(f'Comparativa de: {columna_elegida}', fontsize=14)
                ax2.set_xlabel(str(df_limpio.columns[0]), fontsize=10)
                ax2.set_ylabel('Monto', fontsize=10)
                ax2.tick_params(axis='x', labelrotation=45, labelsize=9)
                ax2.grid(axis='y', linestyle='--', alpha=0.7)
                
                fig2.tight_layout()
                st.pyplot(fig2)

            else:
                st.warning("El dataset no tiene suficientes columnas o filas para graficar.")
                
        with tab2:
            st.subheader("Datos Tabulares (Pandas)")
            st.dataframe(df_limpio, use_container_width=True)
            
        with tab3:
            st.subheader("Datos Estructurados (JSON)")
            st.json(datos_en_json)

        st.divider()
        st.subheader("💡 Resumen Rápido")
        col1, col2 = st.columns(2)
        col1.metric(label="Total de Registros Extraídos", value=len(df_limpio))
        col2.metric(label="Total de Columnas Identificadas", value=len(df_limpio.columns))
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
