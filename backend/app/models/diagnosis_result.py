"""Nested diagnosis outcome — separate from transport / API schemas."""



from dataclasses import dataclass, field





@dataclass(frozen=True)

class FaultRef:

    code: str

    description: str





@dataclass(frozen=True)

class TrendMetric:

    metric: str

    direction: str

    from_value: float | None = None

    to_value: float | None = None

    delta: float | None = None



    @classmethod

    def from_dict(cls, data: dict) -> "TrendMetric":

        return cls(

            metric=str(data.get("metric", "")),

            direction=str(data.get("direction", "unknown")),

            from_value=data.get("from"),

            to_value=data.get("to"),

            delta=data.get("delta"),

        )





@dataclass(frozen=True)

class DiagnosisResult:

    risk_level: str

    possible_causes: list[str]

    recommendations: list[str]

    fault_codes: list[str] = field(default_factory=list)

    primary_fault: FaultRef | None = None

    related_faults: list[FaultRef] = field(default_factory=list)

    fault_evolution: list[str] = field(default_factory=list)

    temperature_trend: TrendMetric | None = None

    vibration_trend: TrendMetric | None = None


