import base64
import io
from openai import OpenAI
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(
    page_title="Cyber Art Studio | Generador AI", page_icon="🎨", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (Temática Cyberpunk / Neón) ---
st.markdown(
    """
    <style>
    .main { background-color: #090D16; color: #F8FAFC; }
    .stSidebar { background-color: #111827 !important; }
    .hero-banner {
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 50%, #8B5CF6 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(6,182,212,0.3);
    }
    .card-box {
        background-color: #111827;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1F2937;
        margin-bottom: 15px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
        color: white; font-weight: bold; border-radius: 8px; border: none;
        padding: 10px 20px; width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0891B2 0%, #2563EB 100%);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: CONFIGURACIÓN Y PINCELES ---
st.sidebar.markdown("### ⚡ Terminal & API Key")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key:",
    type="password",
    placeholder="sk-...",
    help="Ingresa tu clave para activar el motor generativo.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖌️ Controles de Trazo")
stroke_width = st.sidebar.slider("Grosor del pincel", 2, 30, 8)
stroke_color = st.sidebar.color_picker(
    "Color del láser", "#06B6D4"
)  # Neón cian por defecto

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Instrucciones del Sistema")
st.sidebar.info(
    "1. Configura tu API Key.\n2. Dibuja un concepto o boceto en el panel"
    " central.\n3. Selecciona el estilo de renderizado.\n4. Ejecuta el núcleo"
    " neural para generar la obra."
)

# --- CONTENIDO PRINCIPAL ---
st.markdown(
    """
    <div class="hero-banner">
        <h1 style="margin:0; font-size: 2.2rem;">⚡ Cyber Art Studio: Neural Canvas 🌌</h1>
        <p style="margin-top: 8px; font-size: 1rem; opacity: 0.9;">Transforma tus trazos y bocetos geométricos en renderizados de arte digital mediante Inteligencia Artificial.</p>
    </div>
""",
    unsafe_allow_html=True,
)

col_canvas, col_control = st.columns([1.1, 1.2])

with col_canvas:
  st.markdown("### 📐 Lienzo Cuántico (Boceto)")

  # Lienzo interactivo optimizado
  canvas_result = st_canvas(
      fill_color="#000000",
      stroke_width=stroke_width,
      stroke_color=stroke_color,
      background_color="#000000",
      width=350,
      height=350,
      drawing_mode="freedraw",
      update_streamlit=True,
      return_image_data=True,
      key="cyber_canvas",
  )
  st.markdown(
      "<p style='color: #94A3B8; font-size: 0.85rem;'>💡 <i>Dibuja cualquier"
      " estructura, paisaje o personaje para la síntesis visual.</i></p>",
      unsafe_allow_html=True,
  )

with col_control:
  st.markdown("### ⚙️ Motor de Generación Neural")

  estilo_arte = st.selectbox(
      "Estilo de Renderizado:",
      [
          "Cyberpunk / Neón Futurista",
          "Fotorrealismo Cinemático",
          "Ilustración Concept Art",
          "Pintura al Óleo Clásica",
      ],
  )
  prompt_extra = st.text_input(
      "Detalles adicionales (Opcional):",
      placeholder="Ej: Iluminación nocturna, atmósfera lluviosa...",
  )

  generar_btn = st.button("🚀 Iniciar Síntesis Neural")

  if not openai_api_key:
    st.markdown(
        '<div class="card-box" style="border-left: 4px solid #F59E0B; color:'
        ' #FBBF24;">⚠️ <b>Advertencia:</b> Debes ingresar tu API Key en la barra'
        ' lateral para habilitar la generación de imágenes.</div>',
        unsafe_allow_html=True,
    )

# --- PROCESAMIENTO Y GENERACIÓN CON IA ---
if generar_btn:
  if not openai_api_key:
    st.error(
        "Por favor ingresa tu API Key de OpenAI para continuar con la"
        " síntesis."
    )
  elif canvas_result.image_data is None:
    st.warning("El lienzo está vacío. Dibuja algo antes de ejecutar la síntesis.")
  else:
    with st.spinner(
        "Procesando geometría del boceto y sintetizando imagen con IA..."
    ):
      try:
        client = OpenAI(api_key=openai_api_key)

        # Convertir dibujo del lienzo a imagen PIL
        img_array = canvas_result.image_data.astype("uint8")
        img_pil = Image.fromarray(img_array).convert("RGB")

        buffered = io.BytesIO()
        img_pil.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        # Usar GPT-4o para interpretar el dibujo y generar un prompt descriptivo detallado
        base64_image = base64.b64encode(img_bytes).decode("utf-8")

        vision_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analiza este boceto hecho a mano y describe"
                                f" detalladamente un prompt para generar una"
                                f" obra de arte digital con estilo '{estilo_arte}'"
                                f" basado en estas formas. Detalles adicionales"
                                f" del usuario: {prompt_extra}"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        generated_prompt = vision_response.choices[0].message.content

        # Llamar a DALL-E 3 para generar la imagen final basada en la interpretación del boceto
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=(
                f"High quality digital art, style of {estilo_arte}, based on"
                f" this concept: {generated_prompt}"
            ),
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = image_response.data[0].url

        st.markdown("---")
        st.markdown("### ✨ Resultado de la Síntesis Neural")
        st.image(
            image_url,
            caption=(
                f"Obra Generada - Estilo: {estilo_arte}"
            ),
            use_container_width=True,
        )
        st.success("¡Obra sintetizada con éxito por el núcleo neural!")

      except Exception as e:
        st.error(
            f"Ocurrió un error al procesar la solicitud con la API de OpenAI: {e}"
        )
