"""
Analisis de simulaciones CST para el informe de avance.

Por cada subcarpeta de Simulaciones2026/ genera:
  - cst_barrido_<material>.png   : S11 para cada z_recipiente (barrido parametrico)
  - cst_validacion_<material>.png: S11 simulado (z mas profundo) vs medicion real
                                   (solo si hay patron registrado en measurements/)

Uso:
    python analisis_simulaciones.py

Las figuras se guardan en results/24-06-26/.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import ScalarFormatter

import data_procesing as dp

# ── Rutas ─────────────────────────────────────────────────────────────────────

BASE     = Path(__file__).resolve().parent.parent
SIM_BASE = BASE.parent / "Simulaciones2026"
MEAS_24  = BASE / "measurements" / "24-06-26"
MEAS_23  = BASE / "measurements" / "15-11-23"
OUT_DIR  = BASE / "plots"
# ── Mapeo carpeta de simulacion → archivo de medicion real ────────────────────
# Cada entrada es una Path completa al archivo medido.
# Si una carpeta no tiene patron, no se genera la figura de validacion.
# Verificar con el compañero si Simulacion_Alchol es isopropilico o etilico.

PATRON = {
    "Simulacion_Agua_Destilada": MEAS_24 / "AGUA DEST.s1p",
    "Simulaciones_Aire":         MEAS_24 / "AIRE.s1p",
    "Simulacion_Alchol":         MEAS_24 / "ALC_ISOPR.s1p",   # confirmar
    "Simulaciones_Agua":         MEAS_23 / "Agua.s1p",         # agua comun vs medicion 15-11-23
}

# Carpetas a ignorar (simulaciones obsoletas o archivos sueltos)
IGNORAR = set()   # ninguna excluida por ahora

# Rango de frecuencias de interes: 10 MHz – 2 GHz
F_MIN = 10e6
F_MAX = 2000e6


# ── Funciones auxiliares ──────────────────────────────────────────────────────

def extraer_z(path: Path) -> int:
    with open(path) as f:
        for line in f:
            if "z_recipiente" in line:
                return int(line.split("z_recipiente=")[1].split("}")[0].split(";")[0].strip())
    return 0


def recortar(data: dict):
    frec = data["Frec"]
    s11  = data["Complex"]
    mask = (frec >= F_MIN) & (frec <= F_MAX)
    return frec[mask], s11[mask]



def estilo_eje(ax, ylabel: str, leyenda=True):
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Frecuencia (MHz)")
    ax.grid(True, which="major", linewidth=0.8)
    ax.grid(True, which="minor", linewidth=0.3)
    if leyenda:
        ax.legend(fontsize=9)


def titulo_limpio(nombre_carpeta: str) -> str:
    return nombre_carpeta.replace("Simulacion_", "").replace("Simulaciones_", "").replace("_", " ")


# ── Descubrir subcarpetas de simulacion ───────────────────────────────────────

carpetas = sorted([
    d for d in SIM_BASE.iterdir()
    if d.is_dir() and d.name not in IGNORAR
])

if not carpetas:
    print(f"No se encontraron carpetas en {SIM_BASE}")
    raise SystemExit(1)

print(f"Carpetas encontradas: {[c.name for c in carpetas]}\n")

cmap = plt.cm.plasma


# ── Procesar cada carpeta ─────────────────────────────────────────────────────

for carpeta in carpetas:
    archivos = sorted(carpeta.glob("*.s1p"))
    if not archivos:
        print(f"  [{carpeta.name}] Sin archivos .s1p — salteando.")
        continue

    material = titulo_limpio(carpeta.name)
    slug     = carpeta.name.lower().replace(" ", "_")

    # Leer todos los archivos y ordenar por z_recipiente
    sims = []
    for f in archivos:
        data = dp.vna_proc_file(str(carpeta), f.name)
        z    = extraer_z(f)
        sims.append((z, data))
    sims.sort(key=lambda x: x[0])   # de z mas superficial a mas profundo

    zvals   = [z for z, _ in sims]
    colores = [cmap(i / max(len(zvals) - 1, 1)) for i in range(len(zvals))]

    print(f"[{carpeta.name}]  z simulados: {zvals}")

    # ── Figura 1: barrido parametrico ─────────────────────────────────────────

    fig1, (ax_re, ax_im) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig1.suptitle(
        f"Barrido paramétrico — z_recipiente\n"
        f"Sonda coaxial 21 mm | {material} | Simulación CST",
        fontsize=11
    )

    for color, (z, data) in zip(colores, sims):
        frec, s11 = recortar(data)
        frec_MHz  = frec / 1e6
        ax_re.plot(frec_MHz, np.real(s11), color=color, lw=1.5, label=f"z = {z} mm")
        ax_im.plot(frec_MHz, np.imag(s11), color=color, lw=1.5, label=f"z = {z} mm")

    estilo_eje(ax_re, "Re(S₁₁)")
    estilo_eje(ax_im, "Im(S₁₁)")
    fig1.tight_layout()

    salida1 = OUT_DIR / f"cst_barrido_{slug}.png"
    fig1.savefig(salida1, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {salida1.name}")
    plt.close(fig1)

    # ── Figura 2: validacion vs medicion real (si hay patron) ─────────────────

    ruta_medido = PATRON.get(carpeta.name)

    if ruta_medido is None:
        print(f"  Sin patron registrado para '{carpeta.name}' — se omite figura de validacion.")
        continue

    if not ruta_medido.exists():
        print(f"  Patron '{ruta_medido.name}' no encontrado en {ruta_medido.parent.name}/ — se omite figura de validacion.")
        continue

    # Simulacion mas estable: z mas profundo (ultimo de la lista ordenada)
    z_ref, sim_ref = sims[-1]

    med = dp.vna_proc_file(str(ruta_medido.parent), ruta_medido.name)
    frec_med, s11_med = recortar(med)

    sim_alin  = dp.Resample_S11(
        {"Frec": frec_med,         "Complex": s11_med},
        {"Frec": sim_ref["Frec"],  "Complex": sim_ref["Complex"]}
    )
    s11_sim = np.array(sim_alin["Complex"])
    frec_MHz = frec_med / 1e6

    fig2, (ax_re2, ax_im2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig2.suptitle(
        f"Validación del modelo CST — S₁₁ simulado vs. medido\n"
        f"{material} | Sonda coaxial 21 mm | z = {z_ref} mm",
        fontsize=11
    )

    ax_re2.plot(frec_MHz, np.real(s11_med), "b-",  lw=1.5, label="Medido (VNA)")
    ax_re2.plot(frec_MHz, np.real(s11_sim), "r--", lw=1.5, label=f"Simulado CST (z = {z_ref} mm)")
    ax_im2.plot(frec_MHz, np.imag(s11_med), "b-",  lw=1.5, label="Medido (VNA)")
    ax_im2.plot(frec_MHz, np.imag(s11_sim), "r--", lw=1.5, label=f"Simulado CST (z = {z_ref} mm)")

    estilo_eje(ax_re2, "Re(S₁₁)")
    estilo_eje(ax_im2, "Im(S₁₁)")
    fig2.tight_layout()

    salida2 = OUT_DIR / f"cst_validacion_{slug}.png"
    fig2.savefig(salida2, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {salida2.name}")
    plt.close(fig2)

print("\nListo.")
