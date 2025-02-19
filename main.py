import tkinter as tk
import http.client
import json
import bcrypt
import smtplib
import ssl
from email.message import EmailMessage
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

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

#=================== Enviar Correo ==========================#
def send_email(to_email, subject, body, smtp_server, smtp_port, username, password, cc_email=None, bcc_email=None):
    msg = EmailMessage()
    msg.set_content(body, subtype="html")
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = to_email

    if cc_email:
        msg["Cc"] = cc_email  # Destinatario en copia

    # Lista de destinatarios (To + CC + BCC)
    recipients = [to_email]
    if cc_email:
        recipients.append(cc_email)
    if bcc_email:
        recipients.append(bcc_email)  # BCC no se muestra en los correos


    # Conexión segura con SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(username, password)
        server.send_message(msg, from_addr=username, to_addrs=recipients)

    print("📨 Correo enviado exitosamente!")

#=================== Obtener Datos usuario de la sessión ==========================#
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


#=================== Obtener Datos usuario tabla soporte ==========================#
def obtener_datos_tabla_usuario(token, usuario_session_data):
    """Obtiene la información del usuario autenticado usando un token JWT."""
    
    conn = http.client.HTTPSConnection("developmentserver.cl")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    conn.request("GET", f"/tickify/api/soporte/?where=usuario,{usuario_session_data},eq&where[]=status,Ingresado,eq", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    try:
        respuesta_json = json.loads(data)  # Convertir la respuesta en JSON
        
        # Validamos si la API devolvió un token válido
        if respuesta_json.get("error") is None and "data" in respuesta_json and respuesta_json["data"]:
            return respuesta_json["data"]  # Retorna el token
        
        return None  # Retorna None si hubo un error o no hay token válido
    
    except json.JSONDecodeError:
        return None  # Manejo de
    
#=================== Cargar Datos en la Grilla ==========================#
def cargar_datos_en_grilla(tree, token, usuario_session_data):
    """Carga los datos en la grilla (Treeview)."""
    tree.delete(*tree.get_children())  # Limpiar la tabla antes de insertar nuevos datos
    
    datos = obtener_datos_tabla_usuario(token, usuario_session_data)

    for item in datos:

        fecha_formateada = (
            datetime.strptime(item.get("fecha", ""), "%Y-%m-%d").strftime("%d/%m/%Y") 
            if item.get("fecha", "") else ""
        )

        tree.insert("", "end", values=(
            item.get("id_soporte", ""),
            item.get("cliente", ""),
            fecha_formateada,  # Fecha en formato d-m-Y
            item.get("designado_a", ""),
            item.get("area", ""),
            item.get("categoria", ""),
            item.get("prioridad", ""),
            item.get("status", "")
        ))

#=================== Registrar Usuario ==========================#
def registrar_usuario():
    nombre = entry_nombre.get()
    correo = entry_correo.get()
    usuario = entry_usuario_reg.get()
    clave = entry_clave_reg.get()
    token = obtener_token("admin", "123")

    if not (nombre and correo and usuario and clave):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), salt).decode('utf-8')

    conn = http.client.HTTPSConnection("developmentserver.cl")
    payload = json.dumps({
        "data": {
            "nombre": nombre,
            "email": correo,
            "usuario": usuario,
            "password": hashed_password,
            "idrol": "1",
            "estatus": "1"
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # Enviar solicitud POST
    conn.request("POST", "/tickify/api/usuario", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # Mostrar respuesta de la API
    print("Respuesta de la API:", data.decode("utf-8"))

    messagebox.showinfo("Éxito", f"Registrando usuario: {nombre}, {correo}, {usuario}")


#============= Función para verificar el inicio de sesión =============#
def verificar_login():
    usuario = entry_usuario.get()
    clave = entry_clave.get()
    
    token = obtener_token(usuario, clave)
    usuario_session_data = obtener_usuario_session(token, usuario)

    if token:
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        ventana_login.destroy()  # Cierra la ventana de login
        iniciar_aplicacion(token, usuario_session_data)  # Inicia la aplicación principal con el token
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


def cerrar_sesion():
    app.destroy()
    mostrar_login()

#=============== Función para iniciar la aplicación principal ====================#
def iniciar_aplicacion(token, usuario_session_data):
    global app, entry_nombre, entry_departamento, combo_asignado, combo_incidente
    global text_descripcion, combo_prioridad, tree, label_descripcion

    app = tk.Tk()
    app.title("Tickify - Gestión de Tickets - Versión 1.0")
    app.geometry("600x600")
    app.config(bg="#f0f0f0")

    # Cargar imagen
    try:
        imagen_original = Image.open("logo.png")
        imagen_resized = imagen_original.resize((390, 136))
        imagen = ImageTk.PhotoImage(imagen_resized)

        label_imagen = tk.Label(app, image=imagen, bg="#f0f0f0")
        label_imagen.image = imagen  # Evita eliminación por recolector de basura
        label_imagen.pack(pady=10)
    except Exception as e:
        print(f"Error cargando la imagen: {e}")

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
    
    
    if isinstance(usuario_session_data, list) and usuario_session_data:
        datos_usuario = usuario_session_data[0]  # Extraer el primer elemento (diccionario)
        nombre_usuario = datos_usuario.get("nombre", "")  # Obtener el nombre del usuario
        usuario_usuario = datos_usuario.get("usuario", "")  # Obtener el usuario del usuario
    else:
        nombre_usuario = ""

    entry_nombre.insert(0, nombre_usuario)

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
    entry_departamento = ttk.Combobox(frame, values=["Soporte Informática", "Desarrollo de Sistemas"], state="readonly", width=38, font=("Arial", 10))
    entry_departamento.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Incidente:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5, sticky="w")
    combo_incidente = ttk.Combobox(frame, values=[
        "Instalación de Office",
        "Instalación de Antivirus",
        "Formateo de PC",
        "Activación de Office",
        "Cambio de Toner",
        "Atasco de Papel", 
        "Recuperación de Clave de HIS",
        "Impresión Defectuosa",
        "Reportar Impresora Defectuosa",
        "Otro"
    ], state="readonly", width=38, font=("Arial", 10))
    combo_incidente.grid(row=3, column=1, pady=5)
    combo_incidente.bind("<<ComboboxSelected>>", mostrar_descripcion)

    label_descripcion = tk.Label(frame, text="Descripción:", font=("Arial", 10, "bold"), bg="#f0f0f0")
    text_descripcion = tk.Text(frame, width=40, height=5, font=("Arial", 10))

    tk.Label(frame, text="Prioridad:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=4, column=0, pady=5, sticky="w")
    combo_prioridad = ttk.Combobox(frame, values=["Alta", "Media", "Baja"], state="readonly", width=38, font=("Arial", 10))
    combo_prioridad.grid(row=4, column=1, pady=5)

    button_enviar = tk.Button(frame_formulario, text="Enviar Ticket", command=lambda: enviar_ticket(token), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="flat", width=20, height=2)
    button_enviar.pack(pady=20)

    # --- Botón de Cerrar Sesión ---
    button_cerrar_sesion = tk.Button(app, text="Cerrar Sesión", command=cerrar_sesion, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_cerrar_sesion.pack(pady=10)

    # --- Tabla de tickets ---
    columns = ("N°Ticket", "Nombre del Funcionario", "Fecha", "Asignado a", "Departamento", "Incidente", "Prioridad", "Status", "Descripción")
    tree = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=10)

    for col in columns:
        tree.column(col, anchor="center")  # Centra los valores de la columna
        tree.heading(col, anchor="center")
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(expand=True, fill="both", pady=20)

    # Cargar datos en la grilla
    cargar_datos_en_grilla(tree, token, usuario_usuario)

    button_eliminar = tk.Button(frame_tabla, text="Eliminar Ticket", command=eliminar_ticket, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_eliminar.pack(pady=10)

    app.mainloop()

#================= Funciones para la gestión de tickets ================#
def enviar_ticket(token):
    """Envía un ticket a la API."""
    nombre = entry_nombre.get()
    departamento = entry_departamento.get()
    asignado_a = combo_asignado.get()
    incidente = combo_incidente.get()
    descripcion = text_descripcion.get("1.0", tk.END).strip() or "Sin Descripción"
    prioridad = combo_prioridad.get()

    #token = obtener_token("admin", "123")

    fecha_creacion = datetime.now().strftime("%Y-%m-%d")

    # Validaciones antes de enviar
    if asignado_a == "Daniel Bernardo Huerta Rojas" and departamento != "Desarrollo de Sistemas":
        messagebox.showwarning("Advertencia", "Daniel Bernardo Huerta Rojas solo puede ser asignado a Desarrollo de Sistemas.")
        return

    if not nombre or not departamento or not asignado_a or not incidente or not prioridad or (incidente == "Otro" and not descripcion):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    # Crear conexión con la API
   
    datos_ticket = json.dumps({
        "data": {
            "cliente": nombre,
            "fecha": fecha_creacion,
            "area": departamento,
            "designado_a": asignado_a,
            "categoria": incidente,
            "asunto": descripcion,
            "prioridad": prioridad,
            "status": "Ingresado"
        }
    })
    
    conn = http.client.HTTPSConnection("developmentserver.cl")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # Enviar solicitud POST a la API
    conn.request("POST", "/tickify/api/soporte", body=json.dumps(datos_ticket), headers=headers)
    response = conn.getresponse()

    # Estructura del correo en HTML
    email_body = f"""
    <html>
    <body>
        <h2>Nuevo Ticket Registrado</h2>
        <p><strong>Nombre del Funcionario:</strong> {nombre}</p>
        <p><strong>Fecha:</strong> {fecha_creacion}</p>
        <p><strong>Departamento:</strong> {departamento}</p>
        <p><strong>Asignado a:</strong> {asignado_a}</p>
        <p><strong>Incidente:</strong> {incidente}</p>
        <p><strong>Prioridad:</strong> {prioridad}</p>
        <p><strong>Descripción:</strong></p>
        <p>{descripcion}</p>
        <p><strong>Estado:</strong> Ingresado</p>
    </body>
    </html>
    """

    send_email(
        to_email="daniel.telematico@gmail.com",
        cc_email="soportemeli@gmail.com",
        bcc_email="",
        subject=f"Nuevo Ticket Registrado - {incidente}",
        body=email_body,
        smtp_server="smtp.gmail.com",
        smtp_port=465,
        username="daniel.telematico@gmail.com",
        password="zdkbgrxsnjmyyzrj"
    )

    messagebox.showinfo("Éxito", "Ticket registrado con éxito, enviaremos un técnico para que resuelva su problema a la brevedad.")

    cargar_datos_en_grilla(tree, token, nombre)

    # Limpiar los campos después del registro
    entry_departamento.set("")
    combo_asignado.set("")
    combo_incidente.set("")
    text_descripcion.delete("1.0", tk.END)
    combo_prioridad.set("")

#=========== Eliminar Ticket ===============#
def eliminar_ticket():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Seleccione un ticket para eliminar.")
        return
    messagebox.showinfo("Éxito", "Ticket Eliminado con éxito.")
    tree.delete(selected_item)

#============= Mostrar Descripcion ==================#
def mostrar_descripcion(event):
    if combo_incidente.get() == "Otro":
        label_descripcion.grid(row=5, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=5, column=1, pady=5)
    else:
        label_descripcion.grid_forget()
        text_descripcion.grid_forget()

#============= Actualizar Departamentos ==============#
def actualizar_departamentos(event):
    asignado_a = combo_asignado.get()
    if asignado_a == "Daniel Bernardo Huerta Rojas":
        entry_departamento["values"] = ["Desarrollo de Sistemas"]
        entry_departamento.set("Desarrollo de Sistemas")

        combo_incidente["values"] = ["Otro"]
        combo_incidente.set("Otro")

        label_descripcion.grid(row=5, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=5, column=1, pady=5)
        
    else:

        label_descripcion.grid_forget()
        text_descripcion.grid_forget()
    
        departamento = ["Soporte Informática"]
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

#============ Función para mostrar el login nuevamente ==============#
def mostrar_login():
    global ventana_login, entry_usuario, entry_clave
    global entry_nombre, entry_correo, entry_usuario_reg, entry_clave_reg

    ventana_login = tk.Tk()
    ventana_login.title("Tickify - Acceso Funcionarios a Ticket de Soporte - Versión 1.0")
    ventana_login.geometry("600x500")
    ventana_login.config(bg="#f0f0f0")

    # Cargar imagen
    try:
        imagen_original = Image.open("logo.png")
        imagen_resized = imagen_original.resize((390, 136))
        imagen = ImageTk.PhotoImage(imagen_resized)

        label_imagen = tk.Label(ventana_login, image=imagen)
        label_imagen.image = imagen  # Evita eliminación por recolector de basura
        label_imagen.pack(pady=20)
    except Exception as e:
        print(f"Error cargando la imagen: {e}")

    # Notebook (Pestañas)
    notebook = ttk.Notebook(ventana_login)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    # --- Pestañas ---
    frame_login = tk.Frame(notebook, bg="#f0f0f0")
    frame_registro = tk.Frame(notebook, bg="#f0f0f0")
    frame_guia = tk.Frame(notebook, bg="#f0f0f0")

    notebook.add(frame_login, text="Acceso Funcionarios")
    notebook.add(frame_registro, text="Registro Funcionarios")
    notebook.add(frame_guia, text="Guía de Uso")

    # ==================== LOGIN ====================
    frame_login_form = tk.Frame(frame_login, bg="#f0f0f0")
    frame_login_form.pack(pady=20)

    tk.Label(frame_login_form, text="Usuario:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5)
    entry_usuario = tk.Entry(frame_login_form, width=30, font=("Arial", 10))
    entry_usuario.grid(row=0, column=1, pady=5)

    tk.Label(frame_login_form, text="Contraseña:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5)
    entry_clave = tk.Entry(frame_login_form, show="*", width=30, font=("Arial", 10))
    entry_clave.grid(row=1, column=1, pady=5)

    tk.Button(frame_login_form, text="Iniciar Sesión", command=verificar_login, font=("Arial", 12, "bold"),
              bg="#4CAF50", fg="white", relief="flat", width=15, height=2).grid(row=2, column=0, columnspan=2, pady=20)

    # ==================== REGISTRO ====================
    frame_registro_form = tk.Frame(frame_registro, bg="#f0f0f0")
    frame_registro_form.pack(pady=20)

    tk.Label(frame_registro_form, text="Nombre del Funcionario:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5)
    entry_nombre = tk.Entry(frame_registro_form, width=30, font=("Arial", 10))
    entry_nombre.grid(row=0, column=1, pady=5)

    tk.Label(frame_registro_form, text="Correo electrónico:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5)
    entry_correo = tk.Entry(frame_registro_form, width=30, font=("Arial", 10))
    entry_correo.grid(row=1, column=1, pady=5)

    tk.Label(frame_registro_form, text="Usuario:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=2, column=0, pady=5)
    entry_usuario_reg = tk.Entry(frame_registro_form, width=30, font=("Arial", 10))
    entry_usuario_reg.grid(row=2, column=1, pady=5)

    tk.Label(frame_registro_form, text="Contraseña:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5)
    entry_clave_reg = tk.Entry(frame_registro_form, show="*", width=30, font=("Arial", 10))
    entry_clave_reg.grid(row=3, column=1, pady=5)

    tk.Button(frame_registro_form, text="Registrar", command=registrar_usuario, font=("Arial", 12, "bold"),
              bg="#008CBA", fg="white", relief="flat", width=15, height=2).grid(row=5, column=0, columnspan=2, pady=20)

     # ==================== GUÍA DE USO ====================
    label_guia = tk.Label(frame_guia, text="Guía de Uso", font=("Arial", 14, "bold"), bg="#f0f0f0")
    label_guia.pack(pady=10)

    texto_guia = """
    1. Si eres un nuevo usuario, dirígete a la pestaña 'Registro Funcionarios'.
    2. Completa los campos con tu Nombre del Funcionario, Correo electrónico, Usuario y Contraseña.
    3. Haz clic en 'Registrar' para crear tu cuenta.
    4. Luego, ve a la pestaña 'Acceso Funcionarios' y usa tu usuario y contraseña.
    5. Presiona 'Iniciar Sesión' para acceder al sistema.
    """
    
    label_texto_guia = tk.Label(frame_guia, text=texto_guia, font=("Arial", 10), bg="#f0f0f0", justify="left")
    label_texto_guia.pack(padx=20, pady=10)

    ventana_login.mainloop()

# --- Iniciar la aplicación ---
mostrar_login()