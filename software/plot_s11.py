from pathlib import Path
import data_processing as dp
import utilities as utl

from pathlib import Path

def read_cst_parameters(file_path):

    parameters = {}

    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("! Parameters"):
                text = line.split("{", 1)[1].split("}", 1)[0]

                for item in text.split(";"):
                    key, value = item.strip().split("=")
                    parameters[key] = float(value)

                break

    return parameters


#folder = Path(r"D:\VNA-Dielectric-Analyzer-From-S11\measurements\Simulaciones_CST\Simulacion_Acohol_Isopropilico")
#folder = Path(r"D:\VNA-Dielectric-Analyzer-From-S11\measurements\Simulaciones_CST\Simulacion_Agua_Destialada")
folder = Path(r"D:\VNA-Dielectric-Analyzer-From-S11\measurements\Simulaciones_CST\Simulacion_04082026")
file_ref = Path(r"D:\VNA-Dielectric-Analyzer-From-S11\measurements\24-06-26\AGUA DEST.s1p")
file_ref2 = Path(r"D:\VNA-Dielectric-Analyzer-From-S11\measurements\02-08-26\Sonda-Coaxial_21mm_DisifixB_v2_Agua_Dest.s1p" )
s11s = []
frecs = None

for file in folder.glob("*.s1p"):

    data = dp.vna_proc_file(file)
    parameters = read_cst_parameters(file)

    if frecs is None:
        frecs = data["Frec"]

    s11s.append({
        "name": f"z_recipiente = {parameters['z_recipiente']} mm",
        "s11": data["Complex"]
    })

s11s.append({
    "name": "referencia",
    "s11": dp.vna_proc_file(file_ref)["Complex"]
})



utl.plot_s11_list(
    frecs,
    s11s,
    #"S11 - Simulaciones " + folder.name.replace("Simulaciones_", ""),
    "S11 - Simulaciones agua destilada",
    folder / "s11_comparacion.png"
)




utl.show_plots()