# Planeación agregada

## Conjuntos

- $i \in I = {1, 2, \dots}:=$ Conjunto de productos
- $j \in J = {1, 2, \dots}:=$ Conjunto de plantas
- $k \in K = {1, 2, \dots}:=$ Conjunto de clientes
- $q \in Q = {1, 2, \dots}:=$ Conjunto de proveedores de producto terminado
- $t \in T = {1, 2, \dots}:=$ Conjunto de periodos de producción

## Variables de decisión

- $x_{ijt} \in \mathbb{N}:=$ Producción del producto $i$ en planta $j$ en periodo $t$
- $y_{ijkt} \in \mathbb{N}:=$ Cantidad de producto $i$ a enviar desde la planta $j$ al cliente $k$ en periodo $t$
- $z_{iqkt} \in \mathbb{N}:=$ Cantidad de producto $i$ a comprar al proveedor $q$ para que se la envíe al cliente $k$ en el periodo $t$
- $I_{ijt} \in \mathbb{N}:=$ Cantidad de producto $i$ a inventariar en la planta $j$ en periodo $t$

## Parámetros

Sobre capacidades máximas que se mantienen estables durante todo el periodo de planificación:
- $MS_{ij} \in \mathbb{N}:=$ Capacidad máxima de almacenamiento en unidades del producto $i$ en planta $j$
- $MP_{ij} \in \mathbb{N}:=$ Capacidad máxima de producción en unidades del produ++cto $i$ en planta $j$
- $MO_{iq} \in \mathbb{N}:=$ Capacidad máxima de compra en unidades del producto $i$ para el proveedor $q$ Sobre montos:
- $PC_{ij} \in \mathbb{R}^+:=$ Costo de producción unitario del producto $i$ en planta $j$
- $PP_{ikt} \in \mathbb{R}^+:=$ Precio de compra unitario del producto $i$ para el cliente $k$ en periodo $t$
- $OC_{iqk} \in \mathbb{R}^+:=$ Precio de compra total (abstrayendo costos de compra, transporte, etc...) unitario de producto terminado $i$ del proveedor $q$ para el cliente $k$
- $TC_{ijk} \in \mathbb{R}^+:=$ Costo de transporte unitario de producto $i$ desde la planta $j$ al cliente $k$
- $IC_{ij} \in \mathbb{R}^+:=$ Costo de inventario unitario de producto $i$ en planta $j$ Sobre clientes:
- $D_{ikt} \in \mathbb{N}:=$ Demanda del producto $i$ del cliente $k$ para el periodo $t$

Sobre el modelo general se agregaron los siguientes parámetros a seleccionar de forma arbitraria:
- $ML \in (0, 1] :=$ Proporción mínima de la demanda de un cliente que debe ser entregada para todos los periodos y todos los productos
- $I_{ij0}$ se estable a un valor constante al comienzo de la corrida del programa

## Restricciones

- No superar la capacidad máxima de inventario para todos los productos en todas las plantas para todos los periodos:
$$I_{ijt} \leq MS_{ij} \quad \forall t$$
- No superar la capacidad máxima de producción para todos los productos en todas las plantas para todos los periodos:
$$x_{ijt} \leq MP_{ij} \quad \forall t$$
- No superar la capacidad máxima de compra de productos para los proveedores outsourcing:
$$\sum_k z_{iqkt} \leq MO_{iq} \quad \forall i, q, t$$
- Balancear inventario:
$$I_{ij(t-1)} + x_{ijt} = \sum_k y_{ijkt} + I_{ijt} \quad \forall i,j,t$$
- Satisfacer la demanda de los clientes (cota superior):
$$\sum_j y_{ijkt} + \sum_q z_{iqkt} \leq D_{ikt} \quad \forall i, k, t$$
- Satisfacer la demanda de los clientes (cota inferior):
$$\sum_j y_{ijkt} + \sum_q z_{iqkt} \geq \lfloor ML \cdot D_{ikt} \rfloor \quad \forall i, k, t$$

  ## Función objetivo:

$$\begin{equation} z_{sales} = \sum_i \sum_j \sum_k \sum_t y_{ijkt} \cdot PP_{ikt} \end{equation}$$
$$ \begin{equation} z_{production} = \sum_i \sum_j \sum_t x_{ijt} \cdot PC_{ij} \end{equation} $$
$$ \begin{equation} z_{shipment} = \sum_i \sum_j \sum_k \sum_t y_{ijkt} \cdot TC_{ijk} \end{equation} $$
$$\begin{equation}z_{outsourcing} = \sum_i \sum_q \sum_k \sum_t z_{iqkt} \cdot OC_{iqk}\end{equation}$$
$$\begin{equation} z_{inventory} = \sum_i \sum_j \sum_t x_{ijt} \cdot PC_{ij} \end{equation}$$
$$z=Z_{sales} - z_{production} - z_{shipment} - z_{outsourcing} - z_{inventory}$$
