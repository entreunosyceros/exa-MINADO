"""Abre PDF/DOCX del temario en la página indicada."""

import os
import platform
import shutil
import subprocess
import webbrowser
from pathlib import Path

CARPETA_TEMARIOS = Path(__file__).parent / "temarios"


def ruta_temario(archivo: str) -> Path | None:
    ruta = CARPETA_TEMARIOS / archivo
    return ruta if ruta.is_file() else None


def abrir_en_pagina(archivo: str, pagina: int) -> bool:
    ruta = ruta_temario(archivo)
    if ruta is None:
        return False

    pagina = max(1, int(pagina))
    sistema = platform.system().lower()
    extension = ruta.suffix.lower()

    if extension == ".pdf":
        return _abrir_pdf(ruta, pagina, sistema)
    if extension == ".docx":
        return _abrir_docx(ruta, pagina, sistema)
    return _abrir_generico(ruta, sistema)


def _abrir_pdf(ruta: Path, pagina: int, sistema: str) -> bool:
    ruta_s = str(ruta.resolve())
    if sistema == "windows":
        return _abrir_pdf_windows(ruta_s, pagina)
    if sistema == "darwin":
        return _abrir_pdf_macos(ruta_s, pagina)
    return _abrir_pdf_linux(ruta, pagina)


def _abrir_pdf_linux(ruta: Path, pagina: int) -> bool:
    ruta_s = str(ruta.resolve())
    comandos = [
        ["evince", f"--page-label={pagina}", ruta_s],
        ["okular", ruta_s, "-p", str(pagina)],
        ["atril", ruta_s, "--page-label", str(pagina)],
        ["zathura", "-P", str(pagina), ruta_s],
    ]
    for comando in comandos:
        if shutil.which(comando[0]):
            _lanzar(comando)
            return True

    uri = f"{ruta.as_uri()}#page={pagina}"
    if shutil.which("xdg-open"):
        _lanzar(["xdg-open", uri])
        return True

    webbrowser.open(uri)
    return True


def _abrir_pdf_windows(ruta_s: str, pagina: int) -> bool:
    sumatra = (
        shutil.which("SumatraPDF")
        or shutil.which("SumatraPDF.exe")
        or os.path.expandvars(r"%LOCALAPPDATA%\SumatraPDF\SumatraPDF.exe")
    )
    if sumatra and Path(sumatra).is_file():
        _lanzar([sumatra, "-page", str(pagina), ruta_s])
        return True

    acrobat = Path(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe")
    if acrobat.is_file():
        _lanzar([str(acrobat), "/A", f"page={pagina}", ruta_s])
        return True

    os.startfile(ruta_s)
    return True


def _abrir_pdf_macos(ruta_s: str, pagina: int) -> bool:
    _lanzar(["open", ruta_s])
    return True


def _abrir_docx(ruta: Path, pagina: int, sistema: str) -> bool:
    """Abre el DOCX; la página del índice es orientativa en Word/LibreOffice."""
    ruta_s = str(ruta.resolve())
    if sistema == "windows":
        os.startfile(ruta_s)
        return True
    if sistema == "darwin":
        _lanzar(["open", ruta_s])
        return True
    if shutil.which("xdg-open"):
        _lanzar(["xdg-open", ruta_s])
        return True
    webbrowser.open(ruta.as_uri())
    return True


def _abrir_generico(ruta: Path, sistema: str) -> bool:
    ruta_s = str(ruta.resolve())
    if sistema == "windows":
        os.startfile(ruta_s)
        return True
    if sistema == "darwin":
        _lanzar(["open", ruta_s])
        return True
    if shutil.which("xdg-open"):
        _lanzar(["xdg-open", ruta_s])
        return True
    webbrowser.open(ruta.as_uri())
    return True


def _lanzar(comando: list[str]) -> None:
    subprocess.Popen(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
