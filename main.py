import tkinter as tk
import http.client
import json
from tkinter import ttk, messagebox

def obtener_token(usuario, password):
    """Realiza una solicitud HTTP para obtener un token de autenticación."""
    conn = http.client.HTTPSConnection("developmentserver.cl")
    payload = json.dumps({
        "data": {
            "usuario": usuario,
            "password": password
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    conn.request("POST", "/tickify/api/usuario/?op=jwtauth", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    
    try:
        respuesta_json = json.loads(data)  # Convertir la respuesta en JSON
        
        # Validamos si la API devolvió un token válido
        if respuesta_json.get("error") is None and "data" in respuesta_json and respuesta_json["data"]:
            return respuesta_json["data"]  # Retorna el token
        
        return None  # Retorna None si hubo un error o no hay token válido
    
    except json.JSONDecodeError:
        return None  # Manejo de error en caso de respuesta inválida


def obtener_usuario_session(token, usuario):
    """Obtiene la información del usuario autenticado usando un token JWT."""
    conn = http.client.HTTPSConnection("developmentserver.cl")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    conn.request("GET", f"/tickify/api/usuario/?where=usuario,{usuario}", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    try:
        respuesta_json = json.loads(data)  # Convertir la respuesta en JSON
        
        # Validamos si la API devolvió un token válido
        if respuesta_json.get("error") is None and "data" in respuesta_json and respuesta_json["data"]:
            return respuesta_json["data"]  # Retorna el token
        
        return None  # Retorna None si hubo un error o no hay token válido
    
    except json.JSONDecodeError:
        return None  # Manejo de error en caso de respuesta inválida


# --- Función para verificar el inicio de sesión ---
def verificar_login():
    usuario = entry_usuario.get()
    clave = entry_clave.get()
    
    token = obtener_token(usuario, clave)
    usuario_data = obtener_usuario_session(token, usuario)
    print("Usuario autenticado:", usuario_data)

    if token:
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        ventana_login.destroy()  # Cierra la ventana de login
        iniciar_aplicacion(token)  # Inicia la aplicación principal con el token
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


def cerrar_sesion():
    app.destroy()
    mostrar_login()

# --- Función para iniciar la aplicación principal ---
def iniciar_aplicacion(token):
    global app, entry_nombre, entry_departamento, combo_asignado, combo_incidente
    global text_descripcion, combo_prioridad, tree, label_descripcion

    print(token)

    app = tk.Tk()
    app.title("Tickify - Gestión de Tickets")
    app.geometry("600x600")
    app.config(bg="#f0f0f0")

    notebook = ttk.Notebook(app)
    notebook.pack(expand=True, fill="both")

    frame_formulario = tk.Frame(notebook, bg="#f0f0f0")
    frame_tabla = tk.Frame(notebook, bg="#f0f0f0")

    notebook.add(frame_formulario, text="Agregar Ticket")
    notebook.add(frame_tabla, text="Mis Tickets")

    # --- Formulario ---
    frame = tk.Frame(frame_formulario, bg="#f0f0f0")
    frame.pack(pady=20)

    tk.Label(frame, text="Nombre del Funcionario:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="w")
    entry_nombre = tk.Entry(frame, width=40, font=("Arial", 10))
    entry_nombre.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Asignado a:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="w")
    combo_asignado = ttk.Combobox(frame, values=[
        "Jorge Nicolas Berrios Cornejo",
        "Sergio Andrés Concha Llanos",
        "Juan Pablo Alvarez Avalos",
        "Elena Garrido Santibañez",
        "Daniel Bernardo Huerta Rojas",
        "Leonardo Antonio Martinez Vera"
    ], state="readonly", width=38, font=("Arial", 10))
    combo_asignado.grid(row=1, column=1, pady=5)
    combo_asignado.bind("<<ComboboxSelected>>", actualizar_departamentos)

    tk.Label(frame, text="Departamento:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=2, column=0, pady=5, sticky="w")
    entry_departamento = ttk.Combobox(frame, values=["Soporte Informático", "Desarrollo de sistemas"], state="readonly", width=38, font=("Arial", 10))
    entry_departamento.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Incidente:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5, sticky="w")
    combo_incidente = ttk.Combobox(frame, values=[
        "Activación de Office", "Atasco de Papel", "Impresión Defectuosa",
        "Formateo de Computador", "Recuperar Clave de HIS", "Computador no Enciende",
        "Instalación de Antivirus", "Otro"
    ], state="readonly", width=38, font=("Arial", 10))
    combo_incidente.grid(row=3, column=1, pady=5)
    combo_incidente.bind("<<ComboboxSelected>>", mostrar_descripcion)

    label_descripcion = tk.Label(frame, text="Descripción:", font=("Arial", 10, "bold"), bg="#f0f0f0")
    text_descripcion = tk.Text(frame, width=40, height=5, font=("Arial", 10))

    tk.Label(frame, text="Prioridad:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=4, column=0, pady=5, sticky="w")
    combo_prioridad = ttk.Combobox(frame, values=["Alta", "Media", "Baja"], state="readonly", width=38, font=("Arial", 10))
    combo_prioridad.grid(row=4, column=1, pady=5)

    button_enviar = tk.Button(frame_formulario, text="Enviar Ticket", command=enviar_ticket, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="flat", width=20, height=2)
    button_enviar.pack(pady=20)

    # --- Botón de Cerrar Sesión ---
    button_cerrar_sesion = tk.Button(app, text="Cerrar Sesión", command=cerrar_sesion, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_cerrar_sesion.pack(pady=10)

    # --- Tabla de tickets ---
    columns = ("Nombre del Funcionario", "Asignado a", "Departamento", "Incidente", "Prioridad", "Descripción")
    tree = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(expand=True, fill="both", pady=20)

    button_eliminar = tk.Button(frame_tabla, text="Eliminar Ticket", command=eliminar_ticket, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_eliminar.pack(pady=10)

    app.mainloop()

# --- Funciones para la gestión de tickets ---
def enviar_ticket():
    nombre = entry_nombre.get()
    departamento = entry_departamento.get()
    asignado_a = combo_asignado.get()
    incidente = combo_incidente.get()
    descripcion = text_descripcion.get("1.0", tk.END).strip()
    prioridad = combo_prioridad.get()

    if asignado_a == "Daniel Bernardo Huerta Rojas" and departamento != "Desarrollo de sistemas":
        messagebox.showwarning("Advertencia", "Daniel Bernardo Huerta Rojas solo puede ser asignado a Desarrollo de sistemas.")
        return

    if not nombre or not departamento or not asignado_a or not incidente or not prioridad or (incidente == "Otro" and not descripcion):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    tree.insert("", tk.END, values=(nombre, asignado_a, departamento, incidente, prioridad, descripcion))

    entry_nombre.delete(0, tk.END)
    entry_departamento.set("")
    combo_asignado.set("")
    combo_incidente.set("")
    text_descripcion.delete("1.0", tk.END)
    combo_prioridad.set("")

    messagebox.showinfo("Éxito", "Ticket enviado con Éxito")

def eliminar_ticket():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Seleccione un ticket para eliminar.")
        return
    tree.delete(selected_item)

def mostrar_descripcion(event):
    if combo_incidente.get() == "Otro":
        label_descripcion.grid(row=5, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=5, column=1, pady=5)
    else:
        label_descripcion.grid_forget()
        text_descripcion.grid_forget()

def actualizar_departamentos(event):
    asignado_a = combo_asignado.get()
    if asignado_a == "Daniel Bernardo Huerta Rojas":
        entry_departamento["values"] = ["Desarrollo de sistemas"]
        entry_departamento.set("Desarrollo de sistemas")

        combo_incidente["values"] = ["Otro"]
        combo_incidente.set("Otro")

        label_descripcion.grid(row=5, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=5, column=1, pady=5)
        
    else:

        label_descripcion.grid_forget()
        text_descripcion.grid_forget()
    
        departamento = ["Soporte Informático"]
        incidentes = [
            "Activación de Office", "Atasco de Papel", "Impresión Defectuosa",
            "Formateo de Computador", "Recuperar Clave de HIS", "Computador no Enciende",
            "Instalación de Antivirus", "Otro"
        ]

    # Actualizar los valores de los combobox
    entry_departamento["values"] = departamento
    entry_departamento.set("")

    combo_incidente["values"] = incidentes
    combo_incidente.set("")


# --- Función para mostrar el login nuevamente ---
def mostrar_login():
    global ventana_login, entry_usuario, entry_clave

    ventana_login = tk.Tk()
    ventana_login.title("Acceso Funcionarios a Ticket de Soporte")
    ventana_login.geometry("300x250")
    ventana_login.config(bg="#f0f0f0")

    tk.Label(ventana_login, text="Usuario:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
    entry_usuario = tk.Entry(ventana_login, width=30, font=("Arial", 10))
    entry_usuario.pack(pady=5)

    tk.Label(ventana_login, text="Contraseña:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
    entry_clave = tk.Entry(ventana_login, show="*", width=30, font=("Arial", 10))
    entry_clave.pack(pady=5)

    tk.Button(ventana_login, text="Iniciar Sesión", command=verificar_login, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="flat", width=15, height=2).pack(pady=20)

    ventana_login.mainloop()

# --- Iniciar el login ---
mostrar_login()
