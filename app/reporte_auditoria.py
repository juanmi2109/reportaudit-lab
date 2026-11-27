"""
ReportAudit — lógica de negocio del servicio de reportes de auditoría.

Versión corregida tras la auditoría de seguridad del Laboratorio 1.
"""

import hashlib
import os
import re
import sqlite3
import subprocess
from pathlib import Path

import yaml


# Configuración mediante variables de entorno.
NOTIFICATION_API_KEY = os.environ.get(
    "REPORTAUDIT_NOTIFICATION_API_KEY", ""
)
SMTP_PASSWORD = os.environ.get(
    "REPORTAUDIT_SMTP_PASSWORD", ""
)

RUTA_DB = os.path.join(
    os.path.dirname(__file__), "..", "reportes.db"
)

NOMBRE_HTML_VALIDO = re.compile(
    r"^[A-Za-z0-9_][A-Za-z0-9_.-]*\.html$"
)


def cargar_configuracion(ruta_config):
    """Carga la configuración del servicio desde un archivo YAML."""
    with open(ruta_config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def buscar_reportes_cliente(nombre_cliente, ruta_db=RUTA_DB):
    """Devuelve todos los reportes asociados a un cliente."""
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        query = "SELECT * FROM reportes WHERE cliente = ?"
        cursor.execute(query, (nombre_cliente,))
        resultados = cursor.fetchall()
        return resultados
    finally:
        conexion.close()


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF de forma segura."""
    if (
        Path(nombre_archivo).name != nombre_archivo
        or not NOMBRE_HTML_VALIDO.fullmatch(nombre_archivo)
    ):
        raise ValueError("Nombre de archivo no válido")

    salida = nombre_archivo + ".pdf"

    try:
        subprocess.run(
            ["wkhtmltopdf", nombre_archivo, salida],
            check=False,
        )
    except FileNotFoundError:
        print(
            "Aviso: wkhtmltopdf no está instalado; "
            "no se generó el PDF."
        )

    return salida


def hash_password_legacy(password):
    """Genera un hash de contraseña con sal aleatoria."""
    sal = os.urandom(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), sal, 600_000
    )
    return sal.hex() + ":" + derivado.hex()


def notificar_cliente(email, mensaje):
    """Simula el envío de una notificación al cliente."""
    estado = "configurada" if NOTIFICATION_API_KEY else "no configurada"
    print(f"[NotifyAPI: clave {estado}] -> {email}: {mensaje}")
    return True