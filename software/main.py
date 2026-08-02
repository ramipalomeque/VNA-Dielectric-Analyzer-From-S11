import argparse
from pathlib import Path
import data_processing as dp
import utilities as utl
import modelos as mdls
from shutil import copy2



def get_s11_references(messurement_path):

    air_path = messurement_path / "AIRE.s1p"
    short_path = messurement_path / "SHORT.s1p"
    agua_dest_path = messurement_path / "AGUA DEST.s1p"
    alc_isp_path = messurement_path / "ALC_ISOPR.s1p"
    alc_eth_path = messurement_path / "ALC_ETH.s1p"

    s11_references = {
        "aire": dp.vna_proc_file(air_path),
        "short": dp.vna_proc_file(short_path),
        "agua_dest": dp.vna_proc_file(agua_dest_path),
        "alc_isp": dp.vna_proc_file(alc_isp_path),
    }

    source = Path(alc_eth_path)
    if source.exists():
        s11_references["alc_eth"] = dp.vna_proc_file(alc_eth_path)

    return s11_references


# ============================================================================
# Argumentos
# ============================================================================
def parse_arguments():

    parser = argparse.ArgumentParser(description="VNA Dielectric Analyzer")
    parser.add_argument("date", help="Fecha de medición. Ejemplo: 24-11-26")
    parser.add_argument("--air", help="Ruta del archivo AIRE.s1p")
    parser.add_argument("--short", help="Ruta del archivo SHORT.s1p")
    parser.add_argument("--water", help="Ruta del archivo AGUA DEST.s1p")
    parser.add_argument("--iso", help="Ruta del archivo ALC_ISOPR.s1p")
    parser.add_argument("--sample", help="Ruta del archivo de muestra")
    return parser.parse_args()

# ============================================================================
# Inicio
# ============================================================================

def main():
    plot_er     = False
    plot_s11    = False
    save_s11    = True
    save_er     = False

    args = parse_arguments()

    measurement_date = utl.parse_measurement_date(args.date)
    ROOT_DIR = Path(__file__).resolve().parent.parent

    reference_path = ROOT_DIR / "measurements" / "24-06-26"
    result_path = ROOT_DIR / "results" / measurement_date 

    result_path.mkdir(parents=True, exist_ok=True)
    template_path = ROOT_DIR / "results" / "template.xlsx"
    result_s11= result_path / f"S11_{measurement_date}.xlsx"
    result_er= result_path / f"ER_{measurement_date}.xlsx"


    # ============================================================================
    # Validacion de archivos 
    # ============================================================================

    sources_files = {
        "aire": args.air,
        "short": args.short,
        "agua_dest": args.water,
        "alc_isp": args.iso,
        "sample": args.sample,
    }

    for key, source in sources_files.items():
        source = Path(source)
        if not source.exists():
            raise ValueError(f"El archivo {key} es obligatorio.")
    
    # ============================================================================
    # Lectura de archivos de referencia
    # ============================================================================
    s11_data = {
        "aire": dp.vna_proc_file(sources_files["aire"]),
        "short": dp.vna_proc_file(sources_files["short"]),
        "agua_dest": dp.vna_proc_file(sources_files["agua_dest"]),
        "alc_isp": dp.vna_proc_file(sources_files["alc_isp"]),
        "sample": dp.vna_proc_file(sources_files["sample"]),
    }

    s11_references = get_s11_references(reference_path)
    
    # ============================================================================
    # Cálculo de permitividad del material usando agua como referencia.
    # ============================================================================

    frecs = s11_data['agua_dest']['Frec']
    frecs_ref = s11_references['agua_dest']['Frec']

    er_agua = dp.get_er_DUTm (
                frecs,
                s11_data['agua_dest']['Complex'], 
                s11_data['agua_dest']['Complex'], 
                s11_data['aire']['Complex'], 
                s11_data['short']['Complex']
                )
    er_alc_isp = dp.get_er_DUTm (
                frecs,
                s11_data['alc_isp']['Complex'], 
                s11_data['agua_dest']['Complex'], 
                s11_data['aire']['Complex'], 
                s11_data['short']['Complex']
                )
    er_sample = dp.get_er_DUTm (
                frecs,
                s11_data['sample']['Complex'], 
                s11_data['agua_dest']['Complex'], 
                s11_data['aire']['Complex'], 
                s11_data['short']['Complex']
                )

    er_agua_ref = dp.get_er_DUTm (
                frecs_ref,
                s11_references['agua_dest']['Complex'], 
                s11_references['agua_dest']['Complex'], 
                s11_references['aire']['Complex'], 
                s11_references['short']['Complex']
    )
    er_alc_isp_ref = dp.get_er_DUTm (
                frecs_ref,
                s11_references['alc_isp']['Complex'], 
                s11_references['agua_dest']['Complex'], 
                s11_references['aire']['Complex'], 
                s11_references['short']['Complex']
    )
    er_sample_ref = dp.get_er_DUTm (
                frecs_ref,
                s11_references['alc_eth']['Complex'], 
                s11_references['agua_dest']['Complex'], 
                s11_references['aire']['Complex'], 
                s11_references['short']['Complex']
    )

    print("Calculo de permitividades con agua de referencia completado.")

    # ============================================================================
    # Cálculo de permitividad del material usando agua y alcohol isopropílico como referencia.
    # ============================================================================
    er_sample_cal = dp.get_er_setup (
                frecs,
                s11_data['sample']['Complex'], 
                s11_data['agua_dest']['Complex'], 
                s11_data['aire']['Complex'],
                s11_data['alc_isp']['Complex'], 
                s11_data['short']['Complex']                
    )
    er_sample_cal_ref = dp.get_er_setup (
                frecs_ref,
                s11_references['alc_eth']['Complex'],
                s11_references['agua_dest']['Complex'],
                s11_references['aire']['Complex'],
                s11_references['alc_isp']['Complex'],
                s11_references['short']['Complex']
    )

    er_sample_cal2 = dp.get_er_setup2 (
                frecs,
                s11_data['sample']['Complex'], 
                s11_data['agua_dest']['Complex'], 
                s11_data['aire']['Complex'],
                s11_data['alc_isp']['Complex'], 
                s11_data['short']['Complex']                
    )
    er_sample_cal_ref2 = dp.get_er_setup2 (
                frecs_ref,
                s11_references['alc_eth']['Complex'],
                s11_references['agua_dest']['Complex'],
                s11_references['aire']['Complex'],
                s11_references['alc_isp']['Complex'],
                s11_references['short']['Complex']
    )

    print("Calculo de permitividades con agua y alcohol isopropílico de referencia completado.")
    # ============================================================================
    # Guardado de resultados
    # ============================================================================
    import pandas as pd
    if save_s11:
        
        wb = utl.open_workbook(template_path)
        for name, data in s11_data.items():
            utl.export_complex_to_excel(
                data["Frec"],
                data["Complex"],
                f"S11 {name}",
                wb,
            )
        for name, data in s11_references.items():
            utl.export_complex_to_excel(
                data["Frec"],
                data["Complex"],
                f"S11_ref {name}",
                wb,
            )
        utl.save_workbook(result_s11,wb)
        utl.close_workbook(wb)
        print(f"Parametros S11 guardados en {result_s11}")

    if save_er:
        with pd.ExcelWriter(result_er, engine="openpyxl") as writer:
            utl.export_complex_to_excel(
            frecs,
            er_agua,
            "ER agua",
            writer,
            )
            utl.export_complex_to_excel(
                frecs,
                er_alc_isp,
                "ER alc_isp",
                writer,
            )
            utl.export_complex_to_excel(
                frecs,
                er_alc_isp_ref,
                "ER alc_isp_ref",
                writer,
            )
            utl.export_complex_to_excel(
                frecs,
                mdls.get_er_pat_alc_isopropilico(frecs),
                "ER alc_isp_pat",
                writer,
            )
            
            utl.export_complex_to_excel(
                frecs,
                er_sample_cal,
                "ER sample_cal",
                writer,
            )
            utl.export_complex_to_excel(
                frecs,
                er_sample_cal_ref,
                "ER sample_cal_ref",
                writer,
            )

            utl.export_complex_to_excel(
                frecs,
                mdls.get_er_pat_alc_etilico(frecs),
                "ER alc_eth_pat",
                writer,
            )
            utl.export_complex_to_excel(
                frecs,
                er_sample_ref,
                "ER sample_ref",
                writer,
            )

        print(f"Parametros permitividades guardados en {result_er}")

        
    # ============================================================================
    # Gráficos de S11
    # ============================================================================
    
    if plot_s11:
        # Comparacion de S11 de agua y agua de referencia
        utl.plot_s11_list(
            frecs,
            [
                {"name": "Agua simulado", "s11": s11_data["agua_dest"]["Complex"]},
                {"name": "Agua de referencia", "s11": s11_references["agua_dest"]["Complex"]},
            ],
            "S11 Agua",
            result_path / "s11_agua.png",
        )

        # Comparacion de S11 de aire y aire de referencia
        utl.plot_s11_list(
            frecs,
            [
                {"name": "Aire simulado", "s11": s11_data["aire"]["Complex"]},
                {"name": "Aire de referencia", "s11": s11_references["aire"]["Complex"]},
            ],
            "S11 Aire",
            result_path / "s11_aire.png",
        )

        # Comparacion de S11 de corto y corto de referencia
        utl.plot_s11_list(
            frecs,
            [
                {"name":"short simulado", "s11": s11_data["short"]["Complex"]},
                {"name":"short de referencia", "s11": s11_references["short"]["Complex"]},
            ],
            "S11 Short",
            result_path / "s11_short.png",
        )

        # Comparacion de S11 de alcohol isopropilico y alcohol isopropilico de referencia
        utl.plot_s11_list(
            frecs,
            [
                {"name": "Alcohol isopropilico simulado", "s11": s11_data["alc_isp"]["Complex"]},
                {"name": "Alcohol isopropilico de referencia", "s11": s11_references["alc_isp"]["Complex"]},
            ],
            "S11 Alcohol Isopropilico",
            result_path / "s11_alc_isp.png",
        )

        # Comparacion de S11 de alcohol etilico y alcohol etilico de referencia
        utl.plot_s11_list(
            frecs,
            [
                {"name": "Alcohol etilico simulado", "s11": s11_data["sample"]["Complex"]},
                {"name": "Alcohol etilico de referencia", "s11": s11_references["alc_eth"]["Complex"]},
            ],
            "S11 DUT",
            result_path / "s11_dut.png",
        )

    # ============================================================================
    # Gráficos de er
    # ============================================================================
    
    if plot_er:
        utl.plot_er_list(
            frecs,
            [
                {"name": "Agua simulado", "er": er_agua},                
                {"name": "Agua de referencia", "er": er_agua_ref},
                {"name": "Agua teorico", "er": mdls.get_debye_model(frecs)},
            ],
            "Er Agua",
            result_path / "er_agua.png",
        )

        utl.plot_er_list(
            frecs,
            [
                {"name": "Alcohol isopropilico simulado", "er": er_alc_isp},
                {"name": "Alcohol isopropilico de referencia", "er": er_alc_isp_ref},
                {"name": "Alcohol isopropilico teorico", "er": mdls.get_er_pat_alc_isopropilico(frecs)},
            ],
            "Er Alcohol Isopropilico",
            result_path / "er_alc_isp.png",
        )

        utl.plot_er_list(
            frecs,
            [
                #{"name": "DUT simulado", "er": er_sample},
                {"name": "DUT calibrado", "er": er_sample_cal},
                #{"name": "DUT de referencia", "er": er_sample_ref},
                {"name": "DUT de referencia calibrado", "er": er_sample_cal_ref},
                {"name": "DUT teorico", "er": mdls.get_er_pat_alc_etilico(frecs)},
            ],
            "Er DUT",
            result_path / "er_dut.png",
        )

    utl.show_plots()

    print("Gráficos guardados en " + str(result_path))

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":

    main()



