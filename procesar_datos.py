"""Procesador de datos de ventas.

Lee un CSV de ventas, lo limpia con pandas y genera dos archivos:
  - datos_limpios.csv          : datos sin duplicados, sin vacíos y con columna "total"
  - resumen_por_categoria.csv  : estadísticas agrupadas por categoría

Las rutas se configuran con variables de entorno (no están fijas en el código):
  INPUT_PATH  ruta del CSV de entrada
  OUTPUT_DIR  carpeta donde se escriben los resultados
"""

import os
import sys
from pathlib import Path

import pandas as pd

COLUMNAS_REQUERIDAS = ["id", "producto", "categoria", "cantidad", "precio"]


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el DataFrame: nombres de columnas, espacios, duplicados y nulos."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {faltantes}")

    # Quitar espacios y normalizar texto
    for col in ["producto", "categoria"]:
        df[col] = df[col].astype("string").str.strip().str.title()

    # Convertir a número; lo que no sea número se vuelve NaN
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    # Eliminar filas incompletas y duplicadas
    df = df.dropna(subset=COLUMNAS_REQUERIDAS)
    df = df.drop_duplicates()

    df["cantidad"] = df["cantidad"].astype(int)
    df["total"] = (df["cantidad"] * df["precio"]).round(2)
    return df


def resumir(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula estadísticas por categoría."""
    resumen = (
        df.groupby("categoria")
        .agg(
            num_ventas=("id", "count"),
            unidades_vendidas=("cantidad", "sum"),
            precio_promedio=("precio", "mean"),
            total_ventas=("total", "sum"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_ventas", ascending=False)
    )
    return resumen


def main() -> int:
    ruta_entrada = Path(os.getenv("INPUT_PATH", "datos_ejemplo/ventas.csv"))
    carpeta_salida = Path(os.getenv("OUTPUT_DIR", "salida"))

    if not ruta_entrada.is_file():
        print(f"ERROR: no se encontró el archivo de entrada: {ruta_entrada}", file=sys.stderr)
        return 1

    carpeta_salida.mkdir(parents=True, exist_ok=True)

    crudo = pd.read_csv(ruta_entrada)
    limpio = limpiar(crudo)
    resumen = resumir(limpio)

    limpio.to_csv(carpeta_salida / "datos_limpios.csv", index=False)
    resumen.to_csv(carpeta_salida / "resumen_por_categoria.csv", index=False)

    print(f"Filas leídas: {len(crudo)}")
    print(f"Filas después de limpiar: {len(limpio)}")
    print(f"Archivos generados en: {carpeta_salida}")
    print()
    print("Resumen por categoría:")
    print(resumen.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
