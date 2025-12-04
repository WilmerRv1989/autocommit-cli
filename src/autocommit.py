import os
import subprocess
import sys
import logging
import shlex
import re
from datetime import datetime
from pathlib import Path

# --- CONFIGURACIÓN DE LOGS SEGURA ---
LOG_FILE = os.path.join(os.path.expanduser("~"), ".autocommit.log")
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

def setup_secure_logging():
    """Configura logging seguro con rotación automática."""
    # Verificar y rotar log si es necesario
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        backup_log = f"{LOG_FILE}.backup"
        if os.path.exists(backup_log):
            os.remove(backup_log)
        os.rename(LOG_FILE, backup_log)
    
    # Configurar logging
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8',
        filemode='a'  # Append mode
    )
    
    # Log inicial de sesión con versión
    logging.info("=== AutoCommit CLI v2.1 Security Hardened - Iniciando sesión ===")
    logging.info(f"Python: {sys.version}, OS: {os.name}")

# Inicializar logging seguro
setup_secure_logging()

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

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Patrones mejorados para detección de archivos sensibles (case-insensitive, regex)
SENSITIVE_PATTERNS_REGEX = [
    r'(?i)\.(env|key|pem|p12|pfx|crt|cer)$',  # Extensiones peligrosas
    r'(?i).*(password|secret|token|credential|api[_-]?key).*',  # Palabras clave
    r'(?i)id_(rsa|dsa|ecdsa|ed25519).*',  # Llaves SSH
    r'(?i).*(config|settings)\.(js|json|yaml|yml)$',  # Archivos de configuración
    r'(?i).*(backup|dump|sql).*\.(sql|bak|dump)$',  # Backups de BD
    r'(?i)\.(p12|pfx|keystore|jks)$'  # Keystores
]

# Límites de seguridad
MAX_INPUT_LENGTH = 1000
COMMAND_TIMEOUT = 30  # segundos
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# Caracteres peligrosos para shell injection
DANGEROUS_CHARS = {';', '&', '|', '$', '`', '(', ')', '<', '>', '\n', '\r'}

class SecurityError(Exception):
    """Excepción para errores de seguridad"""
    pass

def log_and_print(msg, level="info"):
    """Imprime en pantalla y guarda en el log de forma segura."""
    # Sanitizar mensaje para logs (remover información sensible)
    safe_msg = re.sub(r'(password|token|key)([=:]\s*)(\S+)', r'\1\2***', msg, flags=re.IGNORECASE)
    
    if level == "info":
        print(msg)
        logging.info(safe_msg)
    elif level == "error":
        print(f"❌ {msg}")
        logging.error(safe_msg)
    elif level == "warning":
        print(f"⚠️ {msg}")
        logging.warning(safe_msg)
    elif level == "debug":
        # Debug solo a logs, no a pantalla
        logging.debug(safe_msg)

def validate_git_input(user_input, input_type='message'):
    """Valida y sanitiza entrada de usuario para prevenir injection attacks."""
    if not isinstance(user_input, str):
        raise SecurityError(f"Input debe ser string, recibido: {type(user_input)}")
    
    # Verificar longitud
    if len(user_input) > MAX_INPUT_LENGTH:
        raise SecurityError(f"{input_type} excede límite de {MAX_INPUT_LENGTH} caracteres")
    
    # Verificar caracteres peligrosos
    dangerous_found = [char for char in DANGEROUS_CHARS if char in user_input]
    if dangerous_found:
        raise SecurityError(f"Caracteres peligrosos detectados en {input_type}: {dangerous_found}")
    
    # Validación específica por tipo
    if input_type == 'filename':
        # Validar nombres de archivo seguros
        if not re.match(r'^[\w\-_./\\\s]+$', user_input):
            raise SecurityError(f"Nombre de archivo contiene caracteres no permitidos: {user_input}")
    
    elif input_type == 'branch':
        # Validar nombres de rama Git válidos
        if not re.match(r'^[\w\-_./]+$', user_input):
            raise SecurityError(f"Nombre de rama contiene caracteres no permitidos: {user_input}")
    
    return user_input.strip()

def run_command_secure(cmd_parts, cwd=None, exit_on_error=True):
    """Ejecuta comandos Git de forma segura sin shell injection."""
    if isinstance(cmd_parts, str):
        raise SecurityError("Use lista de argumentos, no string para prevenir shell injection")
    
    # Validar que el primer argumento sea git
    if not cmd_parts or cmd_parts[0] != 'git':
        raise SecurityError(f"Solo se permiten comandos git, intentado: {cmd_parts}")
    
    try:
        # Log del comando (sin datos sensibles)
        safe_cmd = ['git'] + ['***' if 'password' in str(arg).lower() else str(arg) for arg in cmd_parts[1:]]
        logging.debug(f"Ejecutando comando seguro: {safe_cmd} en {cwd}")
        
        result = subprocess.run(
            cmd_parts,
            cwd=cwd,
            shell=False,  # CRÍTICO: Nunca usar shell=True
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=COMMAND_TIMEOUT  # Prevenir comandos colgados
        )
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        error_msg = f"Comando excedió timeout de {COMMAND_TIMEOUT}s"
        logging.error(error_msg)
        if exit_on_error:
            log_and_print(error_msg, "error")
            sys.exit(1)
        return None
        
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip()
        logging.error(f"Fallo en comando {cmd_parts}: {err_msg}")
        
        if exit_on_error:
            print(f"\n❌ ERROR CRÍTICO: {' '.join(cmd_parts)}")
            print(f"   Detalle: {err_msg}")
            
            if "conflict" in err_msg.lower():
                log_and_print("Diagnóstico: Conflictos de fusión detectados.", "warning")
            elif "permission denied" in err_msg.lower():
                log_and_print("Diagnóstico: Error de permisos SSH.", "warning")
            elif "not a git repository" in err_msg.lower():
                log_and_print("Diagnóstico: Directorio no es un repositorio Git.", "warning")
            
            sys.exit(1)
        return None
    
    except Exception as e:
        error_msg = f"Error inesperado ejecutando comando: {e}"
        logging.error(error_msg)
        if exit_on_error:
            log_and_print(error_msg, "error")
            sys.exit(1)
        return None

def enhanced_security_scan(repo_path):
    """
    Escanea archivos modificados con patrones regex mejorados y análisis de contenido.
    Retorna True si es seguro proceder, False si el usuario cancela.
    """
    try:
        status_output = run_command_secure(['git', 'status', '--porcelain'], cwd=repo_path, exit_on_error=False)
        if not status_output: 
            return True

        suspicious_files = []
        high_risk_files = []
        
        for line in status_output.splitlines():
            # Formato porcelain: "M  archivo.txt" o "?? archivo.txt"
            if len(line) < 4:
                continue
                
            filename = line[3:].strip()
            
            # Validar nombre de archivo seguro
            try:
                validate_git_input(filename, 'filename')
            except SecurityError:
                high_risk_files.append(f"{filename} (caracteres peligrosos)")
                continue
            
            # Verificar contra patrones regex mejorados
            for pattern in SENSITIVE_PATTERNS_REGEX:
                if re.search(pattern, filename):
                    risk_level = "ALTO" if any(word in filename.lower() for word in ['key', 'password', 'secret']) else "MEDIO"
                    suspicious_files.append(f"{filename} (riesgo {risk_level})")
                    break
            
            # Análisis adicional de contenido para archivos nuevos/modificados
            if line.startswith(('A ', 'M ')) and os.path.exists(os.path.join(repo_path, filename)):
                if _analyze_file_content(os.path.join(repo_path, filename)):
                    suspicious_files.append(f"{filename} (contenido sospechoso)")
        
        # Mostrar alertas por nivel de riesgo
        if high_risk_files:
            print("\n🔴 ALERTA CRÍTICA DE SEGURIDAD 🔴")
            print("Archivos con caracteres PELIGROSOS detectados:")
            for f in high_risk_files:
                print(f"   - {f}")
            logging.error(f"Archivos con caracteres peligrosos: {high_risk_files}")
            log_and_print("Operación BLOQUEADA por seguridad crítica.", "error")
            return False
        
        if suspicious_files:
            print("\n🟡 ALERTA DE SEGURIDAD 🟡")
            print("Archivos que parecen contener CLAVES, SECRETOS o CONFIGURACIONES:")
            for f in suspicious_files:
                print(f"   - {f}")
            
            logging.warning(f"Archivos sensibles detectados: {suspicious_files}")
            
            # Confirmación más estricta
            print("\n⚠️  ATENCIÓN: Subir estos archivos puede exponer información sensible.")
            print("¿Estás ABSOLUTAMENTE SEGURO de que es seguro subirlos?")
            
            for attempt in range(3):  # Máximo 3 intentos
                confirm = input(f"Escribe 'CONFIRMO' (exacto, intento {attempt+1}/3): ")
                if confirm == "CONFIRMO":
                    logging.info(f"Usuario confirmó subida de archivos sensibles tras {attempt+1} intentos")
                    return True
                elif confirm == "":
                    log_and_print("Operación cancelada por el usuario.", "warning")
                    return False
                else:
                    print(f"❌ Respuesta incorrecta: '{confirm}'. Debe escribir exactamente 'CONFIRMO'")
            
            log_and_print("Operación cancelada tras 3 intentos fallidos.", "warning")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error durante escaneo de seguridad: {e}")
        log_and_print(f"Error en escaneo de seguridad: {e}", "error")
        return False

def _analyze_file_content(filepath):
    """Analiza contenido de archivo en busca de patrones sospechosos."""
    try:
        # Solo analizar archivos de texto pequeños
        if os.path.getsize(filepath) > 1024 * 1024:  # 1MB límite
            return False
            
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # Primeros 10KB
            
            # Patrones de contenido sospechoso
            suspicious_patterns = [
                r'(?i)(password|pwd)\s*[=:]\s*[^\s]{3,}',
                r'(?i)(api[_-]?key|token)\s*[=:]\s*[^\s]{10,}',
                r'(?i)(secret|private[_-]?key)\s*[=:]\s*[^\s]{5,}',
                r'-----BEGIN\s+(PRIVATE\s+KEY|CERTIFICATE)',
                r'(?i)(mysql|postgres|mongodb)://.*:.*@'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, content):
                    return True
                    
    except Exception:
        pass  # Si no se puede leer, asumir seguro
    
    return False

# ... (Funciones de soporte is_git_repo, get_current_branch, select_project se mantienen igual) ...
def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def get_current_branch(repo_path):
    """Obtiene la rama actual de forma segura."""
    branch = run_command_secure(['git', 'branch', '--show-current'], cwd=repo_path)
    if branch:
        # Validar nombre de rama
        try:
            validate_git_input(branch, 'branch')
            return branch
        except SecurityError as e:
            logging.error(f"Nombre de rama inválido: {e}")
            raise SecurityError(f"Rama actual tiene nombre inseguro: {branch}")
    return branch

def select_project():
    """Selecciona proyecto de forma segura con validación de entrada."""
    if not ROOT_PROJECTS_DIR:
        log_and_print("No se encontró carpeta de proyectos raíz.", "error")
        return None

    try:
        repos = [d for d in os.listdir(ROOT_PROJECTS_DIR) 
                 if os.path.isdir(os.path.join(ROOT_PROJECTS_DIR, d)) and is_git_repo(os.path.join(ROOT_PROJECTS_DIR, d))]
    except (OSError, PermissionError) as e:
        log_and_print(f"Error accediendo a directorio de proyectos: {e}", "error")
        return None
    
    if not repos:
        print("No hay repositorios Git disponibles.")
        return None

    print(f"\n📂 Raíz detectada: {ROOT_PROJECTS_DIR}")
    print("🔍 Repositorios disponibles:")
    for i, repo in enumerate(repos):
        print(f"{i + 1}. {repo}")
    
    # Validación de entrada mejorada
    for attempt in range(3):
        try:
            selection = input(f"\n👉 Ingresa el número del proyecto (1-{len(repos)}, intento {attempt+1}/3): ").strip()
            
            if not selection:
                print("❌ Selección vacía. Intenta de nuevo.")
                continue
                
            if not selection.isdigit():
                print(f"❌ '{selection}' no es un número válido.")
                continue
                
            choice = int(selection) - 1
            if 0 <= choice < len(repos):
                selected_path = os.path.abspath(os.path.join(ROOT_PROJECTS_DIR, repos[choice]))
                logging.info(f"Usuario seleccionó repositorio: {selected_path}")
                return selected_path
            else:
                print(f"❌ Número fuera de rango. Debe estar entre 1 y {len(repos)}.")
                
        except ValueError:
            print(f"❌ Error procesando '{selection}'. Debe ser un número.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Selección cancelada por el usuario")
            return None
    
    log_and_print("Selección de proyecto cancelada tras 3 intentos.", "warning")
    return None

def main():
    """Función principal con seguridad mejorada."""
    try:
        current_dir = os.getcwd()
        
        # Validar directorio actual
        if not os.path.exists(current_dir):
            raise SecurityError("Directorio actual no existe o no es accesible")
        
        if is_git_repo(current_dir):
            target_repo = current_dir
            print(f"✅ Repositorio detectado: {os.path.basename(current_dir)}")
        else:
            target_repo = select_project()

        if not target_repo:
            logging.info("No se seleccionó repositorio, finalizando.")
            sys.exit(1)

        # Validar que el target_repo es seguro
        target_repo = os.path.abspath(target_repo)  # Normalizar path
        logging.info(f"Repositorio seleccionado: {target_repo}")
        
        # Obtener rama actual de forma segura
        try:
            branch = get_current_branch(target_repo)
            if not branch:
                raise SecurityError("No se pudo determinar la rama actual")
            print(f"🌿 Rama: {branch}")
        except SecurityError as e:
            log_and_print(f"Error de seguridad con la rama: {e}", "error")
            sys.exit(1)

        # 1. ACTUALIZACIÓN (Pull) - Comando seguro
        print("\n🔄 [1/4] Verificando cambios remotos...")
        try:
            pull_result = run_command_secure(['git', 'pull', 'origin', branch], cwd=target_repo, exit_on_error=False)
            if pull_result is None:
                log_and_print("Fallo en actualización (Pull). Revisa conflictos.", "error")
                sys.exit(1)
            print("   ✅ Sincronización exitosa")
        except Exception as e:
            log_and_print(f"Error durante git pull: {e}", "error")
            sys.exit(1)

        # 2. SEGURIDAD (Scanner mejorado)
        print("\n🛡️ [2/4] Escaneando seguridad...")
        if not enhanced_security_scan(target_repo):
            logging.info("Proceso cancelado por escaneo de seguridad")
            sys.exit(1)
        print("   ✅ Escaneo de seguridad completado")

        # 3. VERIFICAR ESTADO
        status = run_command_secure(['git', 'status', '--porcelain'], cwd=target_repo)
        if not status:
            print("\n✨ [3/4] Repositorio limpio, nada que subir.")
            logging.info("Repositorio limpio, finalizando normalmente.")
            sys.exit(0)

        print("\n📄 [3/4] Cambios detectados:")
        print(status)
        
        # Confirmación de usuario
        try:
            confirm = input("\n¿Subir estos cambios? (S/n): ").strip().lower()
            if confirm == 'n' or confirm == 'no':
                logging.info("Proceso cancelado por el usuario.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n\nProceso interrumpido por el usuario.")
            logging.info("Proceso interrumpido con Ctrl+C")
            sys.exit(0)

        # 4. PREPARACIÓN Y SUBIDA
        print("\n📦 [4/4] Preparando y subiendo cambios...")
        
        # Git add de forma segura
        run_command_secure(['git', 'add', '.'], cwd=target_repo)
        print("   ✅ Archivos agregados al staging area")
        
        # Solicitar mensaje de commit con validación
        try:
            msg = input("✍️  Mensaje para el commit (Enter para default): ").strip()
            if not msg:
                msg = "Update via AutoCommit CLI v2.1 (Security Hardened)"
            
            # Validar mensaje de commit
            msg = validate_git_input(msg, 'message')
            
        except SecurityError as e:
            log_and_print(f"Mensaje de commit inseguro: {e}", "error")
            msg = "Update via AutoCommit CLI v2.1 (Security Hardened)"  # Fallback seguro
            print(f"   ⚠️  Usando mensaje seguro por defecto: {msg}")
        
        # Commit seguro
        run_command_secure(['git', 'commit', '-m', msg], cwd=target_repo)
        print("   ✅ Commit creado exitosamente")
        
        # Push seguro
        run_command_secure(['git', 'push', 'origin', branch], cwd=target_repo)
        print(f"   ✅ Cambios subidos a {branch}")
        
        log_and_print("✅ Proceso completado exitosamente con seguridad mejorada.")
        
    except SecurityError as e:
        log_and_print(f"Error de seguridad: {e}", "error")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        logging.info("Proceso interrumpido con Ctrl+C")
        sys.exit(0)
    except Exception as e:
        log_and_print(f"Error inesperado: {e}", "error")
        sys.exit(1)
    finally:
        logging.info("=== Finalizando sesión de AutoCommit CLI ===")

if __name__ == "__main__":
    main()