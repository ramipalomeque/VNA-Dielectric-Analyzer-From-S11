# VNA-S11-Dielectric-Analyzer

Herramienta para la extracción de permitividad dieléctrica de materiales a partir de mediciones S11 realizadas con un Analizador de Redes Vectorial (VNA) y una sonda coaxial abierta.

## Descripción

El software permite calcular la permitividad relativa compleja (εr) de un material bajo prueba (DUT) utilizando mediciones del coeficiente de reflexión S11 y estándares de calibración conocidos.

El proceso utiliza mediciones de:

- Circuito abierto (Open)
- Cortocircuito (Short)
- Agua destilada como referencia dieléctrica
- Material bajo prueba (DUT)

A partir de estas mediciones se obtiene la permitividad relativa del material en función de la frecuencia.

## Funcionalidades

- Lectura de archivos Touchstone `.S1P` provenientes de distintos modelos de VNA.
- Soporte para diferentes formatos de parámetros S:
  - `DB` → Magnitud en dB / Fase
  - `MA` → Magnitud lineal / Fase
  - `RI` → Parte Real / Parte Imaginaria
- Conversión de parámetros S11 a valores complejos.
- Conversión de S11 a admitancia equivalente Y11.
- Ajuste de mediciones mediante:
  - Submuestreo de frecuencias.
  - Interpolación de datos.
- Cálculo de permitividad relativa compleja mediante mediciones de referencia.
- Modelos dieléctricos teóricos para materiales patrón.
- Visualización de resultados en función de la frecuencia.

## Estructura del proyecto

```
├── main.py
├── modelos.py
├── vna.py
├── measurements/
└── results/
```

## Dependencias

- Python 3.x
- NumPy
- SciPy
- Matplotlib

Instalar dependencias:

```bash
pip install numpy scipy matplotlib
```

## Uso

Ejecutar:

```bash
python main.py
```

El programa procesa los archivos de medición obtenidos del VNA y calcula la permitividad del material analizado.

## Método de medición

La técnica utilizada se basa en una sonda coaxial abierta conectada a un VNA.

Las mediciones de referencia permiten caracterizar la respuesta de la sonda mediante estándares conocidos. Luego, utilizando la medición del material bajo prueba, se obtiene su permitividad relativa compleja (εr).

## Formato de entrada

Los archivos de medición deben estar en formato Touchstone S1P.

Ejemplos de formatos soportados:

```
# Hz S DB R 50
```

```
# HZ S MA R 50
```

```
# HZ S RI R 50
```

## Estado del proyecto

Proyecto en desarrollo.

Actualmente incluye:

- Procesamiento de archivos S1P.
- Conversión de formatos de medición.
- Procesamiento de parámetros S11.
- Cálculo de permitividad mediante mediciones de calibración.

## Autor

Proyecto de caracterización electromagnética de materiales mediante VNA y sonda coaxial abierta.