# Caso 1 - Estimación de pedidos de kits de robótica

## Explicación en 10 líneas

1. Usé `datos.csv`: 110 semanas simuladas, sin valores ausentes ni filas repetidas.
2. X = consultas_web, inversion_publicidad_soles y campana_escolar; y = pedidos_kits.
3. Reservé 80 % para entrenar (88 semanas) y 20 % para probar (22 semanas), con `random_state=42`.
4. Entrené una `LinearRegression` (regresión lineal múltiple) con scikit-learn.
5. Cada consulta web extra suma ≈ 0.35 kits por semana, manteniendo lo demás igual.
6. Cada S/ 100 adicionales de publicidad suman ≈ 0.67 kits por semana.
7. Una semana con campaña escolar trae ≈ 5.02 kits más que una sin campaña.
8. En la prueba, MAE = 2.95: el modelo falla en promedio ≈ 3.0 kits por semana (el promedio real es ≈ 19).
9. R² = 0.79: el modelo explica ≈ 79 % de la variación; el resto depende de factores no medidos.
10. La web (Flask + HTML + CSS, sin JavaScript) valida rangos, lee `modelo.json` y muestra la estimación al pulsar «Calcular».

## Resultados de las pruebas obligatorias

| Prueba | Resultado de la página |
|---|---|
| Semana con 20 consultas, S/ 200 y sin campaña | 10 kits (9.8) |
| Semana con 55 consultas, S/ 800 y con campaña | 31 kits (31.0) |

Las capturas están en la carpeta `capturas/` y el detalle en `pruebas_resultados.txt`.

## Conclusiones sobre los límites del modelo

- **Datos simulados y pocos:** solo 110 semanas, y la prueba usa apenas 22; las métricas cambiarían con otra separación.
- **Error que no desaparece:** con R² = 0.79, ≈ 21 % de la variación queda sin explicar; en una semana concreta el error puede superar los 3.0 kits promedio.
- **Supone una relación lineal y constante:** cada consulta o cada sol de publicidad aporta lo mismo siempre; en la realidad la publicidad suele rendir cada vez menos.
- **Solo 3 variables:** no considera precio, stock, feriados, competencia ni el calendario escolar real.
- **No extrapola:** fuera de 5–70 consultas y S/ 0–1100 la aplicación rechaza el dato porque el modelo no fue entrenado ahí.
- **Uso recomendado:** apoyo para planificar compras; la decisión final debe verificarse con el criterio del encargado de la tienda.
