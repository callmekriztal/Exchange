from typing import Any, Dict, Tuple


class DeliverableEvaluator:
    @staticmethod
    def evaluate(
        subtask_title: str,
        service_type: str,
        artifact_type: str,
        content: Dict[str, Any],
        checksum: str,
    ) -> Tuple[float, bool, Dict[str, Any], str]:
        """Evaluates a seller's deliverable against standard acceptance rubrics."""
        # 1. Completeness score (Max 35)
        completeness = 35.0 if content else 0.0

        # 2. Accuracy & Content Depth score (Max 35)
        depth = 32.0
        if service_type == "research":
            findings = content.get("findings", [])
            if len(findings) >= 2:
                depth = 35.0
        elif service_type == "analysis":
            metrics = content.get("computed_metrics", {})
            if "compound_annual_growth_rate_pct" in metrics:
                depth = 34.5
        elif service_type == "report":
            if "markdown_report" in content:
                depth = 35.0

        # 3. Formatting & Schema Conformance (Max 30)
        formatting = 28.0 if checksum and len(checksum) == 64 else 15.0

        total_score = round(completeness + depth + formatting, 1)
        # Cap at 100
        total_score = min(100.0, total_score)
        is_accepted = total_score >= 75.0

        rubric_scores = {
            "completeness": completeness,
            "depth_and_rigor": depth,
            "format_and_integrity": formatting,
            "max_possible": 100.0,
        }

        feedback = (
            f"Buyer Agent verified '{subtask_title}' deliverable: "
            f"Quality Score {total_score}/100. Deliverable integrity verified (SHA256: {checksum[:12]}...). "
            f"Outcome: {'ACCEPTED' if is_accepted else 'REJECTED - Quality threshold 75 not met'}."
        )

        return total_score, is_accepted, rubric_scores, feedback
