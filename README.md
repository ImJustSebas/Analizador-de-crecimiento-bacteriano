Analizador de Crecimiento Bacteriano
Desarrollado por Sebastian Porras Solano
Una herramienta de escritorio para microbiologos que prefieren invertir su tiempo analizando datos, no formateando archivos CSV.

https://img.shields.io/badge/python-3.8%252B-blue
https://img.shields.io/badge/License-MIT-yellow.svg

¿Por que existe este software?
Durante el trabajo de laboratorio es comun encontrarse con archivos CSV generados por diferentes espectrofotometros, lectores de placas o software de camaras. Cada uno utiliza un separador distinto, una codificacion de caracteres exotica o nombres de columna no estandar.

Analizador de Crecimiento Bacteriano nace para eliminar esa friccion. Este programa no solo grafica sus curvas de crecimiento; le permite dialogar con sus datos antes de importarlos, corregir la configuracion sobre la marcha y obtener parametros cineticos listos para incluir en su cuaderno de laboratorio o publicacion.

Capturas de Pantalla
(A continuacion se muestra como insertar imagenes en el README. Las imagenes deben estar en una carpeta llamada screenshots dentro del repositorio).

Ventana de previsualizacion de CSV
Ajuste interactivo de codificacion y separador antes de cargar los datos.
https://screenshots/csv_preview.png

Analisis de curvas de crecimiento
Modelado logistico, barras de error y exportacion de resultados.
https://screenshots/growth_curve.png

Caracteristicas Principales
Previsualizador Interactivo de CSV
Olvidese de probar codificaciones a ciegas. La aplicacion detecta automaticamente UTF-8, Latin-1 o CP1252 y le muestra las primeras 20 filas. Si el separador no es el correcto, puede cambiarlo desde un menu desplegable y ver el resultado al instante.

Gestion de Multiples Condiciones Experimentales
Cargue cuantas cepas, tratamientos o replicas biologicas desee. Cada dataset se identifica con un color unico y un nombre personalizado, permitiendo comparar visualmente el comportamiento de cada grupo.

Calculo Automatico de Replicas
Si en su archivo CSV existen varias mediciones para un mismo tiempo, el software agrupa los datos y calcula automaticamente la media y la desviacion estandar. Las barras de error apareceran reflejadas en la grafica final.

Ajuste Logistico Profesional (Modelo Sigmoide)
El corazon del analisis cuantitativo. La aplicacion ajusta los datos al modelo logistico:
f(t) = A / (1 + e^(-k * (t - t0)))
Obteniendo:

A: Capacidad de carga (asintota maxima).

k: Tasa maxima de crecimiento.

t0: Punto de inflexion de la curva.

R²: Bondad del ajuste.

Td: Tiempo de duplicacion en fase exponencial (ln(2)/k).

Sistema de Respaldo Inteligente (Savitzky-Golay)
Sabemos que no todas las curvas bacterianas son perfectas. Si el modelo logistico no converge debido a ruido o fase de muerte celular, el programa aplica silenciosamente un filtro de suavizado Savitzky-Golay. Usted obtiene una linea de tendencia limpia sin mensajes de error que interrumpan su flujo de trabajo.

Entrada Manual de Datos
¿Olvido anotar un punto o necesita corregir un valor atipico? Seleccione el dataset y agregue el dato manualmente a traves de la interfaz, sin necesidad de reabrir el archivo original.

Exportacion de Alta Calidad

Graficas: Guarde su curva en PNG (para informes rapidos), PDF o SVG (vectores ideales para publicaciones cientificas y posters).

Datos Numericos: Exporte los datos agregados a un archivo Excel (.xlsx) con una hoja por cepa y otra hoja adicional con los parametros del ajuste logistico.

Instalacion y Ejecucion
Requisitos Previos
Tener instalado Python 3.8 o superior.
Si no lo tiene, descarguelo desde python.org. Durante la instalacion en Windows, asegurese de marcar la casilla "Add Python to PATH".

Paso 1: Clonar el Repositorio
bash
git clone https://github.com/ImJustSebas/Analizador-de-crecimiento-bacteriano.git
cd Analizador-de-crecimiento-bacteriano
Paso 2: Instalar Dependencias
Se recomienda usar un entorno virtual, aunque no es obligatorio.

bash
pip install -r requirements.txt
Paso 3: Ejecutar el Programa
bash
python Analizador-de-crecimiento-bacteriano.py
Guia de Uso Rapido
Inicie el programa y asigne un nombre a su proyecto (ej: "Experimento Cepa WT 37C").

Cargue sus archivos CSV usando el boton "Cargar CSV (anadir dataset)".

En la ventana de previsualizacion:

Verifique que las columnas de Tiempo y Altura se hayan detectado correctamente.

Si el texto se ve con simbolos raros, cambie la Codificacion (Latin-1 suele resolver problemas con tildes).

Si los datos aparecen en una sola columna, ajuste el Separador (Tabulacion o Punto y coma).

Haga clic en "Analizar y Graficar".

Explore los parametros de ajuste en la esquina inferior izquierda de la figura.

Exporte la grafica o el informe en Excel segun lo necesite.

Dependencias del Proyecto
El proyecto se apoya en las siguientes bibliotecas cientificas de Python. El archivo requirements.txt contiene las versiones exactas recomendadas.

Pandas: Manipulacion de datos tabulares.

NumPy: Calculos numericos de alto rendimiento.

Matplotlib: Generacion de graficos de calidad publicable.

SciPy: Algoritmos de ajuste de curvas (curve_fit) y filtros de suavizado (savgol_filter).

Chardet: Deteccion inteligente de la codificacion de caracteres del archivo.

OpenPyXL: Soporte para exportar datos a formato Excel (.xlsx).

Estructura Esperada del CSV
El programa es flexible, pero para una experiencia optima, su archivo CSV deberia contener al menos dos columnas:

Tiempo (h)	Densidad Optica (OD600)	Temperatura (C)	Notas
0	0.102	37	Inoculo
2	0.145	37	-
4	0.310	37	Inicio exp.
La aplicacion detecta automaticamente nombres como Tiempo, Time, Horas, Height, Absorbancia, OD, Valor, etc. Si su archivo tiene nombres muy distintos, la ventana de previsualizacion le permitira asignar la columna correcta manualmente.

Contacto y Soporte
Este software es mantenido activamente. Si encuentra un error, tiene una sugerencia o simplemente quiere mostrar como utiliza la herramienta en su laboratorio, no dude en contactarme.

Autor: Sebastian Porras Solano

Email: sebastianporras067@gmail.com

GitHub: @ImJustSebas

Si este programa le ha sido util en su investigacion, considere dejar una estrella (Star) en el repositorio. Ayuda a que otros colegas lo encuentren mas facilmente.

Licencia
Este proyecto esta licenciado bajo los terminos de la Licencia MIT.
Esto significa que puede usar, modificar y distribuir el codigo libremente, incluso en entornos comerciales o educativos, siempre que se mantenga el aviso de copyright original. Consulte el archivo LICENSE para mas detalles.

