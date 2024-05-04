# Modelo de Planeación Agregada

Este repositorio presenta una solución al modelo de planeación agregada en una de sus variantes más sencillas, lee el documento con nuestro modelo [aquí](app_model.md).

## Cómo usarlo

Asegúrate de tener Docker instalado en tu computadora, dentro de tu terminal corre los siguientes comandos.
```bash
docker build -t aggregate_planning:1.0.0 .
docker run aggregate_planning:1.0.0 --data=data/pessimistic/planning_data.xlsx --name=pessimistic
```

Verás que la aplicación no imprimirá en pantalla los resultados del proceso de optimización. Estos se encontrarán en carpetas con el nombre que proveas en el comando anterior. En este caso, el programa tomará como datos de planeación los presentes en el archivo `data/pessimistic/planning_data.xlsx`, y los guardó en una carpeta especial con el nombre de `pessimistic` dentro del directorio `report`.

En esta carpeta se generarán reportes del proceso de solución con las 4 principales variables:
1. Producción: production.csv
2. Inventario: inventory.csv
3. Outsourcing: outsource.csv
4. Envíos: shipment.csv

Habrá un archivo llamado `solver.log` que contendrá el valor que tomó la función objetivo, así como datos importantes del proceso de solución