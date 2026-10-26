# Script_py

Scripy que lee un archivo de logs, identificando cada linea, validando y monstrara un resumen en consola, se utiliza la biblioteca estandar de python.

Caso de uso:
parando la ruta como argumento: 

    python .\Script.py registro.log

o sin el argumento

python .\Script.py 

nota: especificar la ruta donde se evaluara el archivo.

Ejemplo

Archivo registro.log:

[INFO] 2025-01-10 User logged in
[ERROR] 2025-01-10 Failed to connect to database
[WARNING] Invalid password attempt
[info] 2025-01-11   Cache cleared
[ERROR] 2025-02-30 Disk quota exceeded
Esto no es un log

Salida esperada:

========================================
  RESUMEN DEL ANALISIS DE LOGS
========================================
Total de eventos procesados : 6

Eventos por nivel de severidad:
  INFO     : 2
  WARNING  : 1
  ERROR    : 2

Lineas mal formateadas      : 3
  - Fecha ausente: 1
  - Fecha invalida: 1
  - Sin nivel reconocible: 1
========================================


Flujo del codigo

pedir_ruta: identificar la ubicacion del archivo
leer_lineas: lee el archivo 
validar_fecha: valida el formato de la fecha mediante expresiones regulares 
analizar_linea: detecta el motivo del mal formato
calcular_resumen: acumula los conteos de los errores
mostrar_resumen: muestra el resultado esperado 
