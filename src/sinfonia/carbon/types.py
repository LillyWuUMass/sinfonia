from enum import Enum


class EnergyReportMethodType(Enum):
    RAPL = "rapl"
    OBELIX = "obelix"
    