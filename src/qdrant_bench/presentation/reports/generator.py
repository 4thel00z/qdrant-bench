from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from qdrant_bench.domain.entities.core import Experiment, Run


class ReportGenerator:
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("qdrant_bench.presentation", "reports/templates"),
            autoescape=select_autoescape()
        )

    def generate(self, experiment: Experiment, runs: list[Run]) -> str:
        template = self.env.get_template("report.html")

        # Sort runs by time
        runs = sorted(runs, key=lambda r: r.start_time if r.start_time else 0)

        # Determine best run
        completed_runs = [r for r in runs if r.status == "COMPLETED"]
        best_run = max(completed_runs, key=lambda r: r.metrics.get("f1", 0.0)) if completed_runs else None

        # Prepare chart data
        charts_config = self._prepare_charts(runs)

        return template.render(
            experiment=experiment,
            runs=runs,
            best_run=best_run,
            charts=charts_config
        )

    def _prepare_charts(self, runs: list[Run]) -> dict[str, Any]:
        completed_runs = [r for r in runs if r.status == "COMPLETED"]

        # F1 over Time
        f1_chart = {
            "type": "line",
            "data": {
                "labels": [str(r.id)[:8] for r in completed_runs],
                "datasets": [{
                    "label": "F1 Score",
                    "data": [r.metrics.get("f1", 0.0) for r in completed_runs],
                    "borderColor": "rgb(75, 192, 192)",
                    "tension": 0.1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {"title": {"display": True, "text": "F1 Score Progression"}}
            }
        }

        # Pareto Frontier (Recall vs Latency)
        pareto_chart = {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "label": "Runs",
                    "data": [
                        {"x": r.metrics.get("p95_latency", 0.0), "y": r.metrics.get("recall", 0.0)}
                        for r in completed_runs
                    ],
                    "backgroundColor": "rgb(255, 99, 132)"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {"title": {"display": True, "text": "Recall vs Latency (Pareto)"}},
                "scales": {
                    "x": {"type": "linear", "position": "bottom", "title": {"display": True, "text": "p95 Latency (s)"}},
                    "y": {"title": {"display": True, "text": "Recall"}}
                }
            }
        }

        return {
            "f1_chart": f1_chart,
            "pareto_chart": pareto_chart
        }




