"""Caja de búsqueda minimalista sobre db.json."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont, messagebox

import visor

ARCHIVO_DB = Path(__file__).parent / "db.json"
ANCHO = 600
ALTO_COMPACTO = 70
ALTO_EXPANDIDO = 340
COLOR_ENLACE = "#6eb5ff"
MAX_RESULTADOS = 200


class Buscador:
    def __init__(self) -> None:
        self.expandido = False
        self.coincidencias: list[dict] = []
        self.registro_por_tag: dict[str, dict] = {}
        self._timer_clic: str | None = None

        self.root = tk.Tk()
        self.root.title("Buscar")
        self.root.geometry(f"{ANCHO}x{ALTO_COMPACTO}")
        self.root.minsize(400, ALTO_COMPACTO)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")

        self.marco = tk.Frame(self.root, bg="#1e1e1e", padx=8, pady=8)
        self.marco.pack(fill=tk.BOTH, expand=True)

        fuente = tkfont.nametofont("TkDefaultFont")
        try:
            fuente.configure(size=12)
        except tk.TclError:
            pass

        self.entrada = tk.Entry(
            self.marco,
            font=fuente,
            bg="#2d2d2d",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.entrada.pack(fill=tk.X)
        self.entrada.bind("<Return>", self._buscar)

        self.ayuda = tk.Label(
            self.marco,
            text="",
            font=fuente,
            bg="#1e1e1e",
            fg="#888888",
            anchor="w",
        )

        self.resultados = tk.Text(
            self.marco,
            font=fuente,
            bg="#252526",
            fg="#d4d4d4",
            relief=tk.FLAT,
            wrap=tk.WORD,
            cursor="hand2",
            height=12,
            padx=4,
            pady=4,
        )
        self.resultados.tag_configure(
            "enlace", foreground=COLOR_ENLACE, underline=True
        )
        self.resultados.tag_configure("texto", foreground="#d4d4d4")
        self.resultados.bind("<Button-1>", self._al_clic_resultado)
        self.resultados.bind("<Double-Button-1>", self._copiar_seleccion)
        self.resultados.bind("<Key>", lambda _e: "break")

        self.root.bind("<Escape>", lambda _e: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.datos = self._cargar_db()
        self.entrada.focus_set()

    def _cargar_db(self) -> list[dict]:
        if not ARCHIVO_DB.exists():
            return []
        with open(ARCHIVO_DB, encoding="utf-8") as f:
            return json.load(f)

    def _buscar(self, _event: tk.Event | None = None) -> None:
        consulta = self.entrada.get().strip()
        if not consulta:
            return

        palabras = consulta.lower().split()
        self.coincidencias = [
            registro
            for registro in self.datos
            if all(palabra in registro["texto"].lower() for palabra in palabras)
        ]

        if not self.expandido:
            self.expandido = True
            self.ayuda.pack(fill=tk.X, pady=(6, 0))
            self.resultados.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
            self.root.geometry(f"{ANCHO}x{ALTO_EXPANDIDO}")

        self.ayuda.config(
            text="Clic en el enlace: abrir archivo · Doble clic: copiar texto"
        )
        self._mostrar_resultados()

    def _mostrar_resultados(self) -> None:
        self.resultados.config(state=tk.NORMAL)
        self.resultados.delete("1.0", tk.END)
        self.registro_por_tag.clear()

        if not self.coincidencias:
            self.resultados.insert(tk.END, "(sin coincidencias)", "texto")
            return

        for indice, registro in enumerate(self.coincidencias[:MAX_RESULTADOS]):
            vista = registro["texto"]
            if len(vista) > 90:
                vista = vista[:87] + "..."
            enlace = f"{registro['archivo']}  p.{registro['pagina']}"
            tag = f"r{indice}"
            self.registro_por_tag[tag] = registro
            self.resultados.insert(tk.END, enlace, ("enlace", tag))
            self.resultados.insert(tk.END, f" — {vista}\n", "texto")

        if len(self.coincidencias) > MAX_RESULTADOS:
            restantes = len(self.coincidencias) - MAX_RESULTADOS
            self.resultados.insert(
                tk.END, f"\n... y {restantes} coincidencias más\n", "texto"
            )

    def _registro_en_clic(self, event: tk.Event) -> dict | None:
        indice = self.resultados.index(f"@{event.x},{event.y}")
        for tag in self.resultados.tag_names(indice):
            if tag.startswith("r") and tag in self.registro_por_tag:
                return self.registro_por_tag[tag]
        return None

    def _al_clic_resultado(self, event: tk.Event) -> None:
        if self._timer_clic is not None:
            self.root.after_cancel(self._timer_clic)
        self._timer_clic = self.root.after(
            250, lambda e=event: self._clic_simple(e)
        )

    def _clic_simple(self, event: tk.Event) -> None:
        self._timer_clic = None
        registro = self._registro_en_clic(event)
        if registro is None:
            return
        self._abrir_registro(registro)

    def _abrir_registro(self, registro: dict) -> None:
        archivo = registro["archivo"]
        if visor.abrir_en_pagina(archivo, registro["pagina"]):
            return
        if visor.ruta_temario(archivo) is None:
            messagebox.showerror(
                "Archivo no encontrado",
                f"No está en temarios/:\n{archivo}",
                parent=self.root,
            )
        else:
            messagebox.showerror(
                "No se pudo abrir",
                f"No hay visor disponible para:\n{archivo}",
                parent=self.root,
            )

    def _copiar_seleccion(self, event: tk.Event) -> None:
        if self._timer_clic is not None:
            self.root.after_cancel(self._timer_clic)
            self._timer_clic = None
        registro = self._registro_en_clic(event)
        if registro is None:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(registro["texto"])

    def ejecutar(self) -> None:
        self.root.mainloop()


def main() -> None:
    if not ARCHIVO_DB.exists():
        print("No existe db.json. Ejecuta: python run_app.py extract")
        return
    Buscador().ejecutar()


if __name__ == "__main__":
    main()
