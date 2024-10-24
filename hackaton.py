import customtkinter
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import re
import os
import threading
import google.generativeai as genai


genai.configure(api_key=os.getenv("tu clave"))

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Hola, estamos realizando una prueba a niños de tercer grado y necesitamos tu ayuda para analizar"
                       " los resultados, las preguntas tienen su categoria para conocer en que area los estudiante "
                       "tienen peor rendimiento, esta es la prueba:\nPrueba de Matemáticas para Tercer Grado\n1. "
                       "utilizando este formato Conteo:\n 2/2 correctas (6 y 9)"
                        "\nNumeración: 2/2 correctas (8 y 5 manzanas)"
                        "\nComprensión del sistema numérico: 2/2 correctas (30 y Cuarenta y dos)"
                        "\nOperaciones lógicas: 2/2 correctas (8 y 7)"
                        "\nOperaciones: 3/3 correctas (8, 3 y 15)"
                        "\nEstimación del tamaño: 2/2 correctas (5 manzanas y 5 plátanos)"
                        "\nComprensión del sistema numérico: 1/1 correcta (1)"
                        "\nOperaciones: 1/1 correcta (24)"
                       "Conteo\n¿Cuál es el siguiente número en la secuencia? 3, 4, 5, __\nA) 6\nB) 7\nC) 8\nD) 9\n\n2."
                       " Conteo\n¿Cuántos números hay entre 10 y 20? (sin contar el 10 y el 20)\nA) 8\nB) 9\nC) 10\nD)"
                       " 11\n\n3. Numeración\nSi tienes 5 manzanas y 3 peras, ¿cuántas frutas tienes en total?\nA) 5\nB)"
                       " 6\nC) 7\nD) 8\n\n4. Numeración\n¿Cuál de las siguientes opciones muestra la cantidad correcta "
                       "de objetos?\nA) 🍏🍏🍏🍏🍏 (5 manzanas)\nB) 🍌🍌🍌🍌 (4 plátanos)\nC) 🍉🍉🍉🍉🍉🍉 (6 sandías)"
                       "\nD) 🍓🍓🍓 (3 fresas)\n\n5. Comprensión del sistema numérico\n¿Cuál es el número mayor?"
                       "\nA) 25\nB) 15\nC) 30\nD) 20\n\n6. Comprensión del sistema numérico\nEscribe el número 42 en palabras:"
                       "\nA) Cuarenta y dos\nB) Cuarenta\nC) Dos\nD) Cuarenta y uno\n\n7. Operaciones lógicas\nCompleta"
                       " la serie: 2, 4, 6, __\nA) 7\nB) 8\nC) 9\nD) 10\n\n8. Operaciones lógicas\n¿Cuál de las siguientes "
                       "opciones continúa la serie? 1, 3, 5, __\nA) 7\nB) 8\nC) 6\nD) 9\n\n9. Operaciones\n¿Cuánto es 15 - 7?"
                       "\nA) 8\nB) 7\nC) 6\nD) 9\n\n10. Operaciones\nSi tienes 4 galletas y comes 1,"
                       " ¿cuántas galletas te quedan?\nA) 2\nB) 3\nC) 4\nD) 5\n\n11. Operaciones\n¿Cuánto es 3 x 5?"
                       "\nA) 8\nB) 12\nC) 15\nD) 18\n\n12. Estimación del tamaño\n¿Cuál grupo tiene más objetos?\nA) "
                       "🍏🍏🍏 (3 manzanas)\nB) 🍌🍌🍌🍌🍌 (5 plátanos)\nC) 🍉🍉🍉 (3 sandías)\nD) 🍓🍓 (2 fresas)"
                       "\n\n13. Estimación del tamaño\nSi tienes 10 canicas y tu amigo tiene 7, ¿quién tiene más?\nA)"
                       " Tú\nB) Tu amigo\nC) Ambos tienen la misma cantidad\nD) No se puede saber\n\n14. Comprensión"
                       " del sistema numérico\n¿Cuál de los siguientes números es menor?\nA) 12\nB) 9\nC) 15\nD) 10\n"
                       "\n15. Operaciones\n¿Cuánto es 20 + 4?\nA) 23\nB) 24\nC) 25\nD) 26"
                       "cuando hagas el analisis dividelo en 3 secciones: analisis, conclusiones"
                       " y otros aspectos a tomar en cuenta(este le puedes cambiar el nombre)",
)


history = []

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

def procesar_csv():
    ruta_csv = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not ruta_csv:
        return

    try:
        # Leer archivo CSV con codificación 'utf-8'
        df = pd.read_csv(ruta_csv, encoding='utf-8')
        respuestas_por_persona = df.iloc[:, 1:]

        prompt = "Resultados de la prueba de matemáticas:\n"
        for index, fila in respuestas_por_persona.iterrows():
            prompt += f"\nPersona {index + 1} - Respuestas:\n"
            for respuesta in fila:
                respuesta = str(respuesta).strip()
                if re.match(r'^[\w\.-]+@[\w\.-]+$', respuesta):
                    continue
                if respuesta == "nan":
                    continue
                prompt += f"  {respuesta}\n"

        text_area.configure(state='normal')
        text_area.delete(1.0, "end")
        text_area.insert("end", prompt)
        text_area.configure(state='disabled')

        enviar_a_ia(prompt)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al procesar el archivo CSV: {str(e)}")

def enviar_a_ia(prompt):
    def process_input():
        genai.configure(api_key="tu clave")
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(prompt)
        model_response = response.text
        update_chat_box(prompt, model_response)
        history.append({"role": "user", "parts": [prompt]})
        history.append({"role": "model", "parts": [model_response]})

    thread = threading.Thread(target=process_input)
    thread.start()

def update_chat_box(user_input, model_response):
    chat_box.configure(state="normal")
    chat_box.insert("end", f"User: {user_input}\nBot: {model_response}\n\n")
    chat_box.configure(state="disabled")

root = customtkinter.CTk()
root.title("Evaluador de Respuestas de Matemáticas")
root.geometry("500x600")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

header = customtkinter.CTkLabel(master=frame, text="Evaluador de Respuestas de Matemáticas", font=("Roboto", 18, "bold"))
header.pack(pady=12, padx=14)

text_area = customtkinter.CTkTextbox(master=frame, wrap="word", height=150)
text_area.pack(fill='x', padx=20, pady=10)
text_area.configure(state='disabled')  # Deshabilitar edición al inicio

chat_box = customtkinter.CTkTextbox(master=frame, height=250, state="disabled", wrap="word")
chat_box.pack(fill='x', padx=20, pady=10)

btn_cargar = customtkinter.CTkButton(master=frame, text="Cargar archivo CSV", command=procesar_csv)
btn_cargar.pack(pady=12, padx=10)

root.mainloop()
