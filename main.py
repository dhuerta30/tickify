import tkinter as tk
import http.client
import json
import bcrypt
import smtplib
import ssl
import os
import sys
from email.message import EmailMessage
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

def resource_path(relative_path):
    """ Devuelve la ruta absoluta del archivo, ya sea en desarrollo o empaquetado """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def obtener_token(rut, password):
    """Realiza una solicitud HTTP para obtener un token de autenticación."""
    conn = http.client.HTTPSConnection("developmentserver.cl")
    payload = json.dumps({
        "data": {
            "rut": rut,
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

    #print("📨 Correo enviado exitosamente!")
    messagebox.showinfo("Éxito", "Correo enviado exitosamente!")


#=================== Obtener Datos usuario de la sessión ==========================#
def obtener_usuario_session(token, rut):
    """Obtiene la información del usuario autenticado usando un token JWT."""
    conn = http.client.HTTPSConnection("developmentserver.cl")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    conn.request("GET", f"/tickify/api/usuario/?where=rut,{rut}", headers=headers)
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
def obtener_datos_tabla_usuario(token, rut_usuario):
    """Obtiene la información del usuario autenticado usando un token JWT."""
    
    conn = http.client.HTTPSConnection("developmentserver.cl")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    #cliente = quote(nombre_usuario)
    #status = quote("Ingresado")

    conn.request("GET", f"/tickify/api/soporte/rut_cliente/{rut_usuario}", headers=headers)
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
def cargar_datos_en_grilla(tree, token, rut_usuario):
    """Carga los datos en la grilla (Treeview)."""
    tree.delete(*tree.get_children())  # Limpiar la tabla antes de insertar nuevos datos

    datos = obtener_datos_tabla_usuario(token, rut_usuario)
    #print(datos)
   
    # Si no hay datos, salir de la función sin agregar filas
    if not datos:
        return

    for item in datos:
        fecha_formateada = (
            datetime.strptime(item.get("fecha", ""), "%Y-%m-%d").strftime("%d/%m/%Y")
            if item.get("fecha", "") else ""
        )

        tree.insert("", "end", values=(
            item.get("id_soporte", ""),
            item.get("cliente", ""),
            item.get("rut_cliente", ""),
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
    rut = entry_rut_reg.get()
    clave = entry_clave_reg.get()

    if not (nombre and correo and rut and clave):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), salt).decode('utf-8')

    conn = http.client.HTTPSConnection("developmentserver.cl")
    payload = json.dumps({
        "tabla": "usuario",
        "nombre": nombre,
        "email": correo,
        "rut": rut,
        "password": hashed_password,
        "idrol": "1",
        "estatus": "1"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    # Enviar solicitud POST
    conn.request("POST", "/tickify/Restp/insertar", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # Mostrar respuesta de la API
    #print("Respuesta de la API:", data.decode("utf-8"))

    messagebox.showinfo("Éxito", f"Registrando usuario: {nombre}, {correo}, {rut}")

    # Limpiar los campos después del registro
    entry_nombre.delete(0, tk.END)
    entry_correo.delete(0, tk.END)
    entry_rut_reg.delete(0, tk.END)
    entry_clave_reg.delete(0, tk.END)


#============= Función para verificar el inicio de sesión =============#
def verificar_login():
    rut = entry_rut.get()
    clave = entry_clave.get()
    
    token = obtener_token(rut, clave)
    usuario_session_data = obtener_usuario_session(token, rut)

    if token:
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        ventana_login.destroy()  # Cierra la ventana de login
        iniciar_aplicacion(token, usuario_session_data)  # Inicia la aplicación principal con el token
    else:
        messagebox.showerror("Error", "Rut o contraseña incorrectos")


def cerrar_sesion():
    app.destroy()
    mostrar_login()

#=================================== Formatear Rut ===========================================#
def formatear_rut(event):
    entry = event.widget  # Detecta qué campo activó el evento
    rut = entry.get().replace(".", "").replace("-", "")  # Quitar puntos y guión

    # Limitar la entrada a 9 caracteres (8 números + 1 dígito verificador)
    if len(rut) > 9:
        rut = rut[:9]

    if len(rut) > 1:
        rut_num = rut[:-1]  # Números del RUT sin el dígito verificador
        dv = rut[-1].upper()  # Dígito verificador en mayúscula

        # Validar que la parte numérica solo contenga números
        if not rut_num.isdigit():
            rut_num = "".join(filter(str.isdigit, rut_num))  # Eliminar caracteres no numéricos

        # Validar que el dígito verificador sea un número o "K"
        if not (dv.isdigit() or dv == "K"):
            dv = ""  # Si es inválido, eliminarlo

        # Formatear solo con guion
        rut_formateado = f"{rut_num}-{dv}"

        # Reemplazar el contenido del campo con el RUT formateado
        entry.delete(0, tk.END)
        entry.insert(0, rut_formateado)


def version():
    version = "1.1"
    return version

#=============== Función para iniciar la aplicación principal =================================#
def iniciar_aplicacion(token, usuario_session_data):
    global app, entry_nombre, entry_rut_cliente, entry_departamento, combo_asignado, combo_incidente
    global text_descripcion, combo_prioridad, tree, label_descripcion

    app = tk.Tk()
    app.title("Tickify - Gestión de Tickets - Versión " + version())
    app.geometry("800x800")
    app.config(bg="#f0f0f0")

    # Cargar imagen
    try:
        logo_path = resource_path(os.path.join("img", "logo.png"))
        imagen_original = Image.open(logo_path)
        imagen_resized = imagen_original.resize((200, 60))
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

    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 16), padding=[20, 10])

    notebook.add(frame_formulario, text="Agregar Ticket")
    notebook.add(frame_tabla, text="Mis Tickets")

    app.option_add('*TCombobox*Listbox.Font', ("Arial", 16))

    # --- Formulario ---
    frame = tk.Frame(frame_formulario, bg="#f0f0f0")
    frame.pack(pady=20)

    tk.Label(frame, text="Nombre del Funcionario:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="w")
    entry_nombre = tk.Entry(frame, width=40, font=("Arial", 16), state="normal")
    entry_nombre.grid(row=0, column=1, pady=5)
    
    # Rut del Funcionario (AQUÍ ESTÁ EL ERROR: Estaba en row=0, debe ser row=1)
    tk.Label(frame, text="Rut del Funcionario:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="w")
    entry_rut_cliente = tk.Entry(frame, width=40, font=("Arial", 16), state="normal")  # Campo solo lectura
    entry_rut_cliente.grid(row=1, column=1, pady=5)
    entry_rut_cliente.bind("<KeyRelease>", formatear_rut)
    
    if isinstance(usuario_session_data, list) and usuario_session_data:
        datos_usuario = usuario_session_data[0]  # Extraer el primer elemento (diccionario)
        nombre_usuario = datos_usuario.get("nombre", "")  # Obtener el nombre del usuario
        usuario_usuario = datos_usuario.get("usuario", "")  # Obtener el rut del usuario
        rut_usuario = datos_usuario.get("rut", "")
    else:
        nombre_usuario = ""

    entry_nombre.insert(0, nombre_usuario)
    entry_rut_cliente.insert(0, rut_usuario)

    entry_nombre.config(state="readonly")
    entry_rut_cliente.config(state="readonly")

    tk.Label(frame, text="Asignado a:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=2, column=0, pady=5, sticky="w")
    combo_asignado = ttk.Combobox(frame, values=[
        "Jorge Nicolas Berrios Cornejo",
        "Sergio Andrés Concha Llanos",
        "Juan Pablo Alvarez Avalos",
        "Elena Garrido Santibañez",
        "Daniel Bernardo Huerta Rojas",
        "Leonardo Antonio Martinez Vera"
    ], state="readonly", width=38, font=("Arial", 16))
    combo_asignado.grid(row=2, column=1, pady=5)
    combo_asignado.bind("<<ComboboxSelected>>", actualizar_departamentos)

    tk.Label(frame, text="Departamento:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5, sticky="w")
    entry_departamento = ttk.Combobox(frame, values=["Soporte Informática", "Desarrollo de Sistemas"], state="readonly", width=38, font=("Arial", 16))
    entry_departamento.grid(row=3, column=1, pady=5)

    tk.Label(frame, text="Incidente:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=4, column=0, pady=5, sticky="w")
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
    ], state="readonly", width=38, font=("Arial", 16))
    combo_incidente.grid(row=4, column=1, pady=5)
    combo_incidente.bind("<<ComboboxSelected>>", mostrar_descripcion)

    label_descripcion = tk.Label(frame, text="Descripción:", font=("Arial", 16, "bold"), bg="#f0f0f0")
    text_descripcion = tk.Text(frame, width=40, height=5, font=("Arial", 16))

    tk.Label(frame, text="Prioridad:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=5, column=0, pady=5, sticky="w")
    combo_prioridad = ttk.Combobox(frame, values=["Alta", "Media", "Baja"], state="readonly", width=38, font=("Arial", 16))
    combo_prioridad.grid(row=5, column=1, pady=5)

    button_enviar = tk.Button(frame_formulario, text="Enviar Ticket", command=lambda: enviar_ticket(token), font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", relief="flat", width=20, height=2)
    button_enviar.pack(pady=20)

    # --- Botón de Cerrar Sesión ---
    button_cerrar_sesion = tk.Button(app, text="Cerrar Sesión", command=cerrar_sesion, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_cerrar_sesion.pack(pady=10)

    # --- Tabla de tickets ---
    columns = ("N°Ticket", "Nombre del Funcionario", "Rut del Funcionario", "Fecha", "Asignado a", "Departamento", "Incidente", "Prioridad", "Status", "Descripción")
    tree = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=10)

    for col in columns:
        tree.column(col, anchor="center")  # Centra los valores de la columna
        tree.heading(col, anchor="center")
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(expand=True, fill="both", pady=20)

    # Cargar datos en la grilla
    cargar_datos_en_grilla(tree, token, rut_usuario)

    button_eliminar = tk.Button(frame_tabla, text="Anular Ticket", command=lambda: anular_ticket(token), font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", relief="flat", width=20, height=2)
    button_eliminar.pack(pady=10)

    app.mainloop()

#================= Funciones para la gestión de tickets ================#
def enviar_ticket(token):
    """Envía un ticket a la API."""
    nombre = entry_nombre.get()
    rut_cliente = entry_rut_cliente.get()
    departamento = entry_departamento.get()
    asignado_a = combo_asignado.get()
    incidente = combo_incidente.get()
    descripcion = text_descripcion.get("1.0", tk.END).strip() or "Sin Descripción"
    prioridad = combo_prioridad.get()
    fecha_creacion = datetime.now().strftime("%Y-%m-%d")

    # Validaciones antes de enviar
    if asignado_a == "Daniel Bernardo Huerta Rojas" and departamento != "Desarrollo de Sistemas":
        messagebox.showwarning("Advertencia", "Daniel Bernardo Huerta Rojas solo puede ser asignado a Desarrollo de Sistemas.")
        return

    if not nombre or not rut_cliente or not departamento or not asignado_a or not incidente or not prioridad or (incidente == "Otro" and not descripcion):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    # Crear conexión con la API
    datos_ticket = json.dumps({
        "data": {
            "cliente": nombre,
            "rut_cliente": rut_cliente,
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
    conn.request("POST", "/tickify/api/soporte", body=datos_ticket, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")

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

    cargar_datos_en_grilla(tree, token, rut_cliente)

    # Limpiar los campos después del registro
    combo_asignado.set("")
    entry_departamento.delete(0, tk.END)
    combo_incidente.set("")
    combo_prioridad.set("")
    text_descripcion.delete("1.0", tk.END)


#=========== Anular Ticket ===============#
def anular_ticket(token):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Seleccione un ticket para Anular.")
        return

    id_soporte = tree.item(selected_item, "values")[0]
    nombre = tree.item(selected_item, "values")[1]
    rut_cliente = tree.item(selected_item, "values")[2]

    respuesta = messagebox.askyesno("Confirmación", f"¿Está seguro de que desea anular el ticket N° {id_soporte}?")
    if respuesta:

        try:
            conn = http.client.HTTPSConnection("developmentserver.cl")
            datos_ticket = json.dumps({
                "data": {
                    "status": "Anulado"
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }

            # Hacer la solicitud UPDATE con el ID seleccionado
            conn.request("PUT", f"/tickify/api/soporte/{id_soporte}", body=datos_ticket, headers=headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
    
            messagebox.showinfo("Éxito", f"Ticket N° {id_soporte} Anulado con éxito.")
            cargar_datos_en_grilla(tree, token, rut_cliente)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")


#============= Mostrar Descripcion ==================#
def mostrar_descripcion(event):
    if combo_incidente.get() == "Otro":
        label_descripcion.grid(row=6, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=6, column=1, pady=5)
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

        label_descripcion.grid(row=6, column=0, pady=5, sticky="w")
        text_descripcion.grid(row=6, column=1, pady=5)
        
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
    global ventana_login, entry_rut, entry_clave
    global entry_nombre, entry_correo, entry_rut_reg, entry_clave_reg

    ventana_login = tk.Tk()
    ventana_login.title("Tickify - Acceso Funcionarios a Ticket de Soporte - Versión " + version())
    ventana_login.geometry("800x700")
    ventana_login.config(bg="#f0f0f0")

    # Cargar imagen
    try:
        logo_path = resource_path(os.path.join("img", "logo.png"))
        imagen_original = Image.open(logo_path)
        imagen_resized = imagen_original.resize((200, 60))
        imagen = ImageTk.PhotoImage(imagen_resized)

        label_imagen = tk.Label(ventana_login, image=imagen)
        label_imagen.image = imagen  # Evita eliminación por recolector de basura
        label_imagen.pack(pady=20)
    except Exception as e:
        print(f"Error cargando la imagen: {e}")

    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 16), padding=[20, 10])

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

    tk.Label(frame_login_form, text="Rut:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5)
    entry_rut = tk.Entry(frame_login_form, width=30, font=("Arial", 16))
    entry_rut.grid(row=0, column=1, pady=5)
    entry_rut.bind("<KeyRelease>", formatear_rut)

    tk.Label(frame_login_form, text="Contraseña:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5)
    entry_clave = tk.Entry(frame_login_form, show="*", width=30, font=("Arial", 16))
    entry_clave.grid(row=1, column=1, pady=5)

    tk.Button(frame_login_form, text="Iniciar Sesión", command=verificar_login, font=("Arial", 12, "bold"),
              bg="#4CAF50", fg="white", relief="flat", width=15, height=2).grid(row=2, column=0, columnspan=2, pady=20)

    # ==================== REGISTRO ====================
    frame_registro_form = tk.Frame(frame_registro, bg="#f0f0f0")
    frame_registro_form.pack(pady=20)

    tk.Label(frame_registro_form, text="Nombre del Funcionario:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=5)
    entry_nombre = tk.Entry(frame_registro_form, width=30, font=("Arial", 16))
    entry_nombre.grid(row=0, column=1, pady=5)

    tk.Label(frame_registro_form, text="Correo electrónico:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=1, column=0, pady=5)
    entry_correo = tk.Entry(frame_registro_form, width=30, font=("Arial", 16))
    entry_correo.grid(row=1, column=1, pady=5)

    tk.Label(frame_registro_form, text="Rut:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=2, column=0, pady=5)
    entry_rut_reg = tk.Entry(frame_registro_form, width=30, font=("Arial", 16))
    entry_rut_reg.grid(row=2, column=1, pady=5)
    entry_rut_reg.bind("<KeyRelease>", formatear_rut)

    tk.Label(frame_registro_form, text="Contraseña:", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=3, column=0, pady=5)
    entry_clave_reg = tk.Entry(frame_registro_form, show="*", width=30, font=("Arial", 16))
    entry_clave_reg.grid(row=3, column=1, pady=5)

    tk.Button(frame_registro_form, text="Registrar", command=registrar_usuario, font=("Arial", 16, "bold"),
              bg="#008CBA", fg="white", relief="flat", width=15, height=2).grid(row=5, column=0, columnspan=2, pady=20)

     # ==================== GUÍA DE USO ====================
    label_guia = tk.Label(frame_guia, text="Guía de Uso", font=("Arial", 16, "bold"), bg="#f0f0f0")
    label_guia.pack(pady=10)

    texto_guia = """
    1. Si eres un nuevo usuario, dirígete a la pestaña 'Registro Funcionarios'.
    2. Completa los campos con tu Nombre del Funcionario, Correo electrónico, Usuario y Contraseña.
    3. Haz clic en 'Registrar' para crear tu cuenta.
    4. Luego, ve a la pestaña 'Acceso Funcionarios' y usa tu usuario y contraseña.
    5. Presiona 'Iniciar Sesión' para acceder al sistema.
    """
    
    label_texto_guia = tk.Label(frame_guia, text=texto_guia, font=("Arial", 16), bg="#f0f0f0", justify="left")
    label_texto_guia.pack(padx=20, pady=10)

    ventana_login.mainloop()

# --- Iniciar la aplicación ---
mostrar_login()