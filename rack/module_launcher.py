import os
import sys
from pathlib import Path

import importlib.util
''' Launcher de modulos del rack.'''
if __name__ == "__main__":
    # Carpeta a monitorear
    modules_folder = Path(__file__).parent / "modules"
    
    if not modules_folder.exists():
        print(f"Carpeta {modules_folder} no existe")
    
    executed_modules = set()
    
    while True:
        # Obtener archivos .py en la carpeta
        py_files = set(modules_folder.glob("*.py"))
        py_files = {f for f in py_files if f.name != "__init__.py"}
        
        # Encontrar nuevos archivos
        new_modules = py_files - executed_modules
        
        for module_file in new_modules:
            try:
                print(f"Añadiendo {module_file.name} al rack...")
                spec = importlib.util.spec_from_file_location(module_file.stem, module_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                executed_modules.add(module_file)
                print(f"{module_file.name} añadido")
            except Exception as e:
                print(f"Error al añadir {module_file.name}: {e}")