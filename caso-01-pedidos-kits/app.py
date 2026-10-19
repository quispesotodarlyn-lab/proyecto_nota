# APLICACION WEB | Caso 1 - Estimacion de pedidos de kits de robotica
# SENATI - Taller de Machine Learning y Deep Learning
#
# Solo Python + Flask + HTML + CSS (sin JavaScript).
# La prediccion se calcula con los coeficientes guardados en modelo.json:
#     y = intercepto + coef1 * x1 + coef2 * x2 + coef3 * x3
#
# Uso:  python app.py   y abrir  http://127.0.0.1:5000

from pathlib import Path
import json
import math

from flask import Flask, render_template, request

app = Flask(__name__)
carpeta = Path(__file__).resolve().parent

# Cargamos una sola vez los coeficientes que dejo entrenar.py.
with open(carpeta / 'modelo.json', encoding='utf-8') as archivo:
    modelo = json.load(archivo)

# Descripcion de los campos del formulario y de sus rangos validos.
CAMPOS = [
    {'nombre': 'consultas_web', 'etiqueta': 'Consultas web de la semana', 'unidad': 'consultas',
     'tipo': 'numero', 'min': 5, 'max': 70, 'step': 1, 'entero': True, 'ejemplo': 20,
     'ayuda': 'Número entero entre 5 y 70.'},
    {'nombre': 'inversion_publicidad_soles', 'etiqueta': 'Inversión en publicidad', 'unidad': 'soles (S/)',
     'tipo': 'numero', 'min': 0, 'max': 1100, 'step': 'any', 'ejemplo': 200,
     'ayuda': 'Monto entre S/ 0 y S/ 1100.'},
    {'nombre': 'campana_escolar', 'etiqueta': '¿Hay campaña escolar?', 'unidad': '',
     'tipo': 'opciones', 'opciones': [('0', 'No (0)'), ('1', 'Sí (1)')], 'defecto': '0',
     'ayuda': 'Indicador de campaña: 0 = no, 1 = sí.'},
]

TITULO = 'Estimador de pedidos semanales de kits de robótica'
ETIQUETA = 'Tienda educativa · Planificación de pedidos'
DESCRIPCION = 'Ingresa los datos de una semana para estimar cuántos kits de robótica podrían pedirse.'
AVISO = 'es una estimación basada en datos simulados. Úsala como apoyo para planificar, no como garantía de ventas.'


def validar(formulario):
    """Revisa cada campo. Devuelve (textos, errores, numeros)."""
    textos, errores, numeros = {}, {}, {}
    for campo in CAMPOS:
        nombre = campo['nombre']
        texto = formulario.get(nombre, '').strip()
        textos[nombre] = texto

        if texto == '':
            errores[nombre] = 'Completa este campo.'
            continue

        # Campos de tipo "opciones": solo se aceptan los valores listados (0 o 1).
        if campo['tipo'] == 'opciones':
            validos = [valor for valor, _ in campo['opciones']]
            if texto in validos:
                numeros[nombre] = float(texto)
            else:
                errores[nombre] = 'Elige una opción válida (0 o 1).'
            continue

        # Campos numericos: aceptamos coma o punto decimal.
        try:
            numero = float(texto.replace(',', '.'))
        except ValueError:
            errores[nombre] = 'Escribe un número válido.'
            continue

        if not math.isfinite(numero):
            errores[nombre] = 'Escribe un número válido.'
        elif not campo['min'] <= numero <= campo['max']:
            errores[nombre] = (f"El valor debe estar entre {campo['min']:g} "
                               f"y {campo['max']:g}.")
        elif campo.get('entero') and numero != int(numero):
            errores[nombre] = 'Escribe un número entero.'
        else:
            numeros[nombre] = numero
    return textos, errores, numeros


def predecir(numeros):
    """Aplica la ecuacion de la regresion lineal con los coeficientes del JSON."""
    total = modelo['intercepto']
    for nombre, coef in modelo['coeficientes'].items():
        total += coef * numeros[nombre]
    return total


def formatear(estimacion, mae):
    """Convierte la estimacion en el texto que se muestra en la pagina."""
    estimacion = max(estimacion, 0)  # no puede haber pedidos negativos
    return {
        'titulo': 'Pedidos estimados para la semana',
        'valor': f'{round(estimacion)} kits',
        'detalle': (f'Valor calculado: {estimacion:.1f} kits. En la prueba, el modelo se '
                    f'equivocó en promedio {mae:.1f} kits por semana.'),
    }


@app.route('/', methods=['GET', 'POST'])
def inicio():
    textos = {campo['nombre']: campo.get('defecto', '') for campo in CAMPOS}
    errores, resultado = {}, None

    # POST = el usuario pulso el boton "Calcular".
    if request.method == 'POST':
        textos, errores, numeros = validar(request.form)
        if not errores:
            estimacion = predecir(numeros)
            resultado = formatear(estimacion, modelo['metricas']['mae'])

    return render_template(
        'index.html',
        campos=CAMPOS, valores=textos, errores=errores, resultado=resultado,
        titulo=TITULO, etiqueta=ETIQUETA, descripcion=DESCRIPCION, aviso=AVISO,
        metricas=modelo['metricas'],
    )


if __name__ == '__main__':
    # debug=True solo para practicar en la computadora.
    app.run(debug=True)
