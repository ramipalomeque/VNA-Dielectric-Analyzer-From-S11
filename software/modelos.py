
import numpy as np
##
# @brief Obtiene el modelo de Debye para agua destilada.
#
# Calcula la permitividad relativa compleja del agua destilada en función
# de la frecuencia utilizando el modelo de Debye.
#
# @param frecs Vector de frecuencias.
#
# @return Vector con la permitividad relativa compleja del agua.
##
def get_debye_model(frecs): 
    E_inf = 4.6        # Permitividad a alta frecuencia
    E_s   = 78.3       # Permitividad estática
    tau   = 8.07e-12   # Tiempo de relajación [s]
    w = 2 * np.pi * frecs
    Er = E_inf + (E_s - E_inf) / (1 - 1j * w * tau)

    return Er

##
# @brief Obtiene el modelo teórico de permitividad del alcohol etílico.
#
# Calcula la permitividad relativa compleja del alcohol etílico en función
# de la frecuencia.
#
# @param frecs Vector de frecuencias.
#
# @return Vector con la permitividad relativa compleja.
##
def get_er_pat_alc_etilico(frecs):
    #A = 4.505 + ((24.43 - 4.505) / (1 + 1j * frecs / (0.964e9))) - 1j * frecs * 0.056 / 1e9
    #return np.real(A) +1j * np.imag(A)

    E_inf = 4.505      # Permitividad a alta frecuencia
    E_s   = 24.43      # Permitividad estática
    fc    = 0.964e9    # Frecuencia característica [Hz]
    sigma = 0.056      # Término de pérdidas

    Er = (
        E_inf
        + (E_s - E_inf) / (1 + 1j * frecs / fc)
        - 1j * frecs * sigma / 1e9
    )
    return Er

##
# @brief Obtiene el modelo teórico de permitividad del alcohol isopropílico.
#
# Calcula la permitividad relativa compleja del alcohol isopropílico al
# 99 % utilizando su modelo dieléctrico.
#
# @param frecs Vector de frecuencias.
#
# @return Vector con la permitividad relativa compleja.
##
def get_er_pat_alc_isopropilico(frecs):
    # curva del er complejo del isopropilico al 99 segun la curva de deybe
    #ER = 3.065 + ((19.30 - 3.551) / (1 + 1j * frecs / (0.443e9))) + ((3.551 - 3.065) / (1 + 1j * frecs / (5.999e9)))
    #return ER
    E_inf = 3.065      # Permitividad a alta frecuencia

    E_s1 = 19.30       # Permitividad inicial del primer polo
    E_s2 = 3.551       # Permitividad entre relajaciones

    fc1 = 0.443e9      # Primera frecuencia característica [Hz]
    fc2 = 5.999e9      # Segunda frecuencia característica [Hz]

    Er = (
        E_inf
        + (E_s1 - E_s2) / (1 + 1j * frecs / fc1)
        + (E_s2 - E_inf) / (1 + 1j * frecs / fc2)
    )

    return Er  