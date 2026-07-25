import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from funciones import (
    vna_proc_file,
    get_er_DUTm,
)

# ============================================================================
# Configuración
# ============================================================================

file_path = 'D:/ME2-PROY-SONDA/rsc/'

#measurement_date = "22-02-24"
measurement_date = "24-06-26"
resource_path = file_path +   measurement_date

print(resource_path)
files = {
    "aire": "AIRE.s1p",
    "isopropilico": "ALC_ISOPR.s1p",
    "agua_dest": "AGUA DEST.s1p",
    "short": "SHORT.s1p",
    "muestra": "ALC_ETH.s1p",
    #'muestra': "ACETONA.s1p",
}

# ============================================================================
# Lectura de archivos
# ============================================================================

s11_aire = vna_proc_file(resource_path, files["aire"])
s11_agua_dest = vna_proc_file(resource_path, files["agua_dest"])
s11_short = vna_proc_file(resource_path, files["short"])
s11_isop = vna_proc_file(resource_path, files["isopropilico"])
s11_muestra = vna_proc_file(resource_path, files["muestra"])

# ============================================================================
# Cálculo de permitividad
# ============================================================================


frecs      = s11_agua_dest['Frec']
er_iso     = get_er_DUTm (frecs, s11_isop['Complex'], s11_agua_dest['Complex'], s11_aire['Complex'], s11_short['Complex'])
er_agua    = get_er_DUTm (frecs, s11_agua_dest['Complex'], s11_agua_dest['Complex'], s11_aire['Complex'], s11_short['Complex'])
er_muestra = get_er_DUTm (frecs, s11_muestra['Complex'], s11_agua_dest['Complex'], s11_aire['Complex'], s11_short['Complex'])

# ============================================================================
# Gráfico
# ============================================================================




frecs_MHz = frecs / 1e6
# Gráfico Er Iso
plt.figure()
manager = plt.get_current_fig_manager()
manager.window.state('zoomed')

plt.plot(frecs_MHz, np.real(er_iso), label='Medido Parte Real')
plt.plot(frecs_MHz, np.imag(er_iso), label='Medido Parte Imaginaria')

plt.title('Real and Imaginary Parts of Er Iso')
plt.xlabel('Frequencia (MHz)')
plt.ylabel('Er')
ax = plt.gca()
plt.xscale('log')
ax.xaxis.set_major_formatter(ScalarFormatter())
plt.legend()
plt.grid(True, which='major', linewidth=1)
plt.grid(True, which='minor', linewidth=0.4)
plt.savefig(resource_path + "/er_iso.png", dpi=300, bbox_inches='tight')



# Gráfico Er Agua
plt.figure()
manager = plt.get_current_fig_manager()
manager.window.state('zoomed')

plt.plot(frecs_MHz, np.real(er_agua), label='Medido Parte Real')
plt.plot(frecs_MHz, np.imag(er_agua), label='Medido Parte Imaginaria')

plt.title('Real and Imaginary Parts of Er Agua')
plt.xlabel('Frequencia (MHz)')
plt.ylabel('Er')
ax = plt.gca()
plt.xscale('log')
ax.xaxis.set_major_formatter(ScalarFormatter())
plt.legend()
plt.grid(True, which='major', linewidth=1)
plt.grid(True, which='minor', linewidth=0.4)
plt.savefig(resource_path + "/er_agua.png", dpi=300, bbox_inches='tight')


# Gráfico Er Muestra
plt.figure()
manager = plt.get_current_fig_manager()
manager.window.state('zoomed')

plt.plot(frecs_MHz, np.real(er_muestra), label='Medido Parte Real')
plt.plot(frecs_MHz, np.imag(er_muestra), label='Medido Parte Imaginaria')

plt.title('Real and Imaginary Parts of Er Muestra')
plt.xlabel('Frequencia (MHz)')
plt.ylabel('Er')
ax = plt.gca()
plt.xscale('log')
ax.xaxis.set_major_formatter(ScalarFormatter())
plt.legend()
plt.grid(True, which='major', linewidth=1)
plt.grid(True, which='minor', linewidth=0.4)
plt.savefig(resource_path + "/er_muestra.png", dpi=300, bbox_inches='tight')


plt.show()