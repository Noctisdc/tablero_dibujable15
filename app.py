import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    
    st.subheader("Herramientas de dibujo")
    # Añadir 5 colores para el tablero
    color_opcion = st.selectbox(
        "Selecciona el color del trazo:",
        ("Negro", "Rojo", "Azul", "Verde", "Amarillo")
    )
    
    diccionario_colores = {
        "Negro": "#000000",
        "Rojo": "#FF0000",
        "Azul": "#0000FF",
        "Verde": "#008000",
        "Amarillo": "#FFFF00"
    }
    stroke_color = diccionario_colores[color_opcion]
    
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")

drawing_mode = "freedraw"
bg_color = '#FFFFFF'

# Create a canvas component (Dimensiones más grandes)
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=500, # Aumentado de 300 a 500
    width=700,  # Aumentado de 400 a 700
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave', type="password") # Cambiado a tipo password por seguridad

# Manejo seguro de la API KEY
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)
else:
    api_key = None

analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando y creando historia..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
            
        # Modificación del prompt para pedir una historia básica
        prompt_text = "Analiza la imagen adjunta y descríbela en español. Luego, basándote estrictamente en lo que ves en el dibujo, inventa y escribe una pequeña historia básica."
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=800, # Aumenté los tokens para que alcance a escribir la historia completa
              )
            
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            
            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content 
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
