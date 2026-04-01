import tkinter as tk
from tkinter import ttk
import socket
import threading

# --- CONFIGURACIÓN ---
IP_ESP32 = "192.168.1.XX" 
PUERTO = 80

# --- CLASE DE DATOS ---
class DatosSensor:
    def __init__(self, valor):
        self.valor = valor

# --- LÓGICA DE RED ---
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conectar():
    try:
        sock.connect((IP_ESP32, PUERTO))
        print("Conectado al ESP32")
        threading.Thread(target=recibir_datos, daemon=True).start()
    except Exception as e:
        print("Error al conectar:", e)

def recibir_datos():
    # Convertimos el flujo de red en un formato de lectura por líneas
    archivo_red = sock.makefile('r')
    while True:
        try:
            # Lee exactamente hasta el salto de línea (\n)
            linea = archivo_red.readline()
            if not linea: 
                break # Si está vacío, se desconectó
            
            # Limpiamos espacios y procesamos
            valor_limpio = linea.strip()
            if valor_limpio:
                sensor = DatosSensor(int(valor_limpio))
                # Actualizar la interfaz
                progress['value'] = sensor.valor
                lbl_valor.config(text=f"Potenciómetro: {sensor.valor}")
                
        except ValueError:
            # Si llega basura ocasional, la ignoramos y el ciclo continúa
            pass
        except Exception as e:
            print("Desconectado del servidor:", e)
            break

# Agregamos manejo de errores al enviar para evitar que la app colapse si se cae la red
def led_on(): 
    try: sock.send(b'ON')
    except: print("Error enviando ON")

def led_off(): 
    try: sock.send(b'OFF')
    except: print("Error enviando OFF")

# --- INTERFAZ DE BOTONES ---
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=48, radius=18,
                 bg="#ff9800", activebg="#e68a00", fg="white", font=("Arial", 11, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, bd=0, highlightthickness=0,
                         relief="flat", bg=parent["bg"], cursor="hand2", **kwargs)
        self.command = command
        self.normal_color = bg
        self.hover_color = activebg
        self.fg = fg
        self.font = font
        self.radius = radius
        self.text = text

        self._draw_button(width, height)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def _draw_button(self, width, height):
        self.delete("all")
        self.create_rectangle(self.radius, 0, width - self.radius, height, fill=self.normal_color, outline="")
        self.create_rectangle(0, self.radius, width, height - self.radius, fill=self.normal_color, outline="")
        self.create_arc(0, 0, self.radius * 2, self.radius * 2, start=90, extent=90,
                        fill=self.normal_color, outline=self.normal_color)
        self.create_arc(width - self.radius * 2, 0, width, self.radius * 2, start=0, extent=90,
                        fill=self.normal_color, outline=self.normal_color)
        self.create_arc(0, height - self.radius * 2, self.radius * 2, height, start=180, extent=90,
                        fill=self.normal_color, outline=self.normal_color)
        self.create_arc(width - self.radius * 2, height - self.radius * 2, width, height,
                        start=270, extent=90, fill=self.normal_color, outline=self.normal_color)
        self.create_text(width / 2, height / 2, text=self.text, fill=self.fg, font=self.font)

    def _on_enter(self, event=None):
        self.normal_color = self.hover_color
        self._draw_button(self.winfo_reqwidth(), self.winfo_reqheight())

    def _on_leave(self, event=None):
        self.normal_color = "#ff9800"
        self._draw_button(self.winfo_reqwidth(), self.winfo_reqheight())

    def _on_click(self, event=None):
        if callable(self.command):
            self.command()


# --- INTERFAZ GRÁFICA ---
root = tk.Tk()
root.title("Control ESP32 - Instituto Cordillera")
root.geometry("540x320")
root.resizable(False, False)
root.configure(bg="#f7f3ef")
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

tk.Label(root, text="CONTROL DE DISPOSITIVO", font=("Arial", 14, "bold"), bg=root["bg"]).grid(row=0, column=0, columnspan=2, pady=14)

lbl_valor = tk.Label(root, text="Potenciómetro: 0", font=("Arial", 11), bg=root["bg"])
lbl_valor.grid(row=1, column=0, columnspan=2, pady=(0, 8))

progress = ttk.Progressbar(root, length=320, maximum=4095)
progress.grid(row=2, column=0, columnspan=2, padx=24, pady=12)

button_config = {
    "width": 220,
    "height": 52,
    "radius": 20,
    "bg": "#ff9800",
    "activebg": "#e68a00",
    "fg": "white",
    "font": ("Arial", 11, "bold"),
}

RoundedButton(root, text="Encender LED", command=led_on, **button_config).grid(row=3, column=0, padx=12, pady=12, sticky="ew")
RoundedButton(root, text="Apagar LED", command=led_off, **button_config).grid(row=3, column=1, padx=12, pady=12, sticky="ew")

threading.Thread(target=conectar, daemon=True).start()

root.mainloop()