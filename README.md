# 🚀 AutoCommit CLI

> "La accesibilidad no es solo ajustar cosas, ¡es innovar para ser más eficientes!"

## 📖 Introducción

**AutoCommit CLI** es una herramienta de línea de comandos **avanzada** diseñada para automatizar el flujo de trabajo repetitivo de Git (`add` + `commit` + `push`) en entornos Windows, **ahora con características de seguridad empresariales**.

Nació de la necesidad real de optimizar el tiempo y reducir la carga cognitiva de escribir múltiples comandos o pelear con interfaces visuales (GUIs) que no siempre son amigables con los lectores de pantalla (NVDA, JAWS).

### 🆕 **Características Nuevas (v2.0 - Diciembre 2025)**
- ✨ **Sistema de logging automático** - Bitácora completa de todas las operaciones
- 🛡️ **Scanner de seguridad integrado** - Detecta archivos sensibles antes de subirlos
- 🔒 **Doble confirmación** - Protección contra subida accidental de credenciales
- 📊 **Trazabilidad completa** - Logs detallados para debugging y auditoría

### ¿Qué hace por ti?

* **🔍 Detecta el contexto:** Sabe si estás dentro de un repositorio o si debe ofrecerte una lista de tus proyectos.
* **🛡️ Previene desastres:** Verifica si hay conflictos remotos (`git pull`) antes de dejarte subir nada.
* **🔒 Protege tus secretos:** Escanea automáticamente archivos sensibles (.env, .key, passwords) y te alerta antes de subirlos.
* **📋 Registra todo:** Mantiene una bitácora automática de todas las operaciones en `~/.autocommit.log`.
* **🔑 Gestión Inteligente:** Se integra perfectamente con configuraciones multi-cuenta (Personal vs. Trabajo/Universidad) usando SSH.
* **⚡ Cero Fricción:** Un solo comando para gobernarlos a todos, ahora más seguro que nunca.

## 🛠️ Requisitos Previos

> **Para Novatos:** Si no tienes experiencia instalando software, sigue cada paso cuidadosamente. ¡No te preocupes, es más fácil de lo que parece!

### ✅ **Verificar si ya tienes todo instalado**
Antes de instalar nada, abre **PowerShell** o **Símbolo del sistema** (presiona `Windows + R`, escribe `cmd` y presiona Enter) y verifica:

```powershell
# Verificar Python (debe mostrar algo como "Python 3.11.x")
python --version

# Verificar Git (debe mostrar algo como "git version 2.x.x")
git --version
```

### 📋 **Lista de Requisitos**
* **🐍 Python 3.7 o superior** - El "cerebro" que ejecuta nuestro script
* **📂 Git 2.0 o superior** - Para manejar los repositorios
* **💻 Windows 10/11** - Sistema operativo compatible
* **🌐 Conexión a Internet** - Para sincronizar con GitHub/GitLab

### 🔧 **Si necesitas instalar algo:**

**Para Python:**
1. Ve a [python.org/downloads](https://python.org/downloads)
2. Descarga la versión más reciente
3. **¡IMPORTANTE!** Durante la instalación, marca la casilla **"Add Python to PATH"**

**Para Git:**
1. Ve a [git-scm.com/download](https://git-scm.com/download)
2. Descarga e instala con las opciones por defecto

## 📥 Instalación (Paso a Paso)

> **💡 Tip para Novatos:** La instalación toma aproximadamente 5-10 minutos. Lee cada paso completamente antes de ejecutarlo.

### 1. 📁 Preparar la Herramienta

**Opción A: Descarga Directa (Más Fácil)**
1. Haz clic en el botón verde **"Code"** arriba de esta página
2. Selecciona **"Download ZIP"**
3. Extrae el archivo en una carpeta fácil de recordar como:
   - `C:\Herramientas\autocommit-cli`
   - `C:\Scripts\autocommit-cli`

**Opción B: Usando Git (Recomendado si ya usas Git)**
```powershell
# Abre PowerShell y ejecuta:
git clone https://github.com/WilmerRv1989/autocommit-cli.git
cd autocommit-cli
```

### 2. ⚙️ Configurar el "Comando Mágico" (PATH)

> **¿Qué es PATH?** Es como una "libreta de direcciones" que le dice a Windows dónde encontrar programas cuando escribes su nombre en cualquier terminal.
Para ejecutar `autocommit` desde cualquier lugar sin escribir la ruta completa, debes agregarlo a las Variables de Entorno.

**📝 Pasos Detallados:**

1. **Abrir Variables de Entorno:**
   - Presiona la tecla **Windows**
   - Escribe `"Variables de entorno"` (sin las comillas)
   - Haz clic en **"Editar las variables de entorno del sistema"**
   - Si Windows te pide permisos de administrador, acepta

2. **Navegar a la configuración:**
   - En la ventana que se abre, haz clic en **"Variables de entorno"** (botón inferior)

3. **Editar PATH:**
   - En la sección **superior** (Variables de usuario), busca la fila que dice `Path`
   - Selecciónala haciendo clic sobre ella (se pondrá azul)
   - Haz clic en **"Editar..."**

4. **Agregar la ruta:**
   - Haz clic en **"Nuevo"**
   - Pega la ruta **completa** a la carpeta `src` de este proyecto
   - **Ejemplo:** `C:\Herramientas\autocommit-cli\src`
   - **⚠️ Importante:** Debe apuntar a la carpeta `src`, no a la raíz del proyecto

5. **Guardar cambios:**
   - Haz clic en **"Aceptar"** en todas las ventanas abiertas
   - **Cierra y vuelve a abrir** cualquier terminal que tengas abierta

**🧪 Verificar la instalación:**
```powershell
# Abre una nueva terminal y escribe:
autocommit
# Si ves el menú del programa, ¡está funcionando! 🎉
```

### 3. Configurar tu Carpeta de Proyectos (Opcional)
El script es inteligente y buscará tus proyectos en las carpetas más comunes (`C:\Users\TuUsuario\repos` o `source\repos`).
Si guardas tus proyectos en una ubicación personalizada, puedes configurar una Variable de Entorno:

1.  Vuelve a **Variables de entorno** > **Variables de usuario**.
2.  Clic en **Nueva...**.
3.  **Nombre:** `GIT_PROJECTS_ROOT`
4.  **Valor:** La ruta de tu carpeta de proyectos.

## 🔐 Configuración Avanzada: Multi-Cuenta con SSH
*(El secreto para gestionar cuentas Personales y de Trabajo/Universidad sin conflictos)*

Si usas múltiples cuentas de GitHub, la clave es usar SSH y un archivo config.

### Paso A: Generar tus Llaves
En una terminal (PowerShell), genera una llave para cada cuenta (dale Enter cuando pida contraseña para dejarla vacía y facilitar la automatización):

> **Nota:** Asegúrate de reemplazar los emails y nombres de los ejemplos con tus propios datos antes de copiar el código.

```powershell
# Cuenta Personal
ssh-keygen -t ed25519 -C "tu_personal@email.com" -f "$env:USERPROFILE\.ssh\id_personal"

# Cuenta Trabajo/Universidad/otras
ssh-keygen -t ed25519 -C "tu_trabajo@email.com" -f "$env:USERPROFILE\.ssh\id_trabajo"
```

### Paso B: El Archivo "Cerebro" (Config)
Ve a la carpeta `%USERPROFILE%\.ssh` y crea un archivo llamado `config` (**⚠️ IMPORTANTE:** ¡Sin extensión .txt!). Ábrelo y pega esto:

```text
# Cuenta Personal (Principal - github.com)
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_personal

# Cuenta Secundaria (Alias - github-trabajo)
Host github-trabajo
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_trabajo
```

### Paso C: Subir a GitHub
1.  Copia el contenido de los archivos `.pub` generados (`id_personal.pub`, etc.).
2.  Pégalos en **Settings > SSH and GPG keys** de la cuenta de GitHub correspondiente.

### Paso D: Conectar los Repositorios de Trabajo
Aquí ocurre la magia. Para que Git sepa qué llave usar, solo debes **cambiar el nombre del servidor** en la dirección del repositorio.

El truco es cambiar `github.com` por el alias que definiste en el archivo config (`github-trabajo`).

**Ejemplo Práctico:**
Si la URL original de tu repositorio es:
`git@github.com:Empresa/Proyecto.git`

Tú debes escribirla así:
`git@github-trabajo:Empresa/Proyecto.git`

**Comando para actualizar un repositorio existente:**
Abre la terminal dentro de la carpeta de tu proyecto de trabajo y ejecuta:

```bash
# Sintaxis: git remote set-url origin git@[TU-ALIAS]:[USUARIO]/[REPO].git

git remote set-url origin git@github-trabajo:TuUsuario/TuRepositorio.git

---

## 🚀 Uso

> **Para Novatos:** El comando `autocommit` es inteligente y se adapta a donde te encuentres. ¡No te preocupes por memorizar opciones complicadas!

### 🎯 **Uso Básico**

1. **Abre tu terminal favorita:**
   - **PowerShell** (recomendado): `Windows + X` → "Windows PowerShell"
   - **Símbolo del sistema**: `Windows + R` → escribe `cmd`
   - **Terminal en VS Code**: `Ctrl + ñ` (si usas VS Code)

2. **Ejecuta el comando:**
```bash
autocommit
```

### 🤖 **Comportamiento Inteligente**

**📍 Si estás DENTRO de un proyecto Git:**
```
✅ Repositorio detectado: mi-proyecto
🌿 Rama: main
🔄 [1/4] Verificando nube...
🛡️ [2/4] Escaneando archivos sensibles...
📄 [3/4] Cambios detectados:
M  archivo1.txt
A  archivo2.py
¿Subir cambios? (S/n):
```

**📂 Si estás FUERA de un proyecto:**
```
📂 Carpeta raíz detectada: C:\Users\TuUsuario\repos
🔍 Selecciona un proyecto de tu lista:
1. mi-web
2. app-python
3. proyecto-universidad
👉 Ingresa el número del proyecto:
```

### 🛡️ **Características de Seguridad**

**🚨 Detección de Archivos Sensibles:**
Si el programa detecta archivos como `.env`, `.key`, `password.txt`, etc.:
```
🚨 ALERTA DE SEGURIDAD 🚨
He detectado archivos que parecen contener CLAVES o SECRETOS:
   - .env
   - config/database.key

¿Estás 100% SEGURO de que quieres subir esto a Internet?
Escribe 'SI' (en mayúsculas) para confirmar, o Enter para cancelar:
```

**📋 Registro Automático:**
Todas las operaciones se guardan automáticamente en: `C:\Users\TuUsuario\.autocommit.log`

---

## 🛡️ Sistema de Seguridad Integrado

> **Nuevo en v2.0:** AutoCommit CLI ahora incluye un sistema de seguridad proactivo que te protege de errores costosos.

### 🔍 **Scanner de Archivos Sensibles**

El programa **automáticamente detecta** y te alerta sobre archivos que podrían contener información sensible:

**🚨 Patrones Detectados:**
- `.env` - Variables de entorno con secrets
- `.key`, `.pem` - Llaves criptográficas
- `config.js`, `settings.json` - Archivos de configuración
- `password`, `secret`, `token` - Cualquier archivo con estas palabras
- `id_rsa`, `credentials` - Archivos de autenticación

### 📊 **Sistema de Logging**

**📍 Ubicación del log:** `C:\Users\[TuUsuario]\.autocommit.log`

**📋 Qué se registra:**
```
2025-12-02 14:30:15 - INFO - === Iniciando sesión de AutoCommit CLI ===
2025-12-02 14:30:15 - INFO - Repositorio seleccionado: C:\repos\mi-proyecto
2025-12-02 14:30:16 - WARNING - Intento de subir archivos sensibles: ['.env']
2025-12-02 14:30:20 - INFO - Usuario autorizó manualmente subida de archivos sensibles
2025-12-02 14:30:25 - INFO - Proceso completado con éxito
```

**🔍 Para revisar el log:**
```powershell
# Ver las últimas 20 líneas
Get-Content ~\.autocommit.log -Tail 20

# Buscar errores específicos
Select-String "ERROR" ~\.autocommit.log
```

---

## 🔧 Solución de Problemas Comunes

### 🚫 Error: "gpg failed to sign the data"
**Síntoma:** Aparece este mensaje al intentar hacer commit
**Causa:** Git está configurado para firmar commits con GPG pero no tienes las llaves configuradas
**Solución:**
```bash
# Desactivar firma GPG globalmente
git config --global commit.gpgsign false
```

### 🔌 Error: "Host desconocido" al usar SSH
**Síntoma:** Error de conexión al intentar push/pull
**Causa:** Archivo de configuración SSH mal nombrado o corrupto
**Solución:**
```powershell
# Verificar archivos SSH
dir $env:USERPROFILE\.ssh

# El archivo debe llamarse exactamente 'config' (sin extensión)
# NO 'config.txt' o 'config.cfg'
```

### 📂 Error: "No se encontró carpeta de proyectos"
**Síntoma:** El programa no encuentra tus repositorios automáticamente
**Causa:** Tus proyectos están en una ubicación no estándar
**Solución:**
```powershell
# Opción 1: Crear carpeta estándar
mkdir $env:USERPROFILE\repos
# Luego mueve tus proyectos ahí

# Opción 2: Configurar ubicación personalizada
# Ve a Variables de Entorno y crea:
# Nombre: GIT_PROJECTS_ROOT
# Valor: C:\tu\carpeta\de\proyectos
```

### 🔄 Error: "autocommit no se reconoce como comando"
**Síntoma:** Windows dice que no encuentra el comando
**Causa:** PATH no configurado correctamente o terminal no reiniciada
**Solución:**
1. **Verifica la instalación:**
```powershell
# Debe existir este archivo:
Test-Path "C:\ruta\donde\instalaste\autocommit-cli\src\autocommit.bat"
```
2. **Reinicia TODAS las terminales** abiertas
3. **Verifica PATH:**
```powershell
$env:PATH -split ';' | Select-String "autocommit"
```

### 🌐 Error de conexión a Internet
**Síntoma:** Fallos en git pull/push
**Causa:** Proxy corporativo, VPN, o firewall
**Solución:**
```bash
# Si usas proxy corporativo:
git config --global http.proxy http://proxy.empresa.com:8080
git config --global https.proxy https://proxy.empresa.com:8080

# Para verificar conectividad:
ping github.com
```

## ⚠️ Casos Especiales y Errores Conocidos

El script está diseñado para detenerse ("fail-safe") si detecta algo inusual, protegiendo tu código de ser sobrescrito. Aquí te explicamos cómo solucionar los bloqueos más comunes:

### 1. El Error del "Repositorio Vacío"
**Síntoma:** Creas un repo nuevo en GitHub, corres el script y te dice: *ALERT: No se pudo actualizar el repositorio local*.
**Causa:** El script intenta bajar cambios (`git pull`), pero como el repositorio en la nube está vacío (0 commits), no encuentra nada y se detiene por seguridad.
**Solución:** Solo la primera vez, sube los archivos manualmente para crear la rama principal:
`git push -u origin main`

### 2. Error "Unrelated Histories"
**Síntoma:** Error fatal: *refusing to merge unrelated histories*.
**Causa:** Creaste un repo en GitHub con un `README` inicial y tienes otro repo en tu PC con archivos distintos. Git no sabe cómo mezclarlos porque no comparten un pasado común.
**Solución:** Fuerza la unión de ambas historias una sola vez:
`git pull origin main --allow-unrelated-histories`

### 3. Conflictos de Edición (Merge Conflict)
**Síntoma:** El script se detiene y avisa de un *CONFLICT*.
**Causa:** Tú y otra persona modificaron la misma línea del mismo archivo. Git no sabe cuál conservar.
**Solución:**
1. Abre los archivos en conflicto.
2. Decide qué código se queda y borra las marcas de Git (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Guarda y haz el commit manual: `git commit -m "Conflicto resuelto"`.

### 4. Error de Rama "Master vs Main"
**Síntoma:** Error *src refspec main does not match any*.
**Causa:** Git antiguo suele llamar a la rama `master`, pero GitHub moderno usa `main`.
**Solución:** Renombra tu rama local para modernizarla:
`git branch -M main`

---

---

## 🆘 Soporte y Ayuda

### 🐛 **Reportar Problemas**
Si encuentras algún error o tienes sugerencias:
1. Ve a la sección **[Issues](../../issues)** de este repositorio
2. Haz clic en **"New Issue"**
3. Describe tu problema con el máximo detalle posible
4. Incluye el contenido de tu archivo de log: `~/.autocommit.log`

### 💬 **Comunidad**
- **Preguntas rápidas:** Usa las **[Discussions](../../discussions)**
- **Características nuevas:** Abre un **Feature Request** en Issues
- **Mejoras de código:** Los **Pull Requests** son bienvenidos

### 📚 **Para Desarrolladores**
Si quieres contribuir al código:
```bash
# 1. Fork el repositorio
# 2. Clona tu fork
git clone https://github.com/TU-USUARIO/autocommit-cli.git

# 3. Crea una rama para tu feature
git checkout -b mi-nueva-feature

# 4. Haz tus cambios y pruébalos
python src/autocommit.py

# 5. Commit y push
git commit -m "feat: descripción de tu mejora"
git push origin mi-nueva-feature

# 6. Abre un Pull Request
```

---

## 🚀 Roadmap y Futuras Mejoras

### ✅ **Completado (v2.0 - Diciembre 2025)**
- Sistema de logging completo
- Scanner de archivos sensibles
- Protección contra subida accidental de credenciales
- Mejora en manejo de errores

### 🔄 **En Desarrollo (v2.1 - Próximamente)**
- [ ] Soporte para Linux y macOS
- [ ] Tests automatizados
- [ ] Commits semánticos automáticos
- [ ] Integración con GitHub CLI

### 🎯 **Planificado (v3.0 - Futuro)**
- [ ] Dashboard web para métricas
- [ ] Integración con Slack/Teams
- [ ] Sistema de plugins
- [ ] Análisis de código con IA

---

## ❤️ Agradecimientos

**AutoCommit CLI** ha crecido gracias a la comunidad. Agradecimientos especiales a:
- La comunidad de **accesibilidad digital** por inspirar el enfoque inclusivo
- Usuarios que reportaron bugs y sugirieron mejoras
- Contribuidores que enviaron Pull Requests

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - siéntete libre de usarlo, modificarlo y compartirlo.

**¿Qué significa esto?** Puedes:
- ✅ Usar comercialmente
- ✅ Modificar el código
- ✅ Distribuir copias
- ✅ Usar en proyectos privados
- ❗ Debes incluir el aviso de copyright

---

<div align="center">

**Desarrollado con ❤️ y mucha cafeína por [WilmerRv](https://github.com/WilmerRv1989)**

*"La automatización inteligente libera tiempo para lo que realmente importa: crear cosas increíbles"*

⭐ **Si te gusta el proyecto, dale una estrella** ⭐

</div>