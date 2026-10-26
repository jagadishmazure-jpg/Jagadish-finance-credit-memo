"""Cost and budget guards. Cost inputs must reject negatives -- a
negative cost would let a caller inflate a budget or hide spend.
"""

import math


def validate_cost(value, field="cost"):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{field} must be finite")
    if value < 0:
        raise ValueError(f"{field} must not be negative")
    return float(value)


class Budget:
    """A capped spend tracker for pipeline runs (synthetic cost units)."""

    def __init__(self, cap):
        self.cap = validate_cost(cap, "cap")
        self.spent = 0.0

    def add(self, cost):
        cost = validate_cost(cost, "cost")
        self.spent += cost
        return self.spent

    @property
    def remaining(self):
        return self.cap - self.spent

    @property
    def over_cap(self):
        return self.spent > self.cap
