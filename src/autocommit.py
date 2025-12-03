import os
import subprocess
import sys
import logging
from datetime import datetime

# --- CONFIGURACIÓN DE LOGS (Bitácora) ---
# Guarda un historial en la carpeta de usuario (ej: C:\Users\mi_usuario\.autocommit.log)
LOG_FILE = os.path.join(os.path.expanduser("~"), ".autocommit.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# --- CONFIGURACIÓN INTELIGENTE DE RUTAS ---
def get_projects_root():
    """Busca la carpeta de proyectos en ubicaciones comunes."""
    env_root = os.getenv("GIT_PROJECTS_ROOT")
    if env_root and os.path.exists(env_root): return env_root
    
    user_home = os.path.expanduser("~")
    possible_paths = [
        os.path.join(user_home, "repos"),
        os.path.join(user_home, "source", "repos"),
        os.path.join(user_home, "Projects")
    ]
    for path in possible_paths:
        if os.path.exists(path): return path
    return None

ROOT_PROJECTS_DIR = get_projects_root()

# --- LISTA NEGRA DE SEGURIDAD ---
# Archivos que nunca deberían subirse sin doble confirmación
SENSITIVE_PATTERNS = [
    ".env", "config.js", "secrets", "credentials", 
    ".pem", ".key", "id_rsa", "password", "token"
]

def log_and_print(msg, level="info"):
    """Imprime en pantalla y guarda en el log al mismo tiempo."""
    if level == "info":
        print(msg)
        logging.info(msg)
    elif level == "error":
        print(f"❌ {msg}")
        logging.error(msg)
    elif level == "warning":
        print(f"⚠️ {msg}")
        logging.warning(msg)

def run_command(command, cwd=None, exit_on_error=True):
    """Ejecuta comandos de sistema de forma segura."""
    try:
        logging.debug(f"Ejecutando: {command} en {cwd}")
        result = subprocess.run(
            command, cwd=cwd, shell=True, check=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip()
        logging.error(f"Fallo en comando '{command}': {err_msg}")
        
        if exit_on_error:
            print(f"\n❌ ERROR CRÍTICO: {command}")
            print(f"   Detalle: {err_msg}")
            
            if "conflict" in err_msg.lower():
                log_and_print("Diagnóstico: Conflictos de fusión detectados.", "warning")
            elif "permission denied" in err_msg.lower():
                log_and_print("Diagnóstico: Error de permisos SSH.", "warning")
            
            sys.exit(1)
        return None

def check_security(repo_path):
    """
    Escanea los archivos modificados en busca de nombres peligrosos.
    Retorna True si es seguro proceder, False si el usuario cancela.
    """
    status_output = run_command("git status --porcelain", cwd=repo_path, exit_on_error=False)
    if not status_output: return True

    suspicious_files = []
    for line in status_output.splitlines():
        # Formato porcelain: "M  archivo.txt" o "?? archivo.txt"
        filename = line[3:].strip()
        for pattern in SENSITIVE_PATTERNS:
            if pattern in filename.lower():
                suspicious_files.append(filename)
                break
    
    if suspicious_files:
        print("\n🚨 ALERTA DE SEGURIDAD 🚨")
        print("He detectado archivos que parecen contener CLAVES o SECRETOS:")
        for f in suspicious_files:
            print(f"   - {f}")
        
        logging.warning(f"Intento de subir archivos sensibles: {suspicious_files}")
        print("\n¿Estás 100% SEGURO de que quieres subir esto a Internet?")
        confirm = input("Escribe 'SI' (en mayúsculas) para confirmar, o Enter para cancelar: ")
        
        if confirm != "SI":
            log_and_print("Operación cancelada por protocolo de seguridad.", "warning")
            return False
            
        logging.info("Usuario autorizó manualmente subida de archivos sensibles.")
    
    return True

# ... (Funciones de soporte is_git_repo, get_current_branch, select_project se mantienen igual) ...
def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def get_current_branch(repo_path):
    return run_command("git branch --show-current", cwd=repo_path)

def select_project():
    if not ROOT_PROJECTS_DIR:
        log_and_print("No se encontró carpeta de proyectos raíz.", "error")
        return None

    repos = [d for d in os.listdir(ROOT_PROJECTS_DIR) 
             if os.path.isdir(os.path.join(ROOT_PROJECTS_DIR, d)) and is_git_repo(os.path.join(ROOT_PROJECTS_DIR, d))]
    
    if not repos:
        print("No hay repositorios disponibles.")
        return None

    print(f"\n📂 Raíz: {ROOT_PROJECTS_DIR}")
    for i, repo in enumerate(repos):
        print(f"{i + 1}. {repo}")
    
    try:
        selection = input("\n👉 Número: ")
        if selection.isdigit() and 0 <= int(selection)-1 < len(repos):
            return os.path.join(ROOT_PROJECTS_DIR, repos[int(selection)-1])
    except ValueError:
        pass
    return None

def main():
    logging.info("=== Iniciando sesión de AutoCommit CLI ===")
    current_dir = os.getcwd()
    
    if is_git_repo(current_dir):
        target_repo = current_dir
        print(f"✅ Repositorio detectado: {os.path.basename(current_dir)}")
    else:
        target_repo = select_project()

    if not target_repo:
        sys.exit(1)

    logging.info(f"Repositorio seleccionado: {target_repo}")
    branch = get_current_branch(target_repo)
    print(f"🌿 Rama: {branch}")

    # 1. ACTUALIZACIÓN (Pull)
    print("\n🔄 [1/4] Verificando nube...")
    if run_command(f"git pull origin {branch}", cwd=target_repo, exit_on_error=False) is None:
        log_and_print("Fallo en actualización (Pull). Revisa conflictos.", "error")
        sys.exit(1)

    # 2. SEGURIDAD (Scanner)
    if not check_security(target_repo):
        sys.exit(1)

    # 3. ESTADO
    status = run_command("git status --porcelain", cwd=target_repo)
    if not status:
        print("\n✨ [2/4] Todo limpio.")
        logging.info("Repositorio limpio, finalizando.")
        sys.exit(0)

    print("\n📄 [2/4] Cambios detectados:")
    print(status)
    
    if input("¿Subir cambios? (S/n): ").lower() == 'n':
        logging.info("Cancelado por usuario.")
        sys.exit(0)

    # 4. SUBIDA
    print("\n📦 [3/4] Empaquetando...")
    run_command("git add .", cwd=target_repo)
    
    msg = input("✍️  Mensaje (Enter para default): ")
    if not msg.strip(): msg = "Update via AutoCommit CLI"
    
    run_command(f'git commit -m "{msg}"', cwd=target_repo)
    
    print(f"\n🚀 [4/4] Subiendo a {branch}...")
    run_command(f"git push origin {branch}", cwd=target_repo)
    
    log_and_print("Proceso completado con éxito.")

if __name__ == "__main__":
    main()