import tkinter as tk
from tkinter import ttk, messagebox

def enviar_ticket():
    nombre = entry_nombre.get()
    departamento = entry_departamento.get()
    asignado_a = combo_asignado.get()
    incidente = combo_incidente.get()
    descripcion = text_descripcion.get("1.0", tk.END).strip()
    prioridad = combo_prioridad.get()
    
    # Validación especial para Daniel Bernardo Huerta Rojas
    if asignado_a == "Daniel Bernardo Huerta Rojas" and departamento != "Desarrollo de sistemas":
        messagebox.showwarning("Advertencia", "Daniel Bernardo Huerta Rojas solo puede ser asignado a Desarrollo de sistemas.")
        return

    if not nombre or not departamento or not asignado_a or not incidente or not prioridad or (incidente == "Otro" and not descripcion):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return
    
    messagebox.showinfo("Éxito", f"Ticket enviado:\nNombre del Funcionario: {nombre}\nAsignado a: {asignado_a}\nDepartamento: {departamento}\nIncidente: {incidente}\nPrioridad: {prioridad}\nDescripción: {descripcion}")
    
    entry_nombre.delete(0, tk.END)
    entry_departamento.set("")  # Reset combobox
    combo_asignado.set("")  # Reset combobox
    combo_incidente.set("")  # Reset combobox
    text_descripcion.delete("1.0", tk.END)
    combo_prioridad.set("")  # Reset combobox

def mostrar_descripcion(event):
    # Solo mostrar el campo de descripción si el incidente seleccionado es "Otro"
    if combo_incidente.get() == "Otro":
        label_descripcion.grid(row=5, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=5, column=1, pady=5)
    else:
        label_descripcion.grid_forget()
        text_descripcion.grid_forget()

app = tk.Tk()
app.title("Formulario de Ticket de Soporte - Tickify")
app.geometry("500x600")
app.config(bg="#f0f0f0")  # Fondo gris claro

# Usar Frame para organizar mejor los widgets
frame = tk.Frame(app, bg="#f0f0f0")
frame.pack(pady=20)

# Etiquetas y campos de entrada
tk.Label(frame, text="Nombre del Funcionario:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="w")
entry_nombre = tk.Entry(frame, width=40, font=("Arial", 10))
entry_nombre.grid(row=0, column=1, pady=5)

# Nuevo combobox para asignado a
tk.Label(frame, text="Asignado a:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="w")
combo_asignado = ttk.Combobox(frame, values=[
    "Jorge Nicolas Berrios Cornejo",
    "Sergio Andrés Concha Llanos",
    "Juan Pablo Alvarez Avalos",
    "Elena Garrido Santibañez",
    "Cagny Nisse Gonzalez Castañeda",
    "Daniel Bernardo Huerta Rojas",
    "Leonardo Antonio Martinez Vera"
], state="readonly", width=38, font=("Arial", 10))
combo_asignado.grid(row=1, column=1, pady=5)

tk.Label(frame, text="Departamento:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=2, column=0, pady=5, sticky="w")
entry_departamento = ttk.Combobox(frame, values=["Soporte Informático", "Desarrollo de sistemas"], state="readonly", width=38, font=("Arial", 10))
entry_departamento.grid(row=2, column=1, pady=5)

tk.Label(frame, text="Incidente:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5, sticky="w")
combo_incidente = ttk.Combobox(frame, values=[
    "Activación de Office", 
    "Atasco de Papel",
    "Impresión defectuosa",
    "Formateo de Computador",
    "Recuperar Clave de HIS",
    "Computador no Enciende",
    "Instalación de Antivirus",
    "Otro"
], state="readonly", width=38, font=("Arial", 10))
combo_incidente.grid(row=3, column=1, pady=5)
combo_incidente.bind("<<ComboboxSelected>>", mostrar_descripcion)  # Controlador para mostrar la descripción

# Etiqueta y campo de texto de descripción (inicialmente ocultos)
label_descripcion = tk.Label(frame, text="Descripción del Problema:", font=("Arial", 10, "bold"), bg="#f0f0f0")
text_descripcion = tk.Text(frame, width=40, height=5, font=("Arial", 10))

tk.Label(frame, text="Prioridad:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=4, column=0, pady=5, sticky="w")
combo_prioridad = ttk.Combobox(frame, values=["Alta", "Media", "Baja"], state="readonly", width=38, font=("Arial", 10))
combo_prioridad.grid(row=4, column=1, pady=5)

# Botón para enviar
button_enviar = tk.Button(app, text="Enviar Ticket", command=enviar_ticket, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="flat", width=20, height=2)
button_enviar.pack(pady=20)

app.mainloop()
