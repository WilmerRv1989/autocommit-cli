import os
import subprocess
import sys

# --- CONFIGURACIÓN automatizada ---
def get_projects_root():
    """
    Busca la carpeta de proyectos en ubicaciones comunes automáticamente.
    Prioridad:
    1. Variable de entorno 'GIT_PROJECTS_ROOT' (Configuración manual)
    2. Carpeta 'repos' en el usuario actual (Ej: C:\Users\mi_usuario\repos)
    3. Carpeta 'source\repos' (Estándar de Visual Studio)
    4. Carpeta 'Projects' (Común en Mac/Linux)
    """
    # 1. Revisar variable de entorno
    env_root = os.getenv("GIT_PROJECTS_ROOT")
    if env_root and os.path.exists(env_root):
        return env_root
    
    # 2. Revisar rutas comunes
    user_home = os.path.expanduser("~")
    possible_paths = [
        os.path.join(user_home, "repos"),          # Tu configuración actual
        os.path.join(user_home, "source", "repos"), # Visual Studio
        os.path.join(user_home, "Projects"),        # Genérico
        os.path.join(user_home, "Desarrollo")       # Genérico ES
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

# Detectamos la raíz al iniciar
ROOT_PROJECTS_DIR = get_projects_root()

def run_command(command, cwd=None, exit_on_error=True):
    """
    Ejecuta comandos de sistema de forma segura y maneja errores.
    Retorna la salida limpia del comando.
    """
    try:
        # Ejecuta el comando capturando stdout y stderr
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if exit_on_error:
            print(f"\n❌ ERROR CRÍTICO AL EJECUTAR: {command}")
            print(f"   Detalle técnico: {e.stderr.strip()}")
            
            # Ayuda contextual para errores comunes
            err_msg = e.stderr.lower()
            if "conflict" in err_msg or "rejected" in err_msg:
                print("\n⚠️  DIAGNÓSTICO: Tienes conflictos con la versión en línea.")
                print("   ACCIÓN: Ejecuta 'git pull' manualmente y resuelve los conflictos en el código.")
            elif "permission denied" in err_msg or "publickey" in err_msg:
                print("\n⚠️  DIAGNÓSTICO: Problema de permisos SSH.")
                print("   ACCIÓN: Verifica tus llaves SSH y el archivo 'config'.")
            
            sys.exit(1)
        return None

def is_git_repo(path):
    """Verifica si la carpeta contiene un subdirectorio .git"""
    return os.path.isdir(os.path.join(path, ".git"))

def get_current_branch(repo_path):
    """Obtiene el nombre de la rama actual (main, master, develop, etc.)"""
    return run_command("git branch --show-current", cwd=repo_path)

def select_project():
    """
    Muestra un menú interactivo si el script se ejecuta fuera de un repositorio.
    """
    if not ROOT_PROJECTS_DIR:
        print(f"\n⚠️  ATENCIÓN: No se encontró ninguna carpeta de proyectos común.")
        print("   Buscamos en 'repos', 'source/repos' y 'Projects' dentro de tu usuario.")
        print("\n   SOLUCIÓN RÁPIDA: Crea una carpeta llamada 'repos' en tu usuario")
        print("   O configura la variable de entorno 'GIT_PROJECTS_ROOT'.")
        return None

    # Escanea la carpeta raíz buscando repositorios git
    repos = [d for d in os.listdir(ROOT_PROJECTS_DIR) 
             if os.path.isdir(os.path.join(ROOT_PROJECTS_DIR, d)) and is_git_repo(os.path.join(ROOT_PROJECTS_DIR, d))]
    
    if not repos:
        print(f"No se encontraron repositorios git en {ROOT_PROJECTS_DIR}")
        return None

    print(f"\n📂 Carpeta raíz detectada: {ROOT_PROJECTS_DIR}")
    print("🔍 Selecciona un proyecto de tu lista:")
    for i, repo in enumerate(repos):
        print(f"{i + 1}. {repo}")
    
    try:
        selection = input("\n👉 Ingresa el número del proyecto: ")
        if not selection.isdigit(): return None
        choice = int(selection) - 1
        if 0 <= choice < len(repos):
            return os.path.join(ROOT_PROJECTS_DIR, repos[choice])
    except ValueError:
        pass
    return None

def main():
    current_dir = os.getcwd()
    
    # --- FASE 1: IDENTIFICACIÓN ---
    if is_git_repo(current_dir):
        target_repo = current_dir
        print(f"✅ Repositorio detectado: {os.path.basename(current_dir)}")
    else:
        target_repo = select_project()

    if not target_repo:
        print("❌ Operación cancelada o ruta inválida.")
        sys.exit(1)

    print(f"\n🚀 Iniciando AutoFlow en: {target_repo}")
    branch = get_current_branch(target_repo)
    print(f"🌿 Rama activa: {branch}")
    
    # --- FASE 2: SINCRONIZACIÓN PREVIA (Seguridad) ---
    print("\n🔄 [1/4] Verificando cambios remotos (git pull)...")
    # exit_on_error=False permite manejar el error nosotros mismos
    pull_result = run_command(f"git pull origin {branch}", cwd=target_repo, exit_on_error=False)
    
    if pull_result is None:
        print("\n🛑 ALTO: La actualización falló.")
        print("   Es probable que existan conflictos de fusión (merge conflicts).")
        print("   El script se detendrá para proteger tus archivos locales.")
        sys.exit(1)
    else:
        print("   ✅ Sincronización exitosa.")

    # --- FASE 3: VERIFICACIÓN DE ESTADO ---
    status = run_command("git status --porcelain", cwd=target_repo)
    if not status:
        print("\n✨ [2/4] El repositorio está limpio. No hay cambios para subir.")
        sys.exit(0)

    print("\n📄 [2/4] Archivos modificados pendientes:")
    print("--------------------------------")
    print(status)
    print("--------------------------------")
    
    confirm = input("¿Deseas subir estos cambios ahora? (S/n): ").lower()
    if confirm == 'n':
        print("Operación cancelada por el usuario.")
        sys.exit(0)

    # --- FASE 4: EMPAQUETADO Y SUBIDA ---
    print("\n📦 [3/4] Agregando archivos al área de preparación (staging)...")
    run_command("git add .", cwd=target_repo)
    
    msg = input("✍️  Mensaje para el commit (Enter para default): ")
    if not msg.strip(): 
        msg = "Actualización automática via AutoFlow CLI"
    
    # Intentamos hacer commit. Manejamos error si no hay nada que commitear (raro pero posible)
    run_command(f'git commit -m "{msg}"', cwd=target_repo)
    
    print(f"\n🚀 [4/4] Subiendo cambios a GitHub ({branch})...")
    run_command(f"git push origin {branch}", cwd=target_repo)
    
    print("\n✅ ¡ÉXITO! Tu repositorio está actualizado.")

if __name__ == "__main__":
    main()