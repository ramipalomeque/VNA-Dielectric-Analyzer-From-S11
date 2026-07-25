import sys
from pathlib import Path
import data_procesing as dp
import utilities as utl
import modelos as mdls
# ============================================================================
# Inicio
# ============================================================================

if len(sys.argv) != 2:
    print("Uso: python main.py <fecha>")
    print("Ejemplo: python main.py 24-11-26")
    sys.exit(1)

measurement_date = utl.parse_measurement_date(sys.argv[1])

ROOT_DIR = Path(__file__).resolve().parent.parent

measurement_path = ROOT_DIR / "measurements" / measurement_date
result_path = ROOT_DIR / "results" / measurement_date

result_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Validacion de archivos 
# ============================================================================

required_files = {
    "aire": "AIRE.s1p",
    "short": "SHORT.s1p",
    "agua_dest": "AGUA DEST.s1p",
    "alc_isp": "ALC_ISOPR.s1p"
}

files = required_files.copy()

# Validar archivos obligatorios
for file_name in required_files.values():
    if not (measurement_path / file_name).exists():
        raise FileNotFoundError(f"No se encontró {file_name}")

print("Iniciando procesamiento para mediciones del dia " + measurement_date)
# Buscar muestras
samples = [
    f.name
    for f in measurement_path.glob("*.s1p")
    if f.name not in required_files.values()
]

if len(samples) == 0:
    raise ValueError("No se encontraron archivos de muestra.")

print(f"Se encontraron {len(samples)} muestras:")
for sample in samples:
    print(f" - {sample}")

# ============================================================================
# Lectura de archivos de referencia
# ============================================================================

s11_aire = dp.vna_proc_file(measurement_path, files["aire"])
s11_agua_dest = dp.vna_proc_file(measurement_path, files["agua_dest"])
s11_short = dp.vna_proc_file(measurement_path, files["short"])
s11_isopropilico = dp.vna_proc_file(measurement_path, files["alc_isp"])

# ============================================================================
# Lectura de muestras
# ============================================================================

s11_muestras = []

for sample in samples:
    s11_muestras.append({
        "name": Path(sample).stem.lower(),
        "data": dp.vna_proc_file(measurement_path, sample)
        })

print("Obtencion de s11 de muestras completada.")

# ============================================================================
# Cálculo de permitividad del material usando agua como referencia.
# ============================================================================

er_muestras = []
frecs      = s11_agua_dest['Frec']
er_agua    = dp.get_er_DUTm (
                frecs,
                s11_agua_dest['Complex'], 
                s11_agua_dest['Complex'], 
                s11_aire['Complex'], 
                s11_short['Complex'])

er_alc_isopr = dp.get_er_DUTm (
                frecs, 
                s11_isopropilico['Complex'], 
                s11_agua_dest['Complex'], 
                s11_aire['Complex'], 
                s11_short['Complex'])

for s11_muestra in s11_muestras:
    er_muestras.append({
        'name': s11_muestra['name'],
        'er': dp.get_er_DUTm (
                frecs, 
                s11_muestra['data']['Complex'], 
                s11_agua_dest['Complex'], 
                s11_aire['Complex'], 
                s11_short['Complex'])
    }) 

print("Calculo de permitividades completado.")

# ============================================================================
# Cálculo de permitividad del material usando agua y alcohol isopropílico como referencia.
# ============================================================================
er_muestras_calibradas = []
er_agua_calibrada = dp.get_er_setup(
                        frecs, 
                        s11_agua_dest['Complex'], 
                        s11_agua_dest['Complex'], 
                        s11_aire['Complex'], 
                        s11_isopropilico['Complex'], 
                        s11_short['Complex'])

for s11_muestra in s11_muestras:
    er_muestras_calibradas.append({
        'name': s11_muestra['name'],
        'er': dp.get_er_setup(
                frecs, 
                s11_muestra['data']['Complex'], 
                s11_agua_dest['Complex'], 
                s11_aire['Complex'], 
                s11_isopropilico['Complex'], 
                s11_short['Complex'])
    }) 

print("Calculo de permitividades completado.")
# ============================================================================
# Guardado de resultados
# ============================================================================

utl.export_er_to_excel(frecs, er_agua, er_muestras, result_path / "permitividades.xlsx")
utl.export_er_to_excel(frecs, er_agua_calibrada, er_muestras_calibradas, result_path / "permitividades_calibradas.xlsx")

print("Resultados guardados en " + str(result_path))

# ============================================================================
# Gráfico
# ============================================================================

utl.plot_er_comparison(
    frecs,
    er_agua,
    "DUT",
    er_agua_calibrada,
    "DUT Calibrado",
    "Real and Imaginary Parts of Er Agua",
    result_path / "er_agua.png"
)
utl.plot_er_comparison(
    frecs,
    er_alc_isopr,
    "DUT",
    mdls.get_er_pat_alc_isopropilico(frecs),
    "DUT Teorico",
    "Real and Imaginary Parts of Er Alcohol Isopropilico",
    result_path / "er_agua_calibrada.png"
)

for muestra, muestra_calibrada in zip(er_muestras, er_muestras_calibradas):
    utl.plot_er_comparison(
        frecs,
        muestra["er"],
        "DUT",
        muestra_calibrada["er"],
        "DUT Calibrado",
        f"Real and Imaginary Parts of Er {muestra['name']}",
        result_path / f"er_{muestra['name']}.png"
    )
    # SOLO si tengo una unica muestra y se que es alcohol etilico
    utl.plot_er_comparison(
            frecs,
            muestra["er"],
            "DUT",
            mdls.get_er_pat_alc_etilico(frecs),
            "DUT Teorico",
            f"Real and Imaginary Parts of Er {muestra['name']}",
            result_path / f"er_{muestra['name']}.png"
        )



utl.show_plots()

print("Gráficos guardados en " + str(result_path))



