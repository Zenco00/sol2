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
    
    # 1. Descarga segura usando requests
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    respuesta = requests.get(url, headers=headers, timeout=15)
    respuesta.raise_for_status() 
    
    # 2. Lectura en memoria con io y Pandas
    archivo_memoria = io.BytesIO(respuesta.content)
    df = pd.read_excel(archivo_memoria, skiprows=filas_a_saltar)
    df = df.dropna(how='all')
    
    # 3. Conversión a JSON para un manejo estructurado
    datos_json_str = df.to_json(orient="records", force_ascii=False)
    datos_json = json.loads(datos_json_str)
    
    return df, datos_json

with st.sidebar:
    st.header("⚙️ Ajustes de Datos")
    saltar_filas = st.number_input("Filas de encabezado a saltar", min_value=0, max_value=10, value=0)

with st.spinner('Descargando y procesando datos del gobierno...'):
    try:
        df_limpio, datos_en_json = cargar_datos_seguros(saltar_filas)
        
        # Usamos pestañas (tabs) para organizar visualmente la aplicación
        tab1, tab2, tab3 = st.tabs(["📈 Visualización (Gráfico)", "📋 Tabla de Datos", "📦 Estructura JSON"])
        
        with tab1:
            st.subheader("📈 Gráfico de la Primera Fila")
            
            if len(df_limpio.columns) >= 2 and not df_limpio.empty:
                # 1. Extraemos solo la primera fila (índice 0)
                primera_fila = df_limpio.iloc[0]
                
                # 2. Usamos la primera celda como nombre/etiqueta principal
                nombre_fila = primera_fila.iloc[0]
                
                # 3. Las categorías (Eje X) serán los nombres de todas las columnas, saltando la primera
                categorias = df_limpio.columns[1:].astype(str)
                
                # 4. Los valores (Eje Y) serán los datos de la primera fila, saltando la primera celda
                valores = pd.to_numeric(primera_fila.iloc[1:], errors='coerce')
                
                # Creamos la figura
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.bar(categorias, valores, color='#2c7fb8', edgecolor='black')

                # Personalización
                ax.set_title(f'Datos para: {nombre_fila}', fontsize=14)
                ax.set_xlabel('Columnas (Categorías)', fontsize=10)
                ax.set_ylabel('Monto', fontsize=10)
                
                # Rotamos los nombres de las columnas a 45 grados por si son muy largos
                ax.tick_params(axis='x', labelrotation=45, labelsize=9)
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Renderizamos en Streamlit
                fig.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("El dataset no tiene suficientes columnas o filas para graficar.")
                
        with tab2:
            st.subheader("Datos Tabulares (Pandas)")
            st.dataframe(df_limpio, use_container_width=True)
            
        with tab3:
            st.subheader("Datos Estructurados (JSON)")
            st.markdown("Visualización nativa del objeto JSON generado a partir de la consulta:")
            st.json(datos_en_json)

        st.divider()
        st.subheader("💡 Resumen Rápido")
        col1, col2 = st.columns(2)
        col1.metric(label="Total de Registros Extraídos", value=len(df_limpio))
        col2.metric(label="Total de Columnas Identificadas", value=len(df_limpio.columns))
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
