import tkinter as tk
from tkinter import messagebox, Scrollbar
import nmap
import json
from softtek_llm.chatbot import Chatbot
from softtek_llm.models import OpenAI
from softtek_llm.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import subprocess

def confirmar_analisis():
    ip = entrada.get()
    if not ip:
        messagebox.showerror("Error", "Debes ingresar una dirección IP.")
    else:
        resultado = messagebox.askokcancel("Confirmación", "¿Estás seguro de que deseas analizar los puertos?")
        if resultado:
            # Obtener los puertos ingresados por el usuario o usar los predeterminados (1-65535)
            puertos = entrada_puertos.get() or '1-65535'
            analizar_puertos(ip, puertos)

def analizar_puertos(ip, puertos):
    scanner = nmap.PortScanner()
    reporte = scanner.scan(ip, puertos, arguments='-T4 -v -oN output.txt')
    cadena_json = json.dumps(reporte)
    generar_resumen(cadena_json)


def generar_resumen(reporte):
    load_dotenv()
    OPENAI_API_KEY = '6b25369971534252bbcee5e488ce59f1'
    if OPENAI_API_KEY is None:
        raise ValueError("OPENAI_API_KEY not found")

    OPENAI_API_BASE = "https://openaistkinno.openai.azure.com/"
    if OPENAI_API_BASE is None:
        raise ValueError("OPENAI_API_BASE not found")

    OPENAI_CHAT_MODEL_NAME = "InnovationGPT2"
    if OPENAI_CHAT_MODEL_NAME is None:
        raise ValueError("OPENAI_CHAT_MODEL_NAME not found")

    model = OpenAI(
        api_key=OPENAI_API_KEY,
        model_name=OPENAI_CHAT_MODEL_NAME,
        api_type="azure",
        api_base=OPENAI_API_BASE,
        verbose=False,
    )

    chatbot = Chatbot(
        model=model,
        description="You are a very helpful and polite chatbot",
        verbose=False,
    )
    response = chatbot.chat(
        prompt="Realiza un resumen ejecutivo de, " + reporte
    )
    mensaje = response.message.content

    # Mostrar el resultado en el widget de texto
    resultado_text.config(state=tk.NORMAL)
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, mensaje)
    resultado_text.config(state=tk.DISABLED)

    nombre_archivo = "Reporte.txt"
    with open(nombre_archivo, 'w') as archivo:
            archivo.write(mensaje)
     
ventana = tk.Tk()
ventana.title("Analizador de IP")

# Obtener el tamaño de la pantalla principal
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Configurar el tamaño de la ventana para que ocupe la mitad del ancho y alto de la pantalla
ancho_ventana = ancho_pantalla // 2
alto_ventana = alto_pantalla // 2
ventana.geometry(f"{ancho_ventana}x{alto_ventana}")

encabezado_label = tk.Label(ventana, text="Analizador de IP", font=("Arial", 24), fg="blue")
encabezado_label.pack(pady=20)

# Frame para agrupar etiqueta "IP:" y entrada
frame_ip = tk.Frame(ventana)
frame_ip.pack(pady=10)

# Etiqueta "IP:" centrada en el lado izquierdo
ip_label = tk.Label(frame_ip, text="IP:", font=("Arial", 18))
ip_label.pack(side=tk.LEFT, padx=10)

# Campo de entrada para la dirección IP
entrada = tk.Entry(frame_ip, font=("Arial", 18))
entrada.pack(side=tk.LEFT)

# Frame para agrupar etiqueta "Puertos:" y entrada de puertos
frame_puertos = tk.Frame(ventana)
frame_puertos.pack(pady=10)

# Etiqueta "Puertos:" centrada en el lado izquierdo
puertos_label = tk.Label(frame_puertos, text="Puertos:", font=("Arial", 18))
puertos_label.pack(side=tk.LEFT, padx=10)

# Campo de entrada para los puertos (opcional)
entrada_puertos = tk.Entry(frame_puertos, font=("Arial", 18))
entrada_puertos.pack(side=tk.LEFT)

boton_analizar = tk.Button(ventana, text="Analizar Puertos", command=confirmar_analisis, font=("Arial", 18))
boton_analizar.pack()

# Widget de texto para mostrar el resultado
resultado_text = tk.Text(ventana, font=("Arial", 18), wrap=tk.WORD)
resultado_text.pack(fill=tk.BOTH, expand=True)

# Barra de desplazamiento para el widget de texto
scrollbar = Scrollbar(resultado_text)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
resultado_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=resultado_text.yview)

# Configurar el enfoque inicial en el campo de entrada
entrada.focus()

# Configurar el tamaño de las filas y columnas de la cuadrícula para que el widget de texto se expanda correctamente
ventana.grid_rowconfigure(3, weight=1)
ventana.columnconfigure(1, weight=1)

ventana.mainloop()