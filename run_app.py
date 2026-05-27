import os
import sys
import platform
import subprocess
import venv
from pathlib import Path

DIRECTORIO_VENV = '.venv'
ARCHIVO_PRINCIPAL = 'buscador.py'
ARCHIVO_EXTRACTOR = 'extractor.py'
ARCHIVO_DB = 'db.json'
ARCHIVO_REQUISITOS = 'requirements.txt'


def ejecutable_python():
    if platform.system().lower() == 'windows':
        return os.path.join(DIRECTORIO_VENV, 'Scripts', 'python.exe')
    return os.path.join(DIRECTORIO_VENV, 'bin', 'python')


def preparar_entorno():
    python = ejecutable_python()
    if not os.path.isfile(python):
        print("Creando entorno virtual...")
        venv.create(DIRECTORIO_VENV, with_pip=True)
        subprocess.run(
            [python, '-m', 'pip', 'install', '--upgrade', 'pip'],
            check=True, capture_output=True
        )

    if os.path.exists(ARCHIVO_REQUISITOS):
        print("Instalando dependencias...")
        subprocess.run(
            [python, '-m', 'pip', 'install', '-r', ARCHIVO_REQUISITOS],
            check=True
        )


def ejecutar_extractor() -> None:
    if not os.path.exists(ARCHIVO_EXTRACTOR):
        print(f"[!] No se encuentra {ARCHIVO_EXTRACTOR}")
        sys.exit(1)
    preparar_entorno()
    subprocess.run([ejecutable_python(), ARCHIVO_EXTRACTOR], check=True)


def asegurar_base_datos(python: str) -> None:
    if os.path.exists(ARCHIVO_DB):
        return
    if not os.path.exists(ARCHIVO_EXTRACTOR):
        return
    print("No existe db.json. Ejecutando extractor...")
    subprocess.run([python, ARCHIVO_EXTRACTOR], check=True)


def principal():
    os.chdir(Path(__file__).parent)

    if len(sys.argv) > 1 and sys.argv[1] in ("extract", "extractor", "--extract"):
        try:
            ejecutar_extractor()
        except KeyboardInterrupt:
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            if e.returncode not in (130, -2):
                print(f"[!] Error: {e}")
                sys.exit(1)
        return

    if not os.path.exists(ARCHIVO_PRINCIPAL):
        print(f"[!] No se encuentra {ARCHIVO_PRINCIPAL}")
        sys.exit(1)

    try:
        preparar_entorno()
        python = ejecutable_python()
        asegurar_base_datos(python)
        subprocess.run([python, ARCHIVO_PRINCIPAL], check=True)
    except KeyboardInterrupt:
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        if e.returncode not in (130, -2):
            print(f"[!] Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    principal()
