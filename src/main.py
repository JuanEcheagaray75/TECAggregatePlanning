import argparse
from argparse import ArgumentParser
from pathlib import Path
from aggregate_planning import AggregatePlanning
from data_loading import PlanningData


def main() -> None:
    parser: ArgumentParser = ArgumentParser(description="Aggregate Planning Solver")
    parser.add_argument(
        "-d", "--data", type=str, help="Path to planning data excel file"
    )
    parser.add_argument("-n", "--name", type=str, help="Aggregate Plannning Model Name")
    parser.add_argument(
        "-l", "--letdown", type=float, help="Minimum coverage %", nargs="?", default=0.9
    )
    parser.add_argument(
        "-i", "--inventory", type=int, help="Initial inventory", nargs="?", default=50
    )
    args: argparse.Namespace = parser.parse_args()

    planning_data_path: Path = Path(args.data)

    assert (
        planning_data_path.is_file()
    ), f"Provided data path at {args.data} doesn't exist"
    assert args.inventory >= 0, "Initial inventory is a negative number"
    assert 0 < args.letdown <= 1, "Letdown is not in (0, 1]"

    app_problem: AggregatePlanning = AggregatePlanning(
        name=args.name,
        let_down_tol=args.letdown,
        init_inventory=args.inventory,
        data_dir=planning_data_path,
        report_dir=Path("report"),
        planning_mapping=PlanningData,
    )
    app_problem = (
        app_problem.init_dataframes()
        .init_sets()
        .init_decision_variables()
        .set_init_inventory()
        .add_inventory_balance()
        .add_max_outsourcing_from_suppliers()
        .add_satisfy_demand()
        .add_objective()
    )
    app_problem.solve()
    app_problem.solution_report()


if __name__ == "__main__":
    main()
