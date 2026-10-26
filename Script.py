import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


NIVELES_VALIDOS = ("INFO", "WARNING", "ERROR")

# expresion para determinar el nivel 
LINEA = re.compile(r"^\[(?P<nivel>[^\]]*)\]\s*(?P<resto>.*)$")

# Forma estricta de fecha y forma
FECHA_ESTRICTA = re.compile(r"\d{4}-\d{2}-\d{2}")
PARECE_FECHA = re.compile(r"^\d[\d/.\-]*$")

# Motivos de linea mal formateada
SIN_NIVEL = "Sin nivel reconocible"
NIVEL_DESCONOCIDO = "Nivel desconocido"
FECHA_AUSENTE = "Fecha ausente"
FECHA_INVALIDA = "Fecha invalida"
MENSAJE_VACIO = "Mensaje vacio"


class ErrorLectura(Exception):
    """Error controlado al leer el archivo (mensaje apto para el usuario)."""


@dataclass
class LineaAnalizada:
    nivel: Optional[str]    # "INFO"/"WARNING"/"ERROR" 
    motivo: Optional[str]   # None si la linea esta bien 


# leer arc
def pedir_ruta() -> str:
  
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = input("Ruta del archivo de logs: ")
    return ruta.strip().strip('"').strip("'")


def leer_lineas(ruta: str) -> list[str]:
    
    try:
        with open(ruta, "r", encoding="utf-8-sig", errors="replace") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        raise ErrorLectura(f"El archivo no existe: {ruta!r}")
    except IsADirectoryError:
        raise ErrorLectura(f"La ruta es un directorio, no un archivo: {ruta!r}")
    except PermissionError:
        raise ErrorLectura(f"Sin permisos para leer: {ruta!r}")
    except OSError as e:
        raise ErrorLectura(f"No se pudo leer {ruta!r}: {e.strerror or e}")



def validar_fecha(token: str) -> Optional[str]:
    """Devuelve None si la fecha es valida, o el motivo (ausente/invalida)."""
    if not PARECE_FECHA.match(token):
        return FECHA_AUSENTE
    if not FECHA_ESTRICTA.fullmatch(token):
        # ej. 10/01/2025 o 2025-1-5
        return FECHA_INVALIDA
    try:
        # rechaza 2025-02-30, 2025-13-01..
        datetime.strptime(token, "%Y-%m-%d")
    except ValueError:
        return FECHA_INVALIDA
    return None



def analizar_linea(linea: str) -> LineaAnalizada:
    """Analiza una linea NO vacia y aplica la politica de motivos (ver punto 3)."""
    coincidencia = LINEA.match(linea.strip())
    if not coincidencia:
        return LineaAnalizada(None, SIN_NIVEL)

    nivel = coincidencia.group("nivel").strip().upper()
    if nivel not in NIVELES_VALIDOS:
        return LineaAnalizada(None, NIVEL_DESCONOCIDO)

    partes = coincidencia.group("resto").split(None, 1)  # split tolera espacios extra
    token = partes[0] if partes else ""
    mensaje = partes[1].strip() if len(partes) > 1 else ""

    motivo_fecha = validar_fecha(token)
    if motivo_fecha:
        return LineaAnalizada(nivel, motivo_fecha)
    if not mensaje:
        return LineaAnalizada(nivel, MENSAJE_VACIO)
    return LineaAnalizada(nivel, None)



def calcular_resumen(lineas: list[str]) -> dict:
    """Recorre las lineas y acumula las metricas pedidas."""
    por_nivel = Counter({n: 0 for n in NIVELES_VALIDOS})
    motivos = Counter()
    total = vacias = mal_formateadas = 0

    for linea in lineas:
        if not linea.strip():          # linea vacia: ni evento ni error
            vacias += 1
            continue
        total += 1
        resultado = analizar_linea(linea)
        if resultado.nivel:
            por_nivel[resultado.nivel] += 1
        if resultado.motivo:
            mal_formateadas += 1
            motivos[resultado.motivo] += 1

    return {
        "total": total,
        "por_nivel": por_nivel,
        "mal_formateadas": mal_formateadas,
        "motivos": motivos,
        "vacias": vacias,
    }



def mostrar_resumen(resumen: dict) -> None:
    linea = "=" * 40
    print(f"\n{linea}\n  RESUMEN DEL ANALISIS DE LOGS\n{linea}")
    print(f"Total de eventos procesados : {resumen['total']}")
    print("\nEventos por nivel de severidad:")
    for nivel in NIVELES_VALIDOS:
        print(f"  {nivel:<9}: {resumen['por_nivel'][nivel]}")
    print(f"\nLineas mal formateadas      : {resumen['mal_formateadas']}")
    for motivo, cantidad in resumen["motivos"].most_common():
        print(f"  - {motivo}: {cantidad}")
    if resumen["vacias"]:
        print(f"\nLineas vacias ignoradas     : {resumen['vacias']}")
    print(linea)



def main() -> int:
    ruta = pedir_ruta()

    try:
        lineas = leer_lineas(ruta)
    except ErrorLectura as e:
        print(f"Error: {e}")
        return 1

    if not any(l.strip() for l in lineas):
        print("Aviso: el archivo esta vacio o solo contiene lineas en blanco.")

    mostrar_resumen(calcular_resumen(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
