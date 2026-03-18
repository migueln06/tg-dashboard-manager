import os
import requests
import sqlite3
from fastapi import UploadFile, File
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from typing import Optional
# Cargar variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def init_db():
    conn = sqlite3.connect("historial.db")
    cursor = conn.cursor()
    # Creamos la tabla si no existe
    cursor.execute("""CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mensaje TEXT,
            tipo TEXT,
            estado TEXT
                   )
""")
    conn.commit()
    conn.close()
    # Ejecutamos la inicialización al arrancar
init_db()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TG Dashboard | Miguel Netti</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-slate-900 min-h-screen flex items-center justify-center p-6">
        <div class="max-w-md w-full bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 overflow-hidden">
            <div class="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white text-center">
                <i class="fa-solid fa-paper-plane text-4xl mb-3"></i>
                <h1 class="text-2xl font-bold tracking-tight">Telegram Dashboard</h1>
                <p class="text-blue-100 text-sm opacity-80">Gestión de contenido para canales</p>
            </div>

            <form id="tgForm" class="p-8 space-y-6">
                <div>
                    <label class="block text-slate-300 text-sm font-medium mb-2 uppercase tracking-wider">Nuevo Mensaje</label>
                    <textarea id="mensaje" name="mensaje" rows="5" 
                        class="w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none"
                        placeholder="Escribe el post de hoy..." required></textarea>
                </div>
                <div>
                    <label class="block text-slate-300 text-sm font-medium mb-2 uppercase tracking-wider">Adjuntar Imagen (Opcional)</label>
                    <input type="file" id="foto" accept="image/*"
                        class="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer">
                </div>
                <button type="submit" id="btnSubmit"
                    class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-3">
                    <i class="fa-solid fa-rocket"></i> Publicar en Canal
                </button>
            </form>
            <div class="mt-8 p-6 bg-slate-900/50 rounded-xl border border-slate-700/50">
    <h2 class="text-slate-300 text-sm font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
        <i class="fa-solid fa-clock-rotate-left"></i> Últimos Envíos
    </h2>
    <div id="tablaHistorial" class="space-y-3">
        <p class="text-slate-500 text-xs italic">Cargando historial...</p>
    </div>
</div>

            <div class="bg-slate-900/50 p-4 text-center border-t border-slate-700/50">
                <span class="text-slate-500 text-xs uppercase tracking-widest font-semibold">Admin: Miguel Netti</span>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<script>
    document.getElementById('tgForm').onsubmit = async function(e) {
        e.preventDefault();
        
        const btn = document.getElementById('btnSubmit');
        const textarea = document.getElementById('mensaje');
        const fotoInput = document.getElementById('foto');
        const originalContent = btn.innerHTML;

        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Enviando...';

        const formData = new FormData();
        formData.append('mensaje', textarea.value);
        if (fotoInput.files[0]) {
            formData.append('foto', fotoInput.files[0]);
        }

        try {
            const response = await fetch('/enviar', {
                method: 'POST',
                body: formData
            });

            // --- INICIO DEL BLINDAJE ---
            // Si la respuesta es exitosa (200 OK), el mensaje llegó a Telegram
            if (response.ok) {
                // Intentamos leer el JSON, si falla (porque vino vacío), usamos un objeto por defecto
                const result = await response.json().catch(() => ({ status: "ok" }));

                if (result && result.status === "ok") {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Publicado!',
                        text: 'El mensaje ya está en tu canal.',
                        background: '#1e293b', color: '#f8fafc', confirmButtonColor: '#2563eb'
                    });
                    textarea.value = '';
                    fotoInput.value = '';
                    // --- ESTA ES LA LÍNEA MÁGICA ---
    cargarHistorial();
                    // --- FIN DEL BLINDAJE ---
                    return; // Salimos con éxito absoluto

                    
                }
            }
            
            // Si llegamos aquí, algo realmente falló
            throw new Error("No se pudo confirmar el envío.");
            // --- FIN DEL BLINDAJE ---

        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Fallo el envío',
                text: error.message,
                background: '#1e293b', color: '#f8fafc'
            });
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    };
    async function cargarHistorial() {
    const contenedor = document.getElementById('tablaHistorial');
    try {
        const response = await fetch('/historial');
        const datos = await response.json();
        
        if (datos.length === 0) {
            contenedor.innerHTML = '<p class="text-slate-600 text-xs">No hay registros aún.</p>';
            return;
        }

        contenedor.innerHTML = datos.map(item => `
            <div class="bg-slate-800 p-3 rounded-lg border border-slate-700 flex justify-between items-center gap-4">
                <div class="overflow-hidden">
                    <p class="text-slate-300 text-sm truncate">${item.mensaje}</p>
                    <span class="text-[10px] text-slate-500 uppercase font-bold">${item.fecha}</span>
                </div>
                <span class="px-2 py-1 rounded text-[9px] font-bold uppercase ${item.tipo === 'Foto' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-emerald-500/20 text-emerald-400'}">
                    ${item.tipo}
                </span>
            </div>
        `).join('');
    } catch (e) {
        contenedor.innerHTML = '<p class="text-red-400 text-xs">Error al cargar historial.</p>';
    }
}

// Cargar al iniciar la página
cargarHistorial();

// TIP PROFESIONAL: Llama a cargarHistorial() dentro de tu .onsubmit 
// justo después de que el SweetAlert de éxito se cierre.
</script>
    </body>
    </html>
    """
# @app.post("/enviar")
# async def enviar_mensaje(mensaje: str = Form(...)):
#     url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
#     payload = {
#         "chat_id": CHAT_ID,
#         "text": mensaje,
#         "parse_mode": "HTML"
#     }
#     response = requests.post(url, json=payload)
#     if response.status_code == 200:
#         return {"status": "success", "detalle": "Mensaje enviado exitosamente"}
#     else:
#         return {"status": "error", "detalle": "Error al enviar el mensaje"}

@app.get("/historial")
async def obtener_historial():
    try:
        with sqlite3.connect("historial.db") as conn:
            conn.row_factory = sqlite3.Row # Esto nos permite usar nombres de columnas
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, mensaje, tipo FROM publicaciones ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            
            # Convertimos los resultados a una lista de diccionarios
            historial = [dict(row) for row in rows]
            return historial
    except Exception as e:
        print(f"Error al leer historial: {e}")
        return []

@app.post("/enviar")
async def enviar_mensaje(
    mensaje: str = Form(...), 
    foto: Optional[UploadFile] = File(None)
):
    response = None 
    tipo_msg = "Texto"
    
    try:
        if foto and foto.filename:
            tipo_msg = "Foto"
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            contenido_foto = await foto.read()
            files = {"photo": (foto.filename, contenido_foto, foto.content_type)}
            payload = {
                "chat_id": CHAT_ID,
                "caption": mensaje,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=payload, files=files)
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": mensaje,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=payload)

        # Verificamos si Telegram aceptó el envío
        if response and response.ok:
            # Intentamos guardar en SQLite (opcional, no detiene el flujo)
            try:
                with sqlite3.connect("historial.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO publicaciones (mensaje, tipo, estado) VALUES (?, ?, ?)",
                        (mensaje, tipo_msg, "Enviado")
                    )
                    conn.commit()
            except Exception as db_e:
                print(f"Error SQLite: {db_e}")

            # EL RETORNO CRUCIAL: Esto evita el error de 'null' en JS
            return {"status": "ok", "detalle": "Publicado con éxito"}
        else:
            detalles = response.text if response else "Sin respuesta de Telegram"
            return {"status": "error", "detalle": detalles}

    except Exception as e:
        return {"status": "error", "detalle": str(e)}

        # Verificamos si response existe antes de devolverlo
    #     if response:
    #         return {"status": "ok" if response.ok else "error", "detalle": response.text}
    #     else:
    #         return {"status": "error", "detalle": "No se generó respuesta"}

    # except Exception as e:
    #     return {"status": "error", "detalle": str(e)}
    
    if response and response.ok:
            # Definimos el tipo
            tipo_msg = "Foto" if (foto and foto.filename) else "Texto"
            
            # Intentamos guardar, pero que un error aquí no rompa la respuesta
            try:
                with sqlite3.connect("historial.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO publicaciones (mensaje, tipo, estado) VALUES (?, ?, ?)",
                        (mensaje, tipo_msg, "Enviado")
                    )
                    conn.commit()
                print("DB: Guardado exitoso")
            except Exception as e_db:
                print(f"DB Error (No crítico): {e_db}")

            # IMPORTANTE: Esta línea DEBE ejecutarse sí o sí
            return {"status": "ok", "detalle": "Enviado correctamente"}
    
    



