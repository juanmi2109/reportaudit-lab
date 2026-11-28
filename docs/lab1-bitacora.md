# Laboratorio 1 — Bitácora de auditoría de la cadena de suministro

- **Autor/a:** Juan Miguel Hernández Romero
- **Repositorio:** https://github.com/juanmi2109/reportaudit-lab
- **Sistema operativo y versión de Python usados:** Ubuntu 24.04 (WSL2), Python 3.12.3

> Completa cada sección en el momento en que la guía te lo pide, no al final.
> Una bitácora escrita "de memoria" al terminar no sirve como evidencia.

---

## Parte B — Auditoría manual (antes de usar ninguna herramienta)

| # | Función | Línea | Qué sospechas | Dato de entrada (*source*) | Destino peligroso (*sink*) |
|---|---|---|---|---|---|
| 1 | Global |22|Credenciales y claves API escritas en código fuente|SMTP_PASSWORD|Asignación en memoria accesible|
| 2 | hash_password_legacy|57|Criptografía débil|password|hashlib.md5()|
| 3 | buscar_reportes_cliente | 42 (ejecución SQL) | Inyección SQL | nombre_cliente | cursor.execute |
| 4 | convertir_a_pdf | No verificada | Inyección de comandos | nombre_archivo | os.system |
| 5 | cargar_configuracion | No verificada | Carga YAML insegura | contenido YAML | yaml.load |

Las filas 3–5 se reconstruyen a partir del código original y la auditoría posterior; no constituyen hallazgos manuales registrados antes de usar herramientas.

**Impacto en el negocio:** para cada sospecha, explica en una frase qué
consecuencia tendría para ReportAudit y sus clientes si fuera real (qué datos,
qué sistema o qué credencial quedarían expuestos).

1. Exposición de claves API y credenciales de correo SMTP en el repositorio público
2. MD5 sin sal facilita la recuperación de contraseñas débiles.
3. Riesgo de acceso indebido a reportes de clientes.
4. Riesgo de ejecución no autorizada de procesos.
5. Riesgo de procesamiento inseguro de configuraciones.
---

## Matriz de detección (se completa a lo largo del laboratorio)

Marca ✓ (lo detectó, anota la regla) o ✗ (no lo detectó) en cada columna cuando
llegues a la parte correspondiente.

| Hallazgo | Manual (B) | SonarQube for IDE sin conexión (D) | SonarQube for IDE en Connected Mode (E) | SonarQube Cloud (F) | CodeQL (F) | Semgrep (G) | Trivy (L) |
|---|---|---|---|---|---|---|---|
| H1 Inyección SQL en `buscar_reportes_cliente` | Sin registro inicial | No verificado | No verificado | No verificado | No verificado | No verificado | n/a |
| H2 Inyección de comandos en `convertir_a_pdf` | Sin registro inicial | No verificado | No verificado | No verificado | No verificado | No verificado | n/a |
| H3 Deserialización YAML insegura en `cargar_configuracion` | Sin registro inicial | No verificado | No verificado | No verificado | No verificado | No verificado | n/a |
| H4 Hash MD5 en `hash_password_legacy` | ✓ (auditoría manual) | No verificado | No verificado | No verificado | No verificado | No verificado | n/a |
| H5 Clave de API escrita en el código | ✓ (auditoría manual) | No verificado | No verificado | No verificado | No verificado | No verificado | ✗ |
| H6 Contraseña SMTP escrita en el código | ✓ (auditoría manual) | No verificado | No verificado | No verificado | No verificado | No verificado | ✗ |

**Conclusión de la matriz** (Parte L): Trivy no reportó los secretos identificados manualmente. No puede garantizarse la ausencia de riesgos con una sola herramienta; SAST, SCA, análisis de secretos y revisión manual se complementan. Queda pendiente recuperar los resultados individuales de las herramientas anteriores para completar la matriz.


## Parte I — Dependabot

Se ha configurado Dependabot para los ecosistemas pip y GitHub Actions, activando las alertas de seguridad y las actualizaciones agrupadas.

**Resultados obtenidos:**

- Componentes identificados en el grafo de dependencias: 13.
- Dependencias directas de Python: 2.
- Dependencias transitivas declaradas: 7.
- Alertas abiertas de Dependabot: 0.
- Alertas cerradas de Dependabot: 0.
- Pull Request automático: #18.
- Actualización propuesta: actions/checkout de la versión 6 a la 7.
- Comprobaciones del pipeline: 5/5 superadas.

**Incidencia:**

Dependabot reconoce las dependencias de Python, pero no muestra alertas de seguridad. Se ha comprobado el archivo dependabot.yml, el grafo de dependencias y las reglas de clasificación automática. También se ha consultado la API de GitHub sin obtener alertas.

Grype y Trivy detectaron 13 vulnerabilidades cada uno. Posteriormente Dependabot mostró también 13 alertas (7 de Werkzeug, 5 de Jinja2 y 1 de Flask). El PR de seguridad #20 se fusionó; en la última comprobación hay 0 alertas abiertas y 13 cerradas. La causa del retraso inicial no se ha determinado. El cierre del Issue #4 queda pendiente de verificar; el PR #18 no se ha fusionado.

---


---

## Parte J — Instalación de herramientas

Syft 1.52.0, Grype 0.119.0 y Trivy 0.74.0 instalados con comprobación SHA-256 satisfactoria (documento de capturas, p. 23).

---

## Parte K — SBOM: el iceberg medido

| Dato | Valor |
|---|---|
| Dependencias directas (`requirements.in`) | 2: Flask y PyYAML |
| Componentes Python en el SBOM | 9 |
| Otros componentes que aparezcan en el SBOM (si los hay) y de dónde salen | 4 GitHub Actions procedentes del workflow de seguridad |
| Formato y versión de especificación del SBOM (`bomFormat`, `specVersion`) | CycloneDX 1.7 |

Syft ha catalogado 13 paquetes: 9 de Python y 4 de GitHub Actions. El documento JSON contiene 15 entradas en su lista de componentes.

El inventario demuestra que, aunque el proyecto declara únicamente dos dependencias directas de Python, también incorpora siete dependencias transitivas

Evidencia: [sbom.cyclonedx.json](evidencias/sbom.cyclonedx.json).
---

## Parte K — Triage de vulnerabilidades de dependencias (Grype)

| Paquete | Versión | ¿Directa o transitiva? (usa `# via`) | CVE / GHSA | Severidad | Corregida en | ¿Explotable en ReportAudit? ¿Por qué? | Decisión |
|---|---|---|---|---|---|---|---|
| Werkzeug | 3.0.1 | Transitiva | GHSA-2g68-c3qc-8985 / CVE-2024-34069 | High | 3.0.3 | No en el modo de ejecución previsto: `app/servicio.py` arranca con `debug=False`, por lo que el depurador interactivo está desactivado. | Actualizar y documentar mediante VEX |
| Werkzeug | 3.0.1 | Transitiva | GHSA-q34m-jh98-gwm2 | Medium | 3.0.6 | Pendiente de evaluar | Actualizar |
| Werkzeug | 3.0.1 | Transitiva | GHSA-f9vj-2wh5-fj8j | Medium | 3.0.6 | Pendiente de evaluar | Actualizar |
| Jinja2 | 3.1.2 | Transitiva | GHSA-h5c8-rqwp-cp95 | Medium | 3.1.3 | Pendiente de evaluar | Actualizar |
| Jinja2 | 3.1.2 | Transitiva | GHSA-h75v-3vvj-5mfj | Medium | 3.1.4 | Pendiente de evaluar | Actualizar |
| Werkzeug | 3.0.1 | Transitiva | GHSA-hgf8-39gv-g3f2 | Medium | 3.1.4 | Pendiente de evaluar | Actualizar |
| Werkzeug | 3.0.1 | Transitiva | GHSA-29vq-49wr-vm6x | Medium | 3.1.6 | Pendiente de evaluar | Actualizar |
| Jinja2 | 3.1.2 | Transitiva | GHSA-q2x7-8rv6-6q7h | Medium | 3.1.5 | Pendiente de evaluar | Actualizar |
| Werkzeug | 3.0.1 | Transitiva | GHSA-87hc-h4r5-73f7 | Medium | 3.1.5 | Pendiente de evaluar | Actualizar |
| Jinja2 | 3.1.2 | Transitiva | GHSA-cpwx-vrp4-4pq7 | Medium | 3.1.6 | Pendiente de evaluar | Actualizar |
| Werkzeug | 3.0.1 | Transitiva | GHSA-g6x2-hccm-hh4m | Medium | 3.1.9 | Pendiente de evaluar | Actualizar |
| Jinja2 | 3.1.2 | Transitiva | GHSA-gmj6-6f8f-6699 | Medium | 3.1.5 | Pendiente de evaluar | Actualizar |
| Flask | 3.0.0 | Directa | GHSA-68rp-wp8r-4726 | Low | 3.1.3 | Pendiente de evaluar | Actualizar |

**Comparación con Dependabot (Parte I):**

Grype ha detectado 13 vulnerabilidades: una de severidad alta, once de severidad media y una de severidad baja. Dependabot no mostró alertas durante la revisión inicial; posteriormente mostró 13.

Inicialmente los resultados no coincidían; posteriormente coincidieron en número, paquetes y distribución por severidad. La causa exacta del retraso no se ha determinado.

Todas las vulnerabilidades detectadas disponen de una versión corregida.

Evidencia: [grype-antes.txt](evidencias/grype-antes.txt).

**Documento VEX (K.4):** [reportaudit.openvex.json](evidencias/reportaudit.openvex.json).

Se ha documentado CVE-2024-34069 (Werkzeug 3.0.1) con el estado `not_affected` y la justificación `vulnerable_code_not_in_execute_path`. El servicio arranca con `debug=False` en `app/servicio.py`, por lo que el depurador interactivo no está activo en el modo de ejecución previsto. Esta conclusión no se extiende a otros modos de despliegue. Se mantiene la decisión de actualizar la dependencia.

El documento JSON se ha preparado y validado según la confirmación del alumno. La validación sintáctica no demuestra por sí sola la validez semántica del VEX.

Queda pendiente evaluar individualmente los demás avisos de Grype.

---

## Parte L — Trivy: dependencias y secretos

Se ha ejecutado Trivy 0.74.0 en modo filesystem, activando los escáneres de vulnerabilidades y secretos y excluyendo los directorios `venv` y `tools`.

### Comparación de herramientas SCA

| Severidad | Dependabot | Grype | Trivy |
|---|---|---|---|
| Critical | 0 | 0 | 0 |
| High | 0 | 1 | 1 |
| Medium | 0 | 11 | 11 |
| Low | 0 | 1 | 1 |
| Total | 0 | 13 | 13 |

Grype y Trivy coinciden en el número de vulnerabilidades detectadas y en su distribución por severidad. Todas disponen de una versión corregida.

Dependabot no reportó alertas en la revisión inicial (datos de la tabla); posteriormente mostró 13 con la misma distribución por severidad. La causa del retraso sigue sin determinarse.

### Detección de secretos

Trivy no ha reportado ningún secreto en esta ejecución, a pesar de las credenciales inseguras identificadas durante la auditoría manual. El símbolo `-` del resumen indica que la categoría de secretos no se analizó para `requirements.txt`; no equivale a un resultado de cero para ese archivo.

La ausencia de hallazgos no garantiza la ausencia de vulnerabilidades. Es necesario combinar distintas herramientas de análisis con la revisión manual.

**Evidencia:** [trivy-antes.txt](evidencias/trivy-antes.txt).

---

## Parte M — Correcciones de la auditoría

**PR #19 (Issue #5):** fusionado tras revisión de Samubrr. Se aplicaron consultas SQL parametrizadas, validación de nombres y ejecución sin shell, carga YAML segura, PBKDF2-HMAC-SHA256 con sal aleatoria y variables de entorno para las credenciales; se eliminó la exposición parcial de la clave en logs. La rotación de credenciales reales queda pendiente de confirmar.

El Quality Gate inicial falló por cobertura del código nuevo del 0 % (mínimo 80 %). Se añadieron pruebas unitarias, generación de coverage.xml en CI e importación en SonarQube Cloud (commit `9792f63`). La cobertura local del módulo corregido fue del 100 % (41 sentencias y 2 ramas); pre-commit pasó. El Quality Gate de main aparece en verde.

Code scanning pasó de 10 alertas abiertas a 1 abierta y 9 cerradas. No quedan alertas abiertas de CodeQL; queda una alerta High de SonarCloud (`python:S4502`, CSRF, `app/servicio.py:25`) pendiente de corrección. La interfaz de Security Hotspots indica 0 pendientes y advierte que estos hallazgos ahora aparecen en Issues. No se ha confirmado individualmente el motivo de cierre de las nueve alertas.

**PR #20 (Issue #6):** fusionado. Flask pasó de 3.0.0 a 3.1.3, Jinja2 de 3.1.2 a 3.1.6 y Werkzeug de 3.0.1 a 3.1.9. Se verificaron las versiones instaladas y `pip check` devolvió `No broken requirements found`. Issue #6 cerrado. Dependabot muestra 0 alertas abiertas y 13 cerradas.

Los cambios SAST corrigen el código propio; las actualizaciones SCA corrigen las versiones de las dependencias. Son controles complementarios.

---

## Parte N — Antes y después

| Medida | Antes | Después |
|---|---|---|
| Hallazgos de Semgrep en `app/` | 3 hallazgos en la prueba de bloqueo (captura, p. 18; alcance de un archivo) | Passed (sin hallazgos bloqueantes) |
| Alertas abiertas de CodeQL (Security → Code scanning) | Pendiente de recuperar recuento específico | 0 |
| Alertas abiertas totales de Code scanning | 10 | 1 |
| Vulnerabilidades en SonarQube Cloud (rama main) | Pendiente de recuperar recuento | 1 alerta de seguridad (CSRF) |
| Security Hotspots por revisar en SonarQube Cloud | Pendiente de recuperar recuento | 0 (clasificación obsoleta en la interfaz) |
| Vulnerabilidades de Grype sobre el SBOM | 13 | 0 |
| Alertas abiertas de Dependabot | 13 | 0 |
| Vulnerabilidades detectadas por Trivy | 13 | 0 |
| Secretos reportados por Trivy | 0 | 0 |

Evidencias posteriores: [SBOM](evidencias/sbom-despues.cyclonedx.json), [Grype](evidencias/grype-despues.txt) (resultado: `No vulnerabilities found`) y [Trivy](evidencias/trivy-despues.txt).

---

## Preguntas de comprobación (Sección 7 de la guía)

1. Windows aloja el navegador y la interfaz de VS Code; Ubuntu (WSL2) aloja el proyecto, Git, Python, el entorno virtual y las herramientas locales. GitHub aloja el repositorio remoto, las revisiones y CI. Ubuntu proporciona un entorno Linux coherente con CI.
2. Flask es directa porque aparece en requirements.in; Werkzeug es transitiva porque Flask la requiere (`# via flask`). El SBOM inicial incluye ambas.
3. Un source es el origen de un dato y un sink es la operación sensible que lo recibe. En servicio.py, `request.args.get("cliente", "")` recibe el dato que llega a buscar_reportes_cliente; en el código original, cursor.execute ejecutaba la consulta construida con ese dato.
4. El apóstrofo de o'brien_ltd rompía la sintaxis de la consulta concatenada y producía HTTP 500 (captura, p. 7). La consulta parametrizada separa datos e instrucciones SQL.
5. Semgrep actúa antes del commit y proporciona respuesta inmediata. SonarQube Cloud y CodeQL analizan en CI y aportan reglas y perspectivas distintas; el hook local no sustituye los controles centrales.
6. No necesariamente: cada herramienta tiene reglas, alcance y técnicas distintas. Trivy no reportó los secretos observados manualmente y los resultados individuales de SAST aún no están completamente recuperados.
7. El PR #19 modificó código propio; el PR #20 actualizó dependencias. CodeQL analiza código y Dependabot compara versiones con avisos de seguridad.
8. Borrar un secreto no invalida las copias ni el historial. Hay que revocarlo o rotarlo y gestionar su sustituto fuera del código.
9. VEX registra una decisión razonada y verificable. Para CVE-2024-34069 se documentó que el depurador está desactivado en el modo previsto, sin extender la conclusión a otros despliegues; aun así se actualizó Werkzeug.
10. El instalador compara el SHA-256 calculado con el publicado antes de utilizar el binario. Esto verifica coincidencia con el artefacto esperado, pero no garantiza que el origen o el canal de publicación no estén comprometidos.
11. Pendiente de las partes O–T.
12. Pendiente de las partes O–T.
13. Pendiente de las partes O–T.
14. Pendiente de las partes O–T.
15. Pendiente de las partes O–T.
16. Pendiente de las partes O–T.
17. Pendiente de las partes O–T.

## Backlog del laboratorio (Issues)

| Issue | Título | PR o evidencia de cierre |
|---|---|---|
| #1 | Adopt an international pull request template | PR #14 |
| #2 | Run SAST (SonarQube Cloud and CodeQL) on every pull request | PR #15 |
| #3 | Block insecure commits with a Semgrep pre-commit hook | PR #16 |
| #4 | Enable Dependabot alerts and security updates | PR #17 - I.3 completado|
| #5 | Remediate the findings of the security audit | PR #19 |
| #6 | Upgrade the vulnerable dependencies | PR #20 |
| #7 | Publish the audit log and the before/after evidence | |
| #8 | Detect ReportAudit credentials in the whole Git history | |
| #9 | Make SCA and secret scanning required checks on main | |
| #10 | Publish a security policy and a private vulnerability reporting channel | |
| #11 | Release v1.0.0 with an SBOM and signed provenance | |
| #12 | Measure supply-chain maturity with OpenSSF Scorecard | Pendiente |
| #13 | Build the CRA evidence index | Pendiente |
