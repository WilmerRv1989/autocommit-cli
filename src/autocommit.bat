@echo off
:: Lanzador para AutoCommit CLI
:: %~dp0 es una variable mágica que significa "la carpeta donde está este archivo"
:: Esto asegura que siempre encuentre el script .py, sin importar dónde instales la herramienta.
python "%~dp0autocommit.py" %*