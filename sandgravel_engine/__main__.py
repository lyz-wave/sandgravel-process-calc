"""CLI entry point: python -m sandgravel_engine [options]

Examples:
  python -m sandgravel_engine --config option1
  python -m sandgravel_engine --config option1 --throughput 1800 --output result.xlsx
  python -m sandgravel_engine --config option2 --grading 0,0,0,35,25,40
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sandgravel_engine.process_flow import run_option
from sandgravel_engine.io import export_to_excel, export_to_json
from sandgravel_engine.models import BalanceResult


def main():
    parser = argparse.ArgumentParser(
        description="砂石加工系统工艺计算引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m sandgravel_engine --config option1
  python -m sandgravel_engine --config option2 --throughput 1800
  python -m sandgravel_engine --config option1 --grading 65,15,8,6,4,2
        """,
    )
    parser.add_argument("--config", "-c", default="option1",
                        choices=["option1", "option2"], help="方案名称")
    parser.add_argument("--throughput", "-t", type=float,
                        help="系统处理量 (T/H)，覆盖配置文件默认值")
    parser.add_argument("--grading", "-g",
                        help="原料级配，6个逗号分隔数值 (>150,150-80,80-40,40-20,20-5,<5)")
    parser.add_argument("--output", "-o", help="输出Excel文件路径")
    parser.add_argument("--json", action="store_true", help="输出JSON到stdout")

    args = parser.parse_args()

    grading = None
    if args.grading:
        grading = [float(x.strip()) for x in args.grading.split(",")]
        if len(grading) != 6:
            parser.error("级配需要6个数值")
        if abs(sum(grading) - 100) > 0.1:
            parser.error(f"级配之和必须为100%%，当前={sum(grading):.1f}%%")

    result = run_option(args.config, throughput=args.throughput, grading=grading)

    if args.json:
        print(export_to_json(_to_balance_result(result)))
        return

    print(f"方案: {args.config}")
    print(f"处理量: {result.system_throughput:.0f} T/H")
    print(f"产品分布:")
    for name, pct in result.products.items():
        print(f"  {name}: {pct:.2f}%")
    print(f"循环负荷: >40mm={result.recirc_gt40:.2f}x  制砂={result.recirc_20_5:.2f}x")
    print(f"设备配置:")
    for eq in result.equipment:
        print(f"  {eq.model} ×{eq.quantity}  ({eq.unit_capacity:.0f}t/h, 负荷{eq.load_factor:.2f})")

    if args.output:
        br = _to_balance_result(result)
        export_to_excel(br, args.output)
        print(f"\n已导出: {args.output}")


def _to_balance_result(result) -> BalanceResult:
    from sandgravel_engine.models import BalanceResult
    return BalanceResult(
        streams=result.streams,
        equipment=result.equipment,
        iterations=result.iterations,
        convergence_error=result.error,
    )


if __name__ == "__main__":
    main()
