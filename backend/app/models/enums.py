"""Valeurs autorisees par les contraintes CHECK du schema.

Le code est en anglais, les valeurs metier restent en francais car elles sont
stockees telles quelles en base et affichees dans l'interface.
"""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    AGENT = "agent"
    COMPTABLE = "comptable"


class PropertyType(StrEnum):
    APPARTEMENT = "appartement"
    VILLA = "villa"
    TERRAIN = "terrain"
    BUREAU = "bureau"
    COMMERCE = "commerce"


class PropertyStatus(StrEnum):
    DISPONIBLE = "disponible"
    LOUE = "loue"
    EN_TRAVAUX = "en_travaux"
    INDISPONIBLE = "indisponible"


class LeaseStatus(StrEnum):
    ACTIF = "actif"
    TERMINE = "termine"
    RESILIE = "resilie"


class PaymentMethod(StrEnum):
    ESPECES = "especes"
    VIREMENT_BANCAIRE = "virement_bancaire"
    CHEQUE = "cheque"
    MOBILE_MONEY_ORANGE = "mobile_money_orange"
    MOBILE_MONEY_MTN = "mobile_money_mtn"
    MOBILE_MONEY_MOOV = "mobile_money_moov"
    WAVE = "wave"


class PaymentStatus(StrEnum):
    PAYE = "paye"
    EN_ATTENTE = "en_attente"
    EN_RETARD = "en_retard"
    REJETE = "rejete"


class TicketPriority(StrEnum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    URGENTE = "urgente"


class TicketStatus(StrEnum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    FERME = "ferme"


def sql_values(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    """Retourne les valeurs d'une enumeration, pour les contraintes CHECK."""
    return tuple(member.value for member in enum_cls)


def check_expression(column: str, enum_cls: type[StrEnum]) -> str:
    """Construit l'expression SQL "col IN ('a', 'b')" d'une contrainte CHECK."""
    joined = ", ".join(f"'{value}'" for value in sql_values(enum_cls))
    return f"{column} IN ({joined})"
