"""Tool: compute numeric risk score from sensor readings."""

from typing import Any

from app.tools.base import ToolContext, ToolResult
from app.tools.schemas import CalculateRiskScoreInput, CalculateRiskScoreOutput


class CalculateRiskScoreTool:
    name = "calculate_risk_score"
    description = "Calculate risk score (0-100) from sensor metrics"

    def run(self, payload: dict[str, Any], context: ToolContext) -> ToolResult:
        _ = context
        inp = CalculateRiskScoreInput.model_validate(payload)
        score = 0.0
        if inp.temperature > 90:
            score += 40
        elif inp.temperature > 80:
            score += 25
        elif inp.temperature > 70:
            score += 10

        if inp.vibration > 8:
            score += 35
        elif inp.vibration > 5:
            score += 20

        if inp.pressure < 15:
            score += 15
        if inp.rpm > 4000:
            score += 10

        risk_score = min(100, int(round(score)))
        out = CalculateRiskScoreOutput(risk_score=risk_score)
        return ToolResult(
            tool_name=self.name,
            input=inp.model_dump(),
            output=out.model_dump(),
        )
