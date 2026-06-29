import streamlit as st
import random
import time
import os
import base64
from PIL import Image
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Ruleta de la Suerte", page_icon="🎡", layout="centered")

if 'opciones' not in st.session_state:
    st.session_state.opciones = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None
if 'rotacion_actual' not in st.session_state:
    st.session_state.rotacion_actual = 0 

# --- 2. CONFIGURACIÓN DE IMÁGENES LOCALES ---
# A) Logo Central
RUTA_LOGO = "logo.png"
if os.path.exists(RUTA_LOGO):
    imagen_centro = Image.open(RUTA_LOGO)
else:
    imagen_centro = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=200"

# B) Fondo de Pantalla Local con Transparencia/Tinte
RUTA_FONDO = "fondo.png"
if os.path.exists(RUTA_FONDO):
    with open(RUTA_FONDO, "rb") as f:
        base64_fondo = base64.b64encode(f.read()).decode()
    
    # Explicación: El linear-gradient aplica una capa negra con 75% de opacidad (0.75) 
    # encima de tu imagen para darle ese efecto sutil y que resalte la ruleta.
    estilo_fondo = f"""
        background-image: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.75)), url("data:image/png;base64,{base64_fondo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    """
else:
    # Degradado de respaldo por si aún no pusiste el archivo fondo.png
    estilo_fondo = "background: linear-gradient(135deg, #0f172a, #1e1b4b);"


# --- 3. ESTILOS VISUALES INYECTADOS ---
st.markdown(f"""
    <style>
    .stApp {{ 
        {estilo_fondo}
        color: white; 
    }}
    .titulo {{ text-align: center; font-size: 3.5rem; margin-bottom: 0; font-weight: 800; }}
    .ganador-txt {{ 
        text-align: center; font-size: 3.5rem; color: #Hff4b4b; 
        font-weight: 900; margin: 10px 0; text-transform: uppercase;
    }}
    .puntero {{
        text-align: center; font-size: 3rem; color: #ff4b4b; 
        margin-bottom: -40px; z-index: 10; position: relative;
    }}
    div[data-testid="stButton"] > button[kind="secondary"]:hover {{
        background-color: #e2e8f0 !important;
        color: #0f172a !important; /* Texto oscuro para que resalte y se lea */
        border-color: #0f172a !important; /* Borde oscuro */
    }}
    </style>
    
""", unsafe_allow_html=True)

st.markdown("<p class='titulo'>🎡 Ruleta de tiktoks</p>", unsafe_allow_html=True)

# --- 4. FORMULARIO PARA AGREGAR OPCIONES ---
with st.form("agregar_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        nueva_opcion = st.text_input("Agregar opción:", placeholder="Ej: Fede, Helado, Reto...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("➕ Agregar", use_container_width=True, type="primary")
        if submit and nueva_opcion.strip():
            if nueva_opcion.strip() not in st.session_state.opciones:
                st.session_state.opciones.append(nueva_opcion.strip())
                st.session_state.ganador = None
                st.rerun()

if st.session_state.opciones:
    st.write(f"**Opciones en juego:** " + ", ".join(st.session_state.opciones))

# --- 5. FUNCIÓN PARA DIBUJAR LA RULETA ---
def dibujar_ruleta(opciones, rotacion):
    fig = go.Figure(data=[go.Pie(
        labels=opciones,
        values=[1] * len(opciones),
        textinfo='label',
        textfont_size=22,
        hole=0.4, # Este es el tamaño del hueco de la dona (40%)
        hoverinfo='none',
        sort=False,
        direction='clockwise',
        rotation=rotacion,
        marker=dict(line=dict(color='#0f172a', width=4))
    )])
    
    fig.add_layout_image(
        dict(
            source=imagen_centro,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            # ¡ACÁ ESTÁ EL CAMBIO! Agrandamos sizex y sizey para cubrir el hueco de 0.4
            sizex=0.35, sizey=0.35, 
            xanchor="center", yanchor="middle",
            layer="above" # Nos aseguramos de que la imagen quede por encima del gráfico
        )
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450
    )
    return fig
# --- 6. MOSTRAR PUNTERO Y RULETA ---
st.markdown("<div class='puntero'>▼</div>", unsafe_allow_html=True)
espacio_ruleta = st.empty() 

if len(st.session_state.opciones) > 0:
    fig_inicial = dibujar_ruleta(st.session_state.opciones, st.session_state.rotacion_actual)
    espacio_ruleta.plotly_chart(fig_inicial, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("⚠️ Necesitas opciones para jugar.")

# --- 7. ESPACIO PARA GANADOR ---
espacio_ganador = st.empty()
if st.session_state.ganador:
    espacio_ganador.markdown(f"<div class='ganador-txt'>🎉 {st.session_state.ganador} 🎉</div>", unsafe_allow_html=True)
else:
    espacio_ganador.markdown("<div style='min-height: 80px;'></div>", unsafe_allow_html=True)

# --- 8. BOTONES Y LÓGICA DE GIRO ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    if not st.session_state.ganador:
        if st.button("🎰 ¡GIRAR LA RULETA!", type="primary", use_container_width=True):
            if len(st.session_state.opciones) < 2:
                st.error("⚠️ Necesitás al menos 2 opciones.")
            else:
                st.session_state.ganador = random.choice(st.session_state.opciones)
                indice_ganador = st.session_state.opciones.index(st.session_state.ganador)
                
                total_opciones = len(st.session_state.opciones)
                grados_por_opcion = 360 / total_opciones
                centro_del_ganador = (indice_ganador * grados_por_opcion) + (grados_por_opcion / 2)
                rotacion_objetivo = 360 - centro_del_ganador
                
                # ANIMACIÓN DE GIRO Y FRENADO MÁS LENTO Y DRAMÁTICO
                frames = 40  
                vueltas_extra = 6 * 360 
                
                for i in range(frames + 1):
                    progreso = i / frames
                    frenado_suave = 1 - (1 - progreso)**4 
                    rotacion_frame = (frenado_suave * (vueltas_extra + rotacion_objetivo))
                    
                    fig_frame = dibujar_ruleta(st.session_state.opciones, rotacion_frame % 360)
                    espacio_ruleta.plotly_chart(fig_frame, use_container_width=True, config={'displayModeBar': False})
                    time.sleep(0.01)
                
                st.session_state.rotacion_actual = rotacion_objetivo
                st.balloons()
                st.rerun()
    else:
        if st.button(f"🗑️ Eliminar '{st.session_state.ganador}' y seguir", type="primary", use_container_width=True):
            st.session_state.opciones.remove(st.session_state.ganador)
            st.session_state.ganador = None
            st.session_state.rotacion_actual = 0 
            st.rerun()
            
        if st.button("🔄 Mantenerlo y volver a girar", use_container_width=True, type="primary"):
            st.session_state.ganador = None
            st.rerun()