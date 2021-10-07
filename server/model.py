from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Visitor:
    id: str


@dataclass
class Product:
    id = -1
    name: str
    activity_type: str


@dataclass
class Sell:
    id = -1
    visitor_id: str
    product_id: str


@dataclass
class VisitorVisit:
    id = -1
    date: datetime
    duration_secs: int
    is_new: bool
    host: str
    visitor_id: str


@dataclass
class ProductVisit:
    id = -1
    date: datetime
    product_id: int
