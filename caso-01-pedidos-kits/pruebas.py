# PRUEBAS | Caso 1 - Estimacion de pedidos de kits de robotica
# Envia al formulario las pruebas obligatorias (y algunas de validacion)
# usando el cliente de pruebas de Flask, sin abrir el navegador.
#
# Uso:  python pruebas.py

import re
from pathlib import Path

import joblib
import pandas as pd

from app import app, CAMPOS

carpeta = Path(__file__).resolve().parent
modelo_pkl = joblib.load(carpeta / 'modelo.pkl')
columnas = [c['nombre'] for c in CAMPOS]
cliente = app.test_client()

lineas = []


def registrar(texto=''):
    print(texto)
    lineas.append(texto)


# ---- Pruebas obligatorias: deben producir una prediccion ----
PRUEBAS = [
    ('Semana con 20 consultas, S/ 200 y sin campana',
     {'consultas_web': '20', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
    ('Semana con 55 consultas, S/ 800 y con campana',
     {'consultas_web': '55', 'inversion_publicidad_soles': '800', 'campana_escolar': '1'}),
]

registrar('PRUEBAS OBLIGATORIAS (resultado de la pagina vs. modelo.pkl)')
for nombre, formulario in PRUEBAS:
    respuesta = cliente.post('/', data=formulario).get_data(as_text=True)
    mostrado = re.search(r'class="resultado-valor">([^<]+)<', respuesta)
    entrada = pd.DataFrame([[float(formulario[c]) for c in columnas]], columns=columnas)
    esperado = modelo_pkl.predict(entrada)[0]
    registrar(f'- {nombre}')
    registrar(f'    entrada          : {formulario}')
    registrar(f'    la pagina muestra: {mostrado.group(1) if mostrado else "SIN RESULTADO"}')
    registrar(f'    modelo.pkl       : {esperado:.4f}')

# ---- Pruebas de validacion: deben RECHAZAR el valor ----
INVALIDAS = [
    ('Consultas = 4 (menor que 5)', {'consultas_web': '4', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
    ('Consultas = 71 (mayor que 70)', {'consultas_web': '71', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
    ('Publicidad = S/ 1200 (mayor que 1100)', {'consultas_web': '20', 'inversion_publicidad_soles': '1200', 'campana_escolar': '0'}),
    ('Publicidad = -50 (negativa)', {'consultas_web': '20', 'inversion_publicidad_soles': '-50', 'campana_escolar': '0'}),
    ('Campana = 2 (solo se permite 0 o 1)', {'consultas_web': '20', 'inversion_publicidad_soles': '200', 'campana_escolar': '2'}),
    ('Texto en lugar de numero', {'consultas_web': 'abc', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
    ('Campo vacio', {'consultas_web': '', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
]

registrar('')
registrar('PRUEBAS DE VALIDACION (deben mostrar un mensaje de error y ningun resultado)')
for nombre, formulario in INVALIDAS:
    respuesta = cliente.post('/', data=formulario).get_data(as_text=True)
    hay_error = 'class="error"' in respuesta
    hay_resultado = 'class="resultado"' in respuesta
    estado = 'OK' if hay_error and not hay_resultado else 'FALLO'
    registrar(f'- {nombre}: {estado}')

with open(carpeta / 'pruebas_resultados.txt', 'w', encoding='utf-8') as archivo:
    archivo.write('\n'.join(lineas) + '\n')
