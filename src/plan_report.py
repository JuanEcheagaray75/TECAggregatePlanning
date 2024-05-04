import pandas as pd
import pathlib

# Typing
from pulp import LpVariable
from pandas import DataFrame
from typing import List, Mapping, Tuple

type OptVars = Mapping[Tuple[int, ...], LpVariable]


class PlanningReport:
    """Helper class to create csv reports from a set of decision variables storing the optimization results from a Pulp runtime"""

    def __init__(self, opt_variables: Mapping[str, Tuple[List[str], OptVars]]) -> None:
        """Aggregate Planning Report Utility

        Args:
            opt_variables (Mapping[str, Tuple[List[str], OptVars]]): Mapping from
            decision variable group name, to a tuple of a list of column names,
            and a mapping of optimization variables created from pulp
        """

        self.opt_variables: Mapping[str, Tuple[List[str], OptVars]] = opt_variables

    def generate_report(self, report_dir: pathlib.Path) -> None:
        """Helper function to write APP report to a directory

        Args:
            report_dir (pathlib.Path): directory in which to store APP reports in csv
        """
        for var_name, var in self.opt_variables.items():
            column_names: List[str] = var[0]
            column_names.append("amount")
            report_name: str = var_name
            results = []

            decision_vars = var[1]

            for dec_var_idx in decision_vars:
                idx_list = list(dec_var_idx)
                var_value = decision_vars[dec_var_idx].value()
                result = idx_list + [var_value]

                results.append(result)

            df: DataFrame = pd.DataFrame(data=results)
            df.columns = column_names
            df.to_csv(path_or_buf=report_dir / f"{report_name}.csv")
