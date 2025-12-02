# 🚀 AutoCommit CLI

> "La accesibilidad no es solo ajustar cosas, ¡es innovar para ser más eficientes!"

## 📖 Introducción

**AutoCommit CLI** es una herramienta de línea de comandos diseñada para automatizar el flujo de trabajo repetitivo de Git (`add` + `commit` + `push`) en entornos Windows.

Nació de la necesidad real de optimizar el tiempo y reducir la carga cognitiva de escribir múltiples comandos o pelear con interfaces visuales (GUIs) que no siempre son amigables con los lectores de pantalla (NVDA, JAWS).

### ¿Qué hace por ti?

* **Detecta el contexto:** Sabe si estás dentro de un repositorio o si debe ofrecerte una lista de tus proyectos.
* **Previene desastres:** Verifica si hay conflictos remotos (`git pull`) antes de dejarte subir nada.
* **Gestión Inteligente:** Se integra perfectamente con configuraciones multi-cuenta (Personal vs. Trabajo/Universidad) usando SSH.
* **Cero Fricción:** Un solo comando para gobernarlos a todos.

## 🛠️ Requisitos Previos

* **Python 3.x** instalado.
* **Git** instalado y accesible desde la consola (`git --version`).
* **Sistema Operativo:** Windows 10/11.

## 📥 Instalación (Paso a Paso)

### 1. Preparar la Herramienta
Clona este repositorio o descarga los archivos en una carpeta segura, por ejemplo: `C:\Scripts` o `C:\Herramientas`.

### 2. Configurar el "Comando Mágico" (PATH)
Para ejecutar `autocommit` desde cualquier lugar sin escribir la ruta completa, debes agregarlo a las Variables de Entorno.

1.  Presiona la tecla **Windows**, escribe "Variables de entorno" y entra en **"Editar las variables de entorno del sistema"**.
2.  Clic en el botón **Variables de entorno**.
3.  En la sección de arriba (**Variables de usuario**), busca la fila `Path` y selecciónala.
4.  Selecciona el botón **Editar**.
5.  Selecciona  **Nuevo** y pega la ruta de la carpeta `src` de este proyecto (Ejemplo: `C:\Scripts\autocommit-cli\src`).
6.  Acepta todas las ventanas.

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

Simplemente abre tu terminal (CMD, PowerShell, Terminal de VS Code) y escribe:

```bash
autocommit
```

* **Si estás dentro de un proyecto:** Iniciará el proceso de sincronización, te pedirá mensaje y subirá los cambios.
* **Si estás fuera:** Te mostrará una lista numerada de tus repositorios para que elijas cuál actualizar.

---

## 🔧 Solución de Problemas Comunes

### Error: "gpg failed to sign the data"
Si Git se queja de firmas GPG y no tienes las llaves configuradas, desactívalo globalmente:
```bash
git config --global commit.gpgsign false
```

### Error: "Host desconocido" al usar SSH
Asegúrate de que tu archivo `config` en la carpeta `.ssh` no tenga la extensión `.txt`. Debe llamarse estrictamente `config`. Puedes verificarlo en la consola con:
```powershell
dir %USERPROFILE%\.ssh
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

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - siéntete libre de usarlo, modificarlo y compartirlo.

Desarrollado con ❤️ y mucha cafeína por WilmerRv