import hashlib
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import reporte_auditoria as ra


class TestReporteAuditoria(unittest.TestCase):

    def test_cargar_configuracion(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "config.yaml"
            ruta.write_text(
                "servicio:\n  nombre: ReportAudit\n",
                encoding="utf-8"
            )

            config = ra.cargar_configuracion(ruta)

            self.assertEqual(
                config["servicio"]["nombre"],
                "ReportAudit"
            )

    def test_buscar_reportes_cliente(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "test.db"

            with sqlite3.connect(ruta) as conexion:
                conexion.execute(
                    "CREATE TABLE reportes "
                    "(id INTEGER, cliente TEXT, monto REAL)"
                )
                conexion.executemany(
                    "INSERT INTO reportes VALUES (?, ?, ?)",
                    [
                        (1, "acme_corp", 100),
                        (2, "acme_corp", 200),
                        (3, "o'brien_ltd", 300),
                    ]
                )

            self.assertEqual(
                len(ra.buscar_reportes_cliente("acme_corp", ruta)), 2
            )
            self.assertEqual(
                len(ra.buscar_reportes_cliente("o'brien_ltd", ruta)), 1
            )
            self.assertEqual(
                ra.buscar_reportes_cliente("inexistente", ruta), []
            )

    @patch("app.reporte_auditoria.subprocess.run")
    def test_convertir_nombre_valido(self, mock_run):
        resultado = ra.convertir_a_pdf("informe.html")

        self.assertEqual(resultado, "informe.html.pdf")
        mock_run.assert_called_once_with(
            ["wkhtmltopdf", "informe.html", "informe.html.pdf"],
            check=False
        )

    def test_convertir_nombre_invalido(self):
        for nombre in ["informe final.html", "../informe.html"]:
            with self.subTest(nombre=nombre):
                with self.assertRaises(ValueError):
                    ra.convertir_a_pdf(nombre)

    @patch(
        "app.reporte_auditoria.subprocess.run",
        side_effect=FileNotFoundError
    )
    def test_convertir_sin_herramienta(self, mock_run):
        self.assertEqual(
            ra.convertir_a_pdf("informe.html"),
            "informe.html.pdf"
        )

    def test_hash_password(self):
        password = "password-de-prueba"

        resultado1 = ra.hash_password_legacy(password)
        resultado2 = ra.hash_password_legacy(password)

        self.assertNotEqual(resultado1, resultado2)

        sal, derivado = resultado1.split(":")

        esperado = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(sal),
            600_000
        )

        self.assertEqual(derivado, esperado.hex())
        self.assertEqual(len(sal), 32)

    @patch("app.reporte_auditoria.NOTIFICATION_API_KEY", "")
    @patch("builtins.print")
    def test_notificar_sin_clave(self, mock_print):
        self.assertTrue(
            ra.notificar_cliente("test@example.com", "Prueba")
        )
        self.assertIn(
            "no configurada",
            mock_print.call_args.args[0]
        )

    @patch(
        "app.reporte_auditoria.NOTIFICATION_API_KEY",
        "valor-ficticio-de-prueba"
    )
    @patch("builtins.print")
    def test_notificar_con_clave(self, mock_print):
        self.assertTrue(
            ra.notificar_cliente("test@example.com", "Prueba")
        )

        mensaje = mock_print.call_args.args[0]

        self.assertIn("clave configurada", mensaje)
        self.assertNotIn("valor-ficticio", mensaje)


if __name__ == "__main__":
    unittest.main()