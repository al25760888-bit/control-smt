import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("mantenimiento_web.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT,
                        mo TEXT,
                        maquina TEXT,
                        soporte TEXT,
                        fecha TEXT)''')
    conn.commit()
    return conn

# --- INTERFAZ CON STREAMLIT ---
st.set_page_config(page_title="Control SMT - Hector Gomez", layout="wide")
st.title("🛠️ Sistema de Gestión de SMT")

# Sidebar para captura de datos
st.sidebar.header("Nuevo Registro")
with st.sidebar.form("formulario"):
    usuario = st.text_input("Nombre de Usuario")
    mo = st.text_input("MO")
    maquina = st.text_input("Máquina")
    soporte = st.selectbox("Tipo de Soporte", ["Preventivo", "Correctivo", "Calibración", "Limpieza"])
    fecha = st.date_input("Fecha", datetime.now())
    
    boton_guardar = st.form_submit_button("Guardar Registro")

if boton_guardar:
    if usuario and maquina:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registros (usuario, mo, maquina, soporte, fecha) VALUES (?, ?, ?, ?, ?)",
                       (usuario, mo, maquina, soporte, str(fecha)))
        conn.commit()
        conn.close()
        st.sidebar.success("¡Registro guardado!")
    else:
        st.sidebar.error("Faltan campos obligatorios")

# --- VISUALIZACIÓN Y ACCIONES ---
st.subheader("📋 Registros Actuales")
conn = conectar_db()
df = pd.read_sql_query("SELECT * FROM registros", conn)
conn.close()

if not df.empty:
    # Mostrar tabla
    st.dataframe(df, use_container_width=True)

    # Botones de acción en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        # Exportar a Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Descargar Reporte (CSV/Excel)",
            data=csv,
            file_name=f"Reporte_SMT_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    
    with col2:
        # Borrar último registro (ejemplo simple)
        if st.button("🗑️ Borrar último registro"):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM registros WHERE id = (SELECT MAX(id) FROM registros)")
            conn.commit()
            conn.close()
            st.rerun()
else:
    st.info("Aún no hay registros en la base de datos.")