Analizador de Crecimiento Bacteriano
Descripcion
Analizador de Crecimiento Bacteriano es una aplicacion de escritorio desarrollada en Python para la visualizacion y analisis cuantitativo de curvas de crecimiento microbiano. La herramienta esta disenada especificamente para laboratorios de microbiologia, biotecnologia y bioquimica que requieren procesar datos de densidad optica (OD), absorbancia o altura de colonias a lo largo del tiempo.

La aplicacion incorpora un sistema inteligente de carga de archivos CSV con previsualizacion interactiva, permitiendo al usuario ajustar manualmente la codificacion y el separador de columnas antes de importar los datos. Una vez cargados los datasets, el software calcula automaticamente medias y desviaciones estandar para puntos de tiempo con replicas, y aplica un modelo de regresion logistica para estimar parametros cineticos fundamentales como la tasa maxima de crecimiento (k), el punto de inflexion (t0) y el tiempo de duplicacion (Td).

Caracteristicas Principales
Carga Robusta de Datos: Previsualizador interactivo de archivos CSV con deteccion automatica de codificacion (UTF-8, Latin-1, CP1252) y separadores (coma, punto y coma, tabulacion). El usuario puede corregir la configuracion en tiempo real observando una tabla de las primeras 20 filas.

Gestion de Multiples Cepas o Condiciones: Soporte para cargar y visualizar simultaneamente multiples datasets, cada uno identificado con un nombre y color unico en la grafica.

Agrupacion Inteligente: Calculo automatico de media y desviacion estandar para mediciones replicadas en el mismo punto temporal.

Entrada Manual de Datos: Interfaz para anadir o corregir puntos de datos individuales directamente sobre el dataset seleccionado, con validacion de tipos numericos.

Ajuste Logistico (Modelo Sigmoide): Implementacion del modelo logistico para estimar capacidad de carga (A), tasa de crecimiento (k) y punto de inflexion (t0). Incluye calculo del coeficiente de determinacion (R²) y tiempo de duplicacion en fase exponencial.

Suavizado de Respaldo: En caso de que los datos no se ajusten a una curva sigmoide clasica, la aplicacion utiliza un filtro Savitzky-Golay para generar una linea de tendencia suavizada sin interrumpir el flujo de trabajo.

Exportacion Profesional:

Guardado de graficas en formatos de alta resolucion: PNG, PDF y SVG (apto para publicaciones cientificas).

Exportacion de datos agregados a formato Excel (.xlsx) con hojas separadas por cepa y parametros de ajuste.

Requisitos del Sistema
Python 3.8 o superior.

Sistema Operativo: Windows, macOS o Linux (compatible con Tkinter).

Dependencias
Las siguientes bibliotecas de Python son necesarias para la ejecucion del programa:

text
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0
scipy>=1.7.0
chardet>=4.0.0
openpyxl>=3.0.0
Nota: chardet y openpyxl son opcionales pero altamente recomendados para la deteccion avanzada de codificacion y exportacion a Excel respectivamente.

Instalacion y Ejecucion
Clonar el repositorio:

bash
git clone https://github.com/tu-usuario/analizador-crecimiento-bacteriano.git
cd analizador-crecimiento-bacteriano
Crear y activar un entorno virtual (recomendado):

bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
venv\Scripts\activate     # En Windows
Instalar las dependencias:

bash
pip install -r requirements.txt
Ejecutar la aplicacion:

bash
python main.py
(Ajusta el nombre del archivo si tu script principal tiene otro nombre, por ejemplo index.py)

Estructura Esperada de los Archivos CSV
La aplicacion realiza un mapeo flexible de columnas, buscando palabras clave. Sin embargo, para una compatibilidad optima, se recomienda que los archivos CSV contengan las siguientes columnas (el orden no es relevante):

Tiempo: Valores numericos (horas, minutos, dias).

Altura: Valores numericos (Densidad Optica, Absorbancia, mm de crecimiento).

Temperatura (Opcional): Valor numerico de la temperatura de incubacion.

Notas (Opcional): Texto libre asociado a la medicion.

La ventana de previsualizacion permite asignar manualmente las columnas correctas en caso de nombres ambiguos o no estandar.

Uso de la Aplicacion
Nuevo Proyecto: Asigne un nombre al experimento actual.

Cargar CSV: Seleccione uno o varios archivos. En la ventana de previsualizacion, verifique que la codificacion, el separador y el mapeo de columnas sean correctos. Presione "Cargar este CSV".

Analizar: Una vez cargados todos los datasets deseados, haga clic en "Analizar y Graficar".

Interpretar Resultados: La grafica mostrara los puntos experimentales (media +/- desviacion estandar) y una linea punteada representando el modelo logistico o el suavizado de datos.

Exportar: Guarde la figura en formato vectorial o exporte la tabla de datos agregados a Excel.
