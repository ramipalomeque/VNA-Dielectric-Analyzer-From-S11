from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
##
# @brief Valida y normaliza una fecha de medición.
#
# Convierte una fecha ingresada en distintos formatos a un formato único
# `dd-MM-yy`, utilizado para localizar las carpetas de mediciones y resultados.
#
# Formatos aceptados:
# - dd-MM-yy
# - dd/MM/yy
# - dd-MM-yyyy
# - dd/MM/yyyy
# - yyyy-MM-dd
# - yyyy/MM/dd
# - ddMMyy
# - ddMMyyyy
#
# @param date_str Fecha ingresada por el usuario.
#
# @return Fecha normalizada en formato `dd-MM-yy`.
#
# @exception ValueError Si la fecha no corresponde a ninguno de los formatos
#            soportados.
##
def parse_measurement_date(date_str):
    formatos = [
        "%d-%m-%y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d%m%y",
        "%d%m%Y",
    ]

    for formato in formatos:
        try:
            fecha = datetime.strptime(date_str.strip(), formato)
            return fecha.strftime("%d-%m-%y")
        except ValueError:
            pass

    raise ValueError(
        "Formato de fecha inválido. Ejemplos válidos: "
        "24-11-26, 24/11/2026, 2026-11-24."
    )

##
# @brief Exporta las permitividades calculadas a un archivo Excel.
#
# Genera un archivo Excel con una hoja para la permitividad del agua
# destilada y una hoja adicional para cada material analizado. Cada hoja
# contiene la frecuencia, la parte real y la parte imaginaria de la
# permitividad relativa compleja (εr).
#
# @param frecs Vector de frecuencias.
# @param er_agua Vector de permitividad compleja del agua destilada.
# @param er_muestras Lista de diccionarios con la información de cada muestra.
#        Cada elemento debe tener la estructura:
#        - name: nombre de la muestra.
#        - er: vector de permitividad compleja.
# @param output_path Ruta completa del archivo Excel a generar.
#
# @return None.
##
def export_er_to_excel(frecs, er_agua, er_muestras, output_path):

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # Hoja del agua
        pd.DataFrame({
            "Frecuencia (Hz)": frecs,
            "Er Real": np.real(er_agua),
            "Er Imag": np.imag(er_agua),
        }).to_excel(writer, sheet_name="agua", index=False)

        # Hojas de las muestras
        for muestra in er_muestras:
            pd.DataFrame({
                "Frecuencia (Hz)": frecs,
                "Er Real": np.real(muestra["er"]),
                "Er Imag": np.imag(muestra["er"]),
            }).to_excel(
                writer,
                sheet_name=muestra["name"][:31],  # Límite de Excel
                index=False,
            )

def plot_er(frecs, er, title, output_file):
    frecs_MHz = frecs / 1e6

    plt.figure()
    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')

    plt.plot(frecs_MHz, np.real(er), label='Parte Real')
    plt.plot(frecs_MHz, np.imag(er), label='Parte Imaginaria')

    plt.title(title)
    plt.xlabel('Frecuencia (MHz)')
    plt.ylabel('Er')

    ax = plt.gca()
    plt.xscale('log')
    ax.xaxis.set_major_formatter(ScalarFormatter())

    plt.legend()
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.4)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')

def plot_er_comparison(frecs, er_1, name_er1, er_2, name_er2, title, output_file):
    frecs_MHz = frecs / 1e6

    plt.figure()
    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')

    plt.plot(frecs_MHz, np.real(er_1), label='Parte Real - ' + name_er1)
    plt.plot(frecs_MHz, np.imag(er_1), label='Parte Imaginaria - ' + name_er1)

    plt.plot(frecs_MHz, np.real(er_2), '--', label='Parte Real - ' + name_er2)
    plt.plot(frecs_MHz, np.imag(er_2), '--', label='Parte Imaginaria - ' + name_er2)

    plt.title(title)
    plt.xlabel('Frecuencia (MHz)')
    plt.ylabel('Er')

    ax = plt.gca()
    plt.xscale('log')
    ax.xaxis.set_major_formatter(ScalarFormatter())

    plt.legend()
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.4)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')    

def plot_s11(frecs, s11, title, output_file):
    frecs_MHz = frecs / 1e6

    plt.figure()
    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')

    plt.plot(frecs_MHz, np.real(s11), label='Parte Real')
    plt.plot(frecs_MHz, np.imag(s11), label='Parte Imaginaria')

    plt.title(title)
    plt.xlabel('Frecuencia (MHz)')
    plt.ylabel('S11')

    ax = plt.gca()
    plt.xscale('log')
    ax.xaxis.set_major_formatter(ScalarFormatter())

    plt.legend()
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.4)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
def show_plots():
    plt.show()