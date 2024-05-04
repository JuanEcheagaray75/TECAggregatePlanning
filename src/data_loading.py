from enum import Enum


class PlanningData(Enum):
    "Enum Class to store the Excel sheet name and the column remapping"

    centers = (
        "Plantas",
        {
            "Producto": "product_id",
            "Planta": "center_id",
            "Costo de produccion por unidad (MXN)": "production_cost",
            "Capacidad máxima de producción de unidades": "max_production",
            "Capacidad máxima de almacenamiento de unidades": "max_storage",
            "Costo de almacenamiento por unidad (MXN)": "inventory_cost",
        },
    )
    demand = (
        "Demanda",
        {
            "Cliente ": "client_id",
            "Id producto": "product_id",
            "Periodo": "period",
            "Demanda de unidades": "demand",
            "Precio de Compra por unidad (MXN)": "purchase_price",
        },
    )
    transport = (
        "Red Logistica",
        {
            "Producto": "product_id",
            "Planta": "center_id",
            "Cliente": "client_id",
            "Costo de transporte  por unidad (MXN)": "transportation_cost",
        },
    )
    suppliers = (
        "Proveedores",
        {
            "Producto": "product_id",
            "Proveedor": "supplier_id",
            "Cliente": "client_id",
            "Costo de compra de producto terminado": "product_cost",
        },
    )
    max_suppliers = (
        "Cant. Máxima Proveedores",
        {
            "Producto": "product_id",
            "Proveedor": "supplier_id",
            "Cantidad": "max_quantity",
        },
    )
