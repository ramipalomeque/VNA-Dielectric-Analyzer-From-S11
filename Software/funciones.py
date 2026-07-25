import os
import numpy as np
import matplotlib.pyplot as plt
import cmath
from datetime import datetime
from scipy.optimize import fsolve
# !pip install git+https://github.com/dpk2442/pysmith.git#egg=pysmith

from modelos import (
    get_debye_model,
    get_er_pat_alc_etilico,
    get_er_pat_alc_isopropilico,
)

##
# @brief Procesa un archivo Touchstone (.s1p) obtenido del VNA.
#
# Lee un archivo de medición en formato S1P y extrae la información de
# frecuencia y coeficiente de reflexión (S11). La función soporta archivos
# cuyos datos se encuentren en formato Magnitud/Fase (DB) o Parte Real/
# Parte Imaginaria (RI), convirtiéndolos a números complejos.
#
# @param file_path Ruta donde se encuentra el archivo.
# @param file_name Nombre del archivo S1P.
#
# @return Diccionario con la información procesada:
#         - Date: fecha de la medición.
#         - Data: encabezado del archivo.
#         - Index: nombres de las columnas.
#         - Frec: frecuencias medidas.
#         - Complex: valores complejos de S11.
##
def vna_proc_file(file_path, file_name): #Procesa archivos S1P de VNA
    if file_name.endswith('.csv'):
      print('Formato de CSV no soportado todavia')
      return

    header_start  = '#'
    data_start    = '!'
    out_dict = {
                'Date'   : '',
                'Data'   : [],
                'Index'  : [],
                'Frec'   : [],
                'Complex': [],
              }

    frecuencies = np.array([])
    complejos   = np.array([])
    phase       = np.array([])
    reals       = np.array([])
    imgs        = np.array([])

    if ( file_path[-1] != '/' ):
      file_path += '/'
    file_path += file_name
    try:
        file = open(file_path, "r")
    except:
        print('TODO: No se puede abrir')
        print(file_name)
        return 404
    file_list = file.readlines()
    # print(file_list)
    file.close()

    for i, line in enumerate(file_list):
        if line.startswith('#'):
            header_index = i
            break

    headers = file_list[header_index][2:].upper().split()

    for line in file_list[header_index + 1:]:
        values = line.strip().split()
        frecuencies = np.append(frecuencies, np.float32(values[0]))
        #Dependiendo el modo del VNA graba los archivos en "MOdulo y Fase" o en "Parte Real e imaginaria"

        if (headers[1]=='S') and (headers[2]=='DB'):
          complejos = np.append(complejos, convertir_a_rectangular(np.float32(values[1]), np.float32(values[2])))
        elif  (headers[1]=='S') and (headers[2]=='RI') :
          reals     = np.append(reals, np.float32(values[1]))
          imgs      = np.append(imgs, np.float32(values[2]))
          complejos = reals +1j*imgs
        elif (headers[1]=='S') and (headers[2] == 'MA'):
          modulo = np.float32(values[1])
          fase = np.float32(values[2])
          complejos = np.append(complejos,modulo * np.exp(1j * np.radians(fase))
    )

    out_dict['Date'   ] = file_list[1][5:]
    out_dict['Data'   ] = file_list[0:11]
    out_dict['Index'  ] = headers
    out_dict['Frec'   ] = frecuencies
    out_dict['Complex'] = complejos

    return out_dict

##
# @brief Convierte un valor expresado en magnitud y fase a un número complejo.
#
# Convierte un coeficiente de reflexión representado mediante magnitud en
# decibeles (dB) y fase en grados a su equivalente en coordenadas
# rectangulares (parte real e imaginaria).
#
# Esta función se utiliza durante el procesamiento de archivos S1P cuando
# las mediciones del VNA se encuentran almacenadas en formato DB (Magnitud/Fase).
#
# @param modulo_db Magnitud del coeficiente de reflexión en decibeles (dB).
# @param fase_grados Fase del coeficiente de reflexión en grados.
#
# @return Número complejo equivalente al valor de entrada.
##
def convertir_a_rectangular(modulo_db, fase_grados):
    modulo        = 10 ** (modulo_db / 20)
    fase_radianes = np.radians(fase_grados)

    return modulo * np.exp(1j * fase_radianes)

##
# @brief Convierte el parámetro S11 en el parámetro de admitancia Y11.
#
# Calcula la admitancia equivalente a partir del coeficiente de reflexión
# medido por el analizador vectorial de redes.
#
# @param frec Vector de frecuencias.
# @param S11 Vector de valores complejos del parámetro S11.
#
# @return Diccionario con:
#         - Frec: frecuencias.
#         - Complex: valores complejos de Y11.
##
def S11_to_Y11(frec, S11):
    z0  = 50
    y0  = 1/z0
    Y11 = y0*(( 1 - S11 ) / ( 1 + S11 ))

    return { 'Frec'    : frec,
             'Complex' : Y11,
            }

##
# @brief Realiza un submuestreo de un conjunto de mediciones.
#
# Ajusta un conjunto de datos eliminando las frecuencias que no se
# encuentran presentes en el conjunto de referencia.
#
# @param small_dict Conjunto de datos de referencia.
# @param big_dict Conjunto de datos a submuestrear.
#
# @return Diccionario con las frecuencias y valores complejos ajustados.
##
def SUBsample_S11 (small_dict, big_dict):
  if (len(small_dict['Frec']) < len(big_dict['Frec']) ):
    index = len(big_dict['Frec']) - 1
    while ( index >= 0 ):
        if( big_dict['Frec'][index] not in small_dict['Frec'] ):
            big_dict['Frec']    = np.delete(big_dict['Frec'], index)
            big_dict['Complex'] = np.delete(big_dict['Complex'], index)
        index -= 1
  else:
    print('El diccionario no es mas chico sino mas grande')

  if (len(small_dict) == len(big_dict) ):
    # print(big_dict)
    return big_dict

# subfolder  = '08-15-23'
# big_dict   = vna_proc_file(file_path + subfolder, files[subfolder][2]) #2 ->Aire
# subfolder  = '21-12-23'
# small_dict = vna_proc_file(file_path + subfolder, files[subfolder][0]) #Cualquier diccionario solo se usan las frecuencias del mas chico
# SUBsample_S11(small_dict, big_dict)

##
# @brief Remuestrea un conjunto de mediciones mediante interpolación.
#
# Interpola linealmente un conjunto de datos para obtener valores en las
# mismas frecuencias que un conjunto de referencia.
#
# @param smaller_set Conjunto de referencia.
# @param data Conjunto de datos a interpolar.
#
# @return Diccionario con las frecuencias y valores complejos remuestreados.
##
def Resample_S11 (smaller_set, data):
  OUT_SET = {'Frec'    : [],
             'Complex' : [],
             }
  # Interpolación
  for freq in smaller_set['Frec']:
    # Encontrar los índices de los valores más cercanos en el conjunto de datos más grande
    idx1 = np.argmin(np.abs(np.array(data['Frec']) - freq))
    idx2 = idx1 + 1 if idx1 < len(data['Frec']) - 1 else idx1

    # Interpolación lineal
    x1, x2 = data['Frec'][idx1], data['Frec'][idx2]
    y1, y2 = data['Complex'][idx1], data['Complex'][idx2]

    # Manejar el caso cuando x1 es igual a x2
    if x1 == x2:
        interpolated_value = y1
    else:
        interpolated_value = y1 + (y2 - y1) * (freq - x1) / (x2 - x1)

    # Agregar el valor interpolado al conjunto de datos más pequeño
    OUT_SET['Complex'].append(interpolated_value)
    OUT_SET['Frec'].append(freq)

  return OUT_SET

##
# @brief Calcula la permitividad relativa del material bajo prueba (DUT).
#
# Estima la permitividad relativa compleja del material utilizando las
# mediciones del DUT y las mediciones de referencia correspondientes al
# circuito abierto, cortocircuito y agua destilada.
#
# @param frecs Vector de frecuencias.
# @param S11_medido Parámetro S11 del material bajo prueba.
# @param S11_agua Parámetro S11 medido en agua destilada.
# @param S11_aire Parámetro S11 medido en circuito abierto.
# @param S11_corto Parámetro S11 medido en cortocircuito.
#
# @return Vector con la permitividad relativa compleja estimada.
##
def get_er_DUTm (frecs, S11_medido, S11_agua, S11_aire, S11_corto):
  Er_agua = get_debye_model(frecs)

  A  = ( (S11_medido - S11_agua)*(S11_aire - S11_corto) ) / ( (S11_medido - S11_corto)*(S11_agua - S11_aire))
  ER =-( ( (S11_medido - S11_aire)*(S11_corto - S11_agua) ) / ( (S11_medido - S11_corto)*(S11_agua - S11_aire) ) )*Er_agua

  return ER-A

##
# @brief Calcula la respuesta calibrada del sistema de medición.
#
# Obtiene la conductancia equivalente del sistema utilizando las
# mediciones de referencia y los modelos dieléctricos de calibración.
#
# @param frecs Vector de frecuencias.
# @param S11_medido Parámetro S11 del material bajo prueba.
# @param s11_agua Parámetro S11 del agua destilada.
# @param s11_abierto Parámetro S11 del circuito abierto.
# @param s11_isopropilico Parámetro S11 del alcohol isopropílico.
# @param s11_corto Parámetro S11 del cortocircuito.
#
# @return Vector con la conductancia calibrada en función de la frecuencia.
##
def get_er_setup(frecs, S11_medido, s11_agua, s11_abierto, s11_isopropilico, s11_corto):
  r_agua    = s11_agua
  r_aire    = s11_abierto
  r_corto   = s11_corto
  r_alcohol = s11_isopropilico

  Er_agua    = get_debye_model(frecs)
  Er_alcohol = get_er_pat_alc_isopropilico(frecs);
  solEm      = []

  # Calculation of ER for each frequency point
  A = ((r_alcohol - r_corto) * (r_agua - r_aire ) * Er_alcohol)
  B = ((r_alcohol - r_aire ) * (r_corto- r_agua ) * Er_agua)
  C = ((r_alcohol - r_aire ) * (r_aire - r_corto) )

  D = ((r_alcohol - r_corto) * (r_agua - r_aire ) * (Er_alcohol**(5/2)))
  E = ((r_alcohol - r_aire ) * (r_corto- r_agua ) * (Er_agua**(5/2)))
  F = ((r_alcohol - r_aire ) * (r_aire - r_corto) )

  Gn = -1 * (A + B + C) / (D + E + F)

  X = ((S11_medido - r_aire) * (r_corto - r_agua) ) / ((S11_medido - r_corto) * (r_agua - r_aire))
  Z = ((S11_medido - r_agua) * (r_aire  - r_corto)) / ((S11_medido - r_corto) * (r_agua - r_aire))

  initial_guess = np.ones_like(frecs)
  initial_guess = np.array(initial_guess)

  Gn      = np.array(Gn)
  Er_agua = np.array(Er_agua)
  X       = np.array(X)
  Z       = np.array(Z)
  # print("ER ", Er_agua)
  # print("X ", X)
  # print("Z ", Z)
  # print("Gn ", Gn)

  for n in range(len(frecs)):
    def equation(Em, Gn, Er_agua, X, Z, n):
        return Em + Gn[n] * (Em**(5/2)) + (Er_agua[n] + Gn[n] * (Er_agua[n]**(5/2))) * X[n] + (1 + Gn[n]) * Z[n]

    # solEm.append(fsolve(equation, initial_guess, args=(Gn, Er_agua, X, Z, n)))
    solEm.append(np.real(fsolve(equation, initial_guess, args=(Gn, Er_agua, X, Z, n))))
  return solEm
