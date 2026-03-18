# Telegram Dashboard - Content Manager 🚀

Este es un panel de administración (Dashboard) de una sola página (SPA) diseñado para gestionar y automatizar el envío de contenido a canales de Telegram. Construido con **FastAPI** y **SQLite**, ofrece una interfaz moderna y persistencia de datos local.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.10+, FastAPI, Uvicorn.
* **Base de Datos:** SQLite3 (Persistencia de historial).
* **Frontend:** HTML5, JavaScript (Fetch API), Tailwind CSS.
* **Integración:** Telegram Bot API (Requests).
* **UI/UX:** SweetAlert2 (Notificaciones asíncronas) y FontAwesome.

## ✨ Características

* **Envío Multimedia:** Soporte para mensajes de texto plano y envío de imágenes con pie de foto (caption).
* **Historial en Tiempo Real:** Registro automático de cada envío en una base de datos local.
* **Interfaz Responsiva:** Diseño oscuro (Dark Mode) optimizado para escritorio y móviles.
* **Validación de Errores:** Manejo robusto de excepciones tanto en el lado del servidor como en el cliente.

Instalar dependencias:

Bash
pip install fastapi uvicorn requests python-multipart

Configuración:
Crea un archivo .env o edita las variables en main.py:

TOKEN: El token de tu Bot de Telegram.

CHAT_ID: El ID de tu canal o grupo.

Ejecutar:

Bash
uvicorn main:app --reload
Accede a http://127.0.0.1:8000 en tu navegador.

Desarrollado por Miguel Netti