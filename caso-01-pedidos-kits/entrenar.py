# ENTRENAMIENTO | Caso 1 - Estimacion de pedidos de kits de robotica
# SENATI - Taller de Machine Learning y Deep Learning
#
# Este script lee datos.csv, entrena una regresion lineal multiple con
# scikit-learn, evalua el modelo con datos que NO vio al entrenar y guarda:
#   - modelo.json : coeficientes e indicadores (los usa la aplicacion Flask)
#   - modelo.pkl  : el modelo completo de scikit-learn (copia de respaldo)
#
# Uso:  python entrenar.py

from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

carpeta = Path(__file__).resolve().parent

# ---------------------------------------------------------------- PASO 1
# Leemos el CSV. "utf-8-sig" elimina la marca invisible (BOM) que Excel agrega.
datos = pd.read_csv(carpeta / 'datos.csv', encoding='utf-8-sig')
print('Filas y columnas:', datos.shape)
print(datos.head())

# Revisamos valores ausentes y filas repetidas.
print('\nValores ausentes por columna:')
print(datos.isna().sum())
print('Filas duplicadas:', datos.duplicated().sum())

# Limpieza de seguridad: si hubiera ausentes o duplicados, se eliminan.
datos = datos.dropna().drop_duplicates()

# Variables de entrada (X) y variable que queremos predecir (y).
COLUMNAS = ['consultas_web', 'inversion_publicidad_soles', 'campana_escolar']
OBJETIVO = 'pedidos_kits'
X = datos[COLUMNAS]
y = datos[OBJETIVO]

# ---------------------------------------------------------------- PASO 2
# 80 % para entrenar y 20 % para probar. random_state fija el sorteo para que
# el resultado sea siempre el mismo.
X_entr, X_prueba, y_entr, y_prueba = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f'\nEntrenamiento: {len(X_entr)} filas | Prueba: {len(X_prueba)} filas')

modelo = LinearRegression()
modelo.fit(X_entr, y_entr)

# ---------------------------------------------------------------- PASO 3
# Coeficientes: cuanto cambia y cuando una X sube 1 unidad y las demas
# se mantienen iguales.
print('\nIntercepto:', round(modelo.intercept_, 4))
for nombre, coef in zip(COLUMNAS, modelo.coef_):
    print(f'  +1 en {nombre}: {coef:+.4f} en {OBJETIVO}')

# ---------------------------------------------------------------- PASO 4
# Evaluacion con los datos de prueba (nunca usados para entrenar).
prediccion = modelo.predict(X_prueba)
mae = mean_absolute_error(y_prueba, prediccion)
r2 = r2_score(y_prueba, prediccion)
print(f'\nMAE (error absoluto medio): {mae:.3f} kits por semana')
print(f'R2  (variacion explicada) : {r2:.3f}')

# ---------------------------------------------------------------- PASO 6
# Guardamos los coeficientes en modelo.json para la aplicacion web.
resumen = {
    'caso': 'Caso 1 - Estimacion de pedidos de kits de robotica',
    'objetivo': OBJETIVO,
    'unidad_objetivo': 'kits por semana',
    'columnas': COLUMNAS,
    'intercepto': float(modelo.intercept_),
    'coeficientes': {c: float(k) for c, k in zip(COLUMNAS, modelo.coef_)},
    'metricas': {
        'mae': float(mae),
        'r2': float(r2),
        'filas_entrenamiento': int(len(X_entr)),
        'filas_prueba': int(len(X_prueba)),
        'filas_total': int(len(datos)),
        'random_state': 42,
    },
}
with open(carpeta / 'modelo.json', 'w', encoding='utf-8') as archivo:
    json.dump(resumen, archivo, indent=2, ensure_ascii=False)

# Copia del modelo completo de scikit-learn.
joblib.dump(modelo, carpeta / 'modelo.pkl')
print('\nArchivos guardados: modelo.json y modelo.pkl')
