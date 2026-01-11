"""Subscription Plan Entity"""
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class SubscriptionPlan:
    plan_id: int
    name: str
    price: Decimal
    features: dict
