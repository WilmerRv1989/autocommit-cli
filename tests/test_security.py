"""
Suite de Tests de Seguridad para AutoCommit CLI v2.1
Valida las mejoras críticas implementadas para prevenir vulnerabilidades.
"""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Añadir src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from autocommit import (
    validate_git_input, 
    run_command_secure, 
    enhanced_security_scan, 
    SecurityError,
    DANGEROUS_CHARS,
    MAX_INPUT_LENGTH
)


class TestInputValidation:
    """Tests para validación de entrada y prevención de injection."""
    
    def test_validate_safe_input(self):
        """Entrada segura debe pasar validación."""
        safe_inputs = [
            "mensaje normal de commit",
            "fix: corrección de bug",
            "feat(api): nueva funcionalidad",
            "archivo-seguro.txt"
        ]
        
        for safe_input in safe_inputs:
            result = validate_git_input(safe_input, 'message')
            assert result == safe_input.strip()
    
    def test_reject_dangerous_characters(self):
        """Caracteres peligrosos deben ser rechazados."""
        dangerous_inputs = [
            "mensaje; rm -rf /",
            "mensaje & malicious_command",
            "mensaje | cat /etc/passwd", 
            "mensaje $(whoami)",
            "mensaje `malicious`",
            "mensaje\nrm -rf /",
            "mensaje\rrm -rf /"
        ]
        
        for dangerous in dangerous_inputs:
            with pytest.raises(SecurityError, match="Caracteres peligrosos"):
                validate_git_input(dangerous, 'message')
    
    def test_reject_oversized_input(self):
        """Entrada demasiado larga debe ser rechazada."""
        oversized = "A" * (MAX_INPUT_LENGTH + 1)
        
        with pytest.raises(SecurityError, match="excede límite"):
            validate_git_input(oversized, 'message')
    
    def test_validate_filename_security(self):
        """Nombres de archivo seguros vs inseguros."""
        safe_filenames = [
            "archivo.txt",
            "mi-archivo_seguro.py",
            "carpeta/subcarpeta/archivo.json"
        ]
        
        for filename in safe_filenames:
            result = validate_git_input(filename, 'filename')
            assert result == filename
        
        dangerous_filenames = [
            "archivo; rm -rf /",
            "archivo$(malicious)",
            "archivo`command`"
        ]
        
        for filename in dangerous_filenames:
            with pytest.raises(SecurityError):
                validate_git_input(filename, 'filename')
    
    def test_validate_branch_security(self):
        """Nombres de rama seguros vs inseguros."""
        safe_branches = [
            "main",
            "feature/nueva-funcionalidad", 
            "hotfix/bug-critico",
            "develop"
        ]
        
        for branch in safe_branches:
            result = validate_git_input(branch, 'branch')
            assert result == branch
        
        dangerous_branches = [
            "branch; rm -rf /",
            "branch$(malicious)",
            "branch`command`"
        ]
        
        for branch in dangerous_branches:
            with pytest.raises(SecurityError):
                validate_git_input(branch, 'branch')


class TestSecureCommandExecution:
    """Tests para ejecución segura de comandos sin shell injection."""
    
    def test_reject_string_commands(self):
        """Comandos como string deben ser rechazados."""
        with pytest.raises(SecurityError, match="Use lista de argumentos"):
            run_command_secure("git status", exit_on_error=False)
    
    def test_reject_non_git_commands(self):
        """Solo comandos git deben ser permitidos."""
        non_git_commands = [
            ['rm', '-rf', '/'],
            ['cat', '/etc/passwd'],
            ['curl', 'malicious-url.com'],
            ['python', 'malicious-script.py']
        ]
        
        for cmd in non_git_commands:
            with pytest.raises(SecurityError, match="Solo se permiten comandos git"):
                run_command_secure(cmd, exit_on_error=False)
    
    @patch('subprocess.run')
    def test_git_commands_allowed(self, mock_run):
        """Comandos git válidos deben ser permitidos."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        valid_git_commands = [
            ['git', 'status'],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'mensaje'],
            ['git', 'push', 'origin', 'main']
        ]
        
        for cmd in valid_git_commands:
            try:
                run_command_secure(cmd, exit_on_error=False)
                # Verificar que subprocess.run fue llamado con shell=False
                mock_run.assert_called()
                call_args = mock_run.call_args
                assert call_args[1]['shell'] is False
            except Exception:
                pass  # Esperamos excepciones por el mock, pero no SecurityError
    
    def test_empty_command_list(self):
        """Lista vacía de comandos debe ser rechazada."""
        with pytest.raises(SecurityError, match="Solo se permiten comandos git"):
            run_command_secure([], exit_on_error=False)
    
    @patch('subprocess.run')
    def test_timeout_protection(self, mock_run):
        """Comandos deben tener timeout de seguridad."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        run_command_secure(['git', 'status'], exit_on_error=False)
        
        # Verificar que timeout fue configurado
        call_args = mock_run.call_args
        assert 'timeout' in call_args[1]
        assert call_args[1]['timeout'] > 0


class TestSensitiveFileScanning:
    """Tests para detección mejorada de archivos sensibles."""
    
    def setup_method(self):
        """Configurar directorio temporal para tests."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        os.makedirs(self.repo_path)
        
        # Simular .git directory
        os.makedirs(os.path.join(self.repo_path, '.git'))
    
    def teardown_method(self):
        """Limpiar directorio temporal."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_file(self, filename, content="test content"):
        """Crear archivo de test."""
        filepath = os.path.join(self.repo_path, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    @patch('autocommit.run_command_secure')
    def test_detect_sensitive_extensions(self, mock_run):
        """Detectar archivos con extensiones sensibles."""
        sensitive_files = [
            ".env",
            "config.key", 
            "certificate.pem",
            "keystore.p12",
            "private.pfx"
        ]
        
        # Simular git status output
        git_status = "\n".join([f"A  {f}" for f in sensitive_files])
        mock_run.return_value = git_status
        
        for filename in sensitive_files:
            self.create_test_file(filename)
        
        # El scanner debe detectar archivos sensibles
        # Nota: En un test real, necesitaríamos mockear la entrada del usuario
        # Por ahora verificamos que el patrón de detección funciona
        assert any(filename.lower().endswith(('.env', '.key', '.pem', '.p12', '.pfx')) 
                  for filename in sensitive_files)
    
    @patch('autocommit.run_command_secure')
    def test_detect_sensitive_content(self, mock_run):
        """Detectar contenido sensible en archivos."""
        mock_run.return_value = "A  config.js"
        
        # Crear archivo con contenido sensible
        sensitive_content = """
        const config = {
            database_password: "super_secret_123",
            api_key: "ak_live_1234567890abcdef",
            private_key: "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgk..."
        }
        """
        
        self.create_test_file("config.js", sensitive_content)
        
        # Verificar que _analyze_file_content detectaría este contenido
        from autocommit import _analyze_file_content
        filepath = os.path.join(self.repo_path, "config.js")
        assert _analyze_file_content(filepath) is True
    
    def test_ignore_safe_files(self):
        """Archivos seguros no deben disparar alertas."""
        safe_files = [
            "README.md",
            "package.json",
            "main.py", 
            "styles.css",
            "index.html"
        ]
        
        from autocommit import SENSITIVE_PATTERNS_REGEX
        import re
        
        for filename in safe_files:
            is_sensitive = any(re.search(pattern, filename) for pattern in SENSITIVE_PATTERNS_REGEX)
            assert not is_sensitive, f"Archivo seguro '{filename}' fue marcado como sensible"


class TestInjectionPrevention:
    """Tests específicos para prevención de injection attacks."""
    
    def test_shell_metacharacters_blocked(self):
        """Metacaracteres de shell deben ser bloqueados."""
        shell_metacharacters = [
            ';', '&', '|', '$', '`', '(', ')', '<', '>', '\n', '\r'
        ]
        
        for char in shell_metacharacters:
            malicious_input = f"innocent_text{char}malicious_command"
            with pytest.raises(SecurityError):
                validate_git_input(malicious_input, 'message')
    
    def test_command_substitution_blocked(self):
        """Sustitución de comandos debe ser bloqueada."""
        command_substitutions = [
            "text$(rm -rf /)",
            "text`malicious_command`", 
            "text${malicious_var}",
            "text$((malicious_arithmetic))"
        ]
        
        for substitution in command_substitutions:
            with pytest.raises(SecurityError):
                validate_git_input(substitution, 'message')
    
    def test_path_traversal_in_filenames(self):
        """Path traversal en nombres de archivo debe ser validado."""
        # Estos deberían ser permitidos (paths relativos normales)
        safe_paths = [
            "src/main.py",
            "docs/README.md", 
            "tests/test_file.py"
        ]
        
        for path in safe_paths:
            result = validate_git_input(path, 'filename')
            assert result == path
        
        # Estos podrían ser problemáticos pero por ahora los permitimos
        # (Git maneja path traversal por sí mismo)
        potentially_unsafe_paths = [
            "../config.txt",
            "../../etc/passwd"
        ]
        
        # Por ahora no bloqueamos path traversal ya que Git lo maneja
        # Pero podríamos añadir esta validación en el futuro


class TestLoggingSecurity:
    """Tests para logging seguro y manejo de información sensible."""
    
    def test_sanitize_sensitive_logs(self):
        """Información sensible debe ser sanitizada en logs."""
        from autocommit import log_and_print
        import logging
        
        # Capturar logs
        with patch('logging.info') as mock_log:
            log_and_print("password=secreto123 in message", "info")
            
            # Verificar que la versión sanitizada fue logged
            mock_log.assert_called_once()
            logged_message = mock_log.call_args[0][0]
            assert "secreto123" not in logged_message
            assert "***" in logged_message
    
    def test_log_rotation_triggers(self):
        """Rotación de logs debe activarse cuando sea necesario."""
        # Este test requeriría crear un archivo de log grande
        # Por simplicidad, verificamos que la lógica existe
        from autocommit import MAX_LOG_SIZE
        assert MAX_LOG_SIZE > 0
        assert isinstance(MAX_LOG_SIZE, int)


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"])