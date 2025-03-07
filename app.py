import pandas as pd
from flask import Flask, render_template, request, jsonify
import unicodedata

# Función para normalizar nombres de columnas
def normalize_column_names(df):
    # Eliminar acentos y caracteres especiales
    df.columns = [
        unicodedata.normalize('NFKD', col)
        .encode('ascii', 'ignore')
        .decode('utf-8')
        .replace(' ', '_')
        for col in df.columns
    ]
    return df

# Limpieza y preparación de datos
def clean_data(df):
    # Rellenar valores nulos en columnas de texto
    text_columns = [
        "Curs", "Denominacio_completa", "Nom_naturalesa", "Nom_area_territorial",
        "Grau", "Nom_ensenyament", "Modalitat"
    ]
    df[text_columns] = df[text_columns].fillna("")

    # Rellenar valores nulos en columnas numéricas
    numeric_columns = ["Matricules_Total", "Matricules_Dones", "Matricules_Homes"]
    df[numeric_columns] = df[numeric_columns].fillna(0)

    # Eliminar filas con valores nulos en columnas clave
    df = df.dropna(subset=text_columns)

    return df

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar el dataset
df = pd.read_csv("data/dataset.csv", encoding="utf-8", low_memory=False)

# Normalizar los nombres de las columnas
df = normalize_column_names(df)

# Limpiar el dataset
df = clean_data(df)

# Imprimir los nombres de las columnas normalizados
print("Columnas normalizadas:", df.columns.tolist())

# Función para obtener valores únicos de una columna
def get_unique_values(column):
    return sorted(df[column].unique().tolist())

# Función para filtrar el dataset según los filtros seleccionados
def filter_data(filters):
    filtered_df = df
    for key, value in filters.items():
        if value:
            filtered_df = filtered_df[filtered_df[key] == value]
    return filtered_df

# Ruta principal para mostrar el frontend
@app.route("/")
def index():
    # Obtener opciones para los filtros
    cursos = get_unique_values("Curs")
    centros = get_unique_values("Denominacio_completa")
    naturalezas = get_unique_values("Nom_naturalesa")
    areas = get_unique_values("Nom_area_territorial")
    grados = get_unique_values("Grau")
    ensenyaments = get_unique_values("Nom_ensenyament")
    modalitats = get_unique_values("Modalitat")

    # Imprimir las opciones para verificar
    print("Cursos:", cursos)
    print("Centros:", centros)
    print("Naturalesas:", naturalezas)
    print("Áreas territoriales:", areas)
    print("Grados:", grados)
    print("Ensenyaments:", ensenyaments)
    print("Modalitats:", modalitats)

    # Renderizar la plantilla HTML con las opciones de los filtros
    return render_template(
        "index.html",
        cursos=cursos,
        centros=centros,
        naturalezas=naturalezas,
        areas=areas,
        grados=grados,
        ensenyaments=ensenyaments,
        modalitats=modalitats,
    )

# Ruta para procesar los filtros y devolver los resultados
@app.route("/filtrar", methods=["POST"])
def filtrar():
    # Obtener los filtros del formulario
    filters = {
        "Curs": request.form.get("curs"),
        "Denominacio_completa": request.form.get("centro"),
        "Nom_naturalesa": request.form.get("naturaleza"),
        "Nom_area_territorial": request.form.get("area"),
        "Grau": request.form.get("grado"),
        "Nom_ensenyament": request.form.get("ensenyament"),
        "Modalitat": request.form.get("modalitat"),
    }

    # Imprimir los filtros para depuración
    print("Filtros aplicados:", filters)

    # Filtrar el dataset según los filtros seleccionados
    filtered_df = filter_data(filters)

    # Imprimir el dataset filtrado para depuración
    print("Dataset filtrado:", filtered_df)

    # Calcular el total de alumnos (hombres y mujeres)
    total_hombres = filtered_df["Matricules_Homes"].sum()
    total_mujeres = filtered_df["Matricules_Dones"].sum()

    # Devolver los resultados en formato JSON
    return jsonify(
        {
            "total_hombres": int(total_hombres),
            "total_mujeres": int(total_mujeres),
        }
    )

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)