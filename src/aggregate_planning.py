import pulp as pl
from pathlib import Path
from data_loading import PlanningData
from plan_report import PlanningReport
from typing import Mapping, Self
import pandas as pd

# Typing
from pandas import DataFrame


# Datasets
class AggregatePlanning:
    def __init__(
        self,
        name: str,
        let_down_tol: float,
        init_inventory: int,
        data_dir: Path,
        planning_mapping: PlanningData,
        report_dir: Path,
    ) -> None:
        self.name: str = name
        self.model: pl.LpProblem = pl.LpProblem(name=self.name, sense=pl.LpMaximize)
        self.let_down_tol: float = let_down_tol
        self.init_inventory: int = init_inventory
        self.data_dir: Path = data_dir
        self.planning_mapping: PlanningData = planning_mapping
        self.report_dir: Path = report_dir / self.name
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, sheet_name: str, col_mapper: Mapping[str, str]) -> DataFrame:
        """Load APP data from data_dir and apply a column mapping

        Args:
            sheet_name (str): Name of the excel sheet to process
            col_mapper (Mapping[str, str]): Mapping from natural column name to a standardized name

        Returns:
            DataFrame: Pandas DataFrame with APP data having more concise column names
        """
        df: DataFrame = pd.read_excel(io=self.data_dir, sheet_name=sheet_name).rename(
            mapper=col_mapper, axis=1
        )
        return df

    # Model Initialization
    def init_dataframes(self) -> Self:
        self.centers_df: DataFrame = self.load_data(
            *self.planning_mapping.centers.value
        )
        self.demand_df: DataFrame = self.load_data(*self.planning_mapping.demand.value)
        self.transport_df: DataFrame = self.load_data(
            *self.planning_mapping.transport.value
        )
        self.suppliers_df: DataFrame = self.load_data(
            *self.planning_mapping.suppliers.value
        )
        self.max_suppliers_df: DataFrame = self.load_data(
            *self.planning_mapping.max_suppliers.value
        )

        return self

    def init_sets(self) -> Self:
        self.products = range(1, self.demand_df["product_id"].max() + 1)
        self.centers = range(1, self.centers_df["center_id"].max() + 1)
        self.clients = range(1, self.demand_df["client_id"].max() + 1)
        self.suppliers = range(1, self.suppliers_df["supplier_id"].max() + 1)
        self.periods = range(1, self.demand_df["period"].max() + 1)

        return self

    def init_decision_variables(self) -> Self:
        self.production = pl.LpVariable.dicts(
            name="production",
            indices=(
                (i, j, t)
                for i in self.products
                for j in self.centers
                for t in self.periods
            ),
            lowBound=0,
            cat=pl.LpInteger,
        )
        self.shipment = pl.LpVariable.dicts(
            name="shipment",
            indices=(
                (i, j, k, t)
                for i in self.products
                for j in self.centers
                for k in self.clients
                for t in self.periods
            ),
            lowBound=0,
            cat=pl.LpInteger,
        )
        self.outsource = pl.LpVariable.dicts(
            name="outsource",
            indices=(
                (i, q, k, t)
                for i in self.products
                for q in self.suppliers
                for k in self.clients
                for t in self.periods
            ),
            lowBound=0,
            cat=pl.LpInteger,
        )
        # Inventory doesn't follow the direct implementation, we need to add
        # some initial inventory
        self.inventory = pl.LpVariable.dicts(
            name="inventory",
            indices=(
                (i, j, t)
                for i in self.products
                for j in self.centers
                for t in range(0, self.demand_df["period"].max() + 1)
            ),
            lowBound=0,
            cat=pl.LpInteger,
        )

        return self

    def set_init_inventory(self) -> Self:
        for i in self.products:
            for j in self.centers:
                # Fix initial inventory to a value
                self.inventory[(i, j, 0)].setInitialValue(self.init_inventory)
                self.inventory[(i, j, 0)].fixValue()

        return self

    # Constraints
    def add_inventory_balance(self) -> Self:
        for i in self.products:
            for j in self.centers:
                prod_center_row: DataFrame = self.centers_df[
                    (self.centers_df["product_id"] == i)
                    & (self.centers_df["center_id"] == j)
                ]  # type: ignore

                # Assume both remain constant for every period
                max_production: int = prod_center_row["max_production"].iloc[0]
                max_storage: int = prod_center_row["max_storage"].iloc[0]

                # Fix initial inventory to a value
                self.inventory[(i, j, 0)].setInitialValue(self.init_inventory)
                self.inventory[(i, j, 0)].fixValue()

                for t in self.periods:
                    # Cannot surpass max production and max storage for every prod-center-time combination
                    self.production[(i, j, t)].upBound = max_production
                    self.inventory[(i, j, t)].upBound = max_storage

                    if t > 0:
                        inv_balance: pl.LpConstraint = (
                            self.inventory[(i, j, t - 1)]
                            + self.production[(i, j, t)]
                            - pl.lpSum(
                                vector=(
                                    self.shipment[(i, j, k, t)] for k in self.clients
                                )
                            )
                            - self.inventory[(i, j, t)]
                        )
                        self.model += pl.LpConstraint(
                            e=inv_balance,
                            sense=pl.LpConstraintEQ,
                            name=f"Inventory balance for product {i} on center {j} during period {t}",
                            rhs=0,
                        )
        return self

    def add_max_outsourcing_from_suppliers(self) -> Self:
        for i in self.products:
            for q in self.suppliers:
                max_quantity: int = self.max_suppliers_df[
                    (self.max_suppliers_df["product_id"] == i)
                    & (self.max_suppliers_df["supplier_id"] == q)
                ]["max_quantity"].iloc[0]
                for t in self.periods:
                    self.model += pl.LpConstraint(
                        e=pl.lpSum(
                            vector=(self.outsource[(i, q, k, t)] for k in self.clients)
                        ),
                        sense=pl.LpConstraintLE,
                        name=f"Max acquisition for supplier {q} and product {i} on period {t}",
                        rhs=max_quantity,
                    )
        return self

    def add_satisfy_demand(self) -> Self:
        for i in self.products:
            for k in self.clients:
                for t in self.periods:
                    total_shipment: pl.LpAffineExpression = pl.lpSum(
                        vector=(self.shipment[(i, j, k, t)] for j in self.centers)
                    )
                    total_outsourcing: pl.LpAffineExpression = pl.lpSum(
                        vector=(self.outsource[(i, q, k, t)] for q in self.suppliers)
                    )
                    total_sent: pl.LpAffineExpression = (
                        total_shipment + total_outsourcing
                    )
                    current_demand: int = self.demand_df[
                        (self.demand_df["product_id"] == i)
                        & (self.demand_df["client_id"] == k)
                        & (self.demand_df["period"] == t)
                    ]["demand"].iloc[0]

                    # Do not send more than they requested
                    self.model += pl.LpConstraint(
                        e=total_sent,
                        sense=pl.LpConstraintLE,
                        name=f"Upper bound for demand of product {i} from client {k} on period {t}",
                        rhs=current_demand,
                    )
                    # Send at least some of what they requested
                    self.model += pl.LpConstraint(
                        e=total_sent,
                        sense=pl.LpConstraintGE,
                        name=f"Lower bound for demand of product {i} from client {k} on period {t}",
                        rhs=int(current_demand * self.let_down_tol),
                    )

        return self

    # Objective function components
    def sales_revenue(self) -> pl.LpAffineExpression:
        sales: pl.LpAffineExpression = pl.lpSum(
            vector=(
                self.shipment[(i, j, k, t)]
                * self.demand_df[
                    (self.demand_df["product_id"] == i)
                    & (self.demand_df["client_id"] == k)
                    & (self.demand_df["period"] == t)
                ]["purchase_price"].iloc[0]
                for i in self.products
                for j in self.centers
                for k in self.clients
                for t in self.periods
            )
        )

        return sales

    def production_cost(self) -> pl.LpAffineExpression:
        production_cost: pl.LpAffineExpression = pl.lpSum(
            vector=(
                self.production[(i, j, t)]
                * self.centers_df[
                    (self.centers_df["product_id"] == i)
                    & (self.centers_df["center_id"] == j)
                ]["production_cost"].iloc[0]
                for i in self.products
                for j in self.centers
                for t in self.periods
            )
        )

        return production_cost

    def shipment_cost(self) -> pl.LpAffineExpression:
        shipment_cost: pl.LpAffineExpression = pl.lpSum(
            vector=(
                self.shipment[(i, j, k, t)]
                * self.transport_df[
                    (self.transport_df["product_id"] == i)
                    & (self.transport_df["center_id"] == j)
                    & (self.transport_df["client_id"] == k)
                ]["transportation_cost"].iloc[0]
                for i in self.clients
                for j in self.centers
                for k in self.clients
                for t in self.periods
            )
        )

        return shipment_cost

    def outsourcing_cost(self) -> pl.LpAffineExpression:
        outsourcing_cost: pl.LpAffineExpression = pl.lpSum(
            vector=(
                self.outsource[(i, q, k, t)]
                * self.suppliers_df[
                    (self.suppliers_df["product_id"] == i)
                    & (self.suppliers_df["supplier_id"] == q)
                    & (self.suppliers_df["client_id"] == k)
                ]["product_cost"].iloc[0]
                for i in self.products
                for q in self.suppliers
                for k in self.clients
                for t in self.periods
            )
        )

        return outsourcing_cost

    def inventory_cost(self) -> pl.LpAffineExpression:
        inventory_cost: pl.LpAffineExpression = pl.lpSum(
            vector=(
                self.inventory[(i, j, t)]
                * self.centers_df[
                    (self.centers_df["product_id"] == i)
                    & (self.centers_df["center_id"] == j)
                ]["inventory_cost"].iloc[0]
                for i in self.products
                for j in self.centers
                for t in self.periods
                if t > 0
            )
        )

        return inventory_cost

    def add_objective(self) -> Self:
        self.model += (
            self.sales_revenue()
            - self.production_cost()
            - self.shipment_cost()
            - self.outsourcing_cost()
            - self.inventory_cost()
        )
        return self

    # Model solution and reporting
    def solve(self) -> None:
        self.model.solve(solver=pl.PULP_CBC_CMD(logPath=self.report_dir / "solver.log"))

    def solution_report(self) -> None:
        report = PlanningReport(
            opt_variables={
                "production": (["product_id", "center_id", "period"], self.production),
                "shipment": (
                    ["product_id", "center_id", "client_id", "period"],
                    self.shipment,
                ),
                "outsource": (
                    ["product_id", "supplier_id", "client_id", "period"],
                    self.outsource,
                ),
                "inventory": (["product_id", "center_id", "period"], self.inventory),
            }
        )
        report.generate_report(report_dir=self.report_dir)
