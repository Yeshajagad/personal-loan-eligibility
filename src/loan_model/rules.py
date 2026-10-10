"""Turns rule rows from lender_rules.csv into objects the engine can query."""
from dataclasses import dataclass

from .catalog import TEXT_RULES
from .common import DATA_DIR, read_csv


@dataclass(frozen=True)
class Rule:
    rule_name: str
    value: object  # float, or a set of strings for list rules
    applies_to: str
    city_group: str
    rule_status: str
    source_url: str
    date_read: str


def parse_value(rule_name, raw):
    if rule_name in TEXT_RULES:
        return {part.strip() for part in raw.split("|") if part.strip()}
    return float(raw)


class LenderRules:
    def __init__(self, lender_id, name, rules):
        self.lender_id = lender_id
        self.name = name
        self.rules = rules

    def get(self, rule_name, employment_type, city_group):
        """Best matching rule. A specific row (e.g. metro) beats an 'all' row."""
        best, best_score = None, -1
        for rule in self.rules:
            if rule.rule_name != rule_name:
                continue
            if rule.applies_to not in ("all", employment_type):
                continue
            if rule.city_group not in ("all", city_group):
                continue
            score = (rule.applies_to != "all") + (rule.city_group != "all")
            if score > best_score:
                best, best_score = rule, score
        return best

    def value(self, rule_name, employment_type, city_group):
        rule = self.get(rule_name, employment_type, city_group)
        return None if rule is None else rule.value


def build_lender_rules(lender_rows, rule_rows):
    """Group rule rows by lender, in the order of lender_rows."""
    by_lender = {row["lender_id"]: [] for row in lender_rows}
    for row in rule_rows:
        if row["lender_id"] not in by_lender:
            continue
        by_lender[row["lender_id"]].append(Rule(
            rule_name=row["rule_name"],
            value=parse_value(row["rule_name"], row["value"]),
            applies_to=row["applies_to"],
            city_group=row["city_group"],
            rule_status=row["rule_status"],
            source_url=row["source_url"],
            date_read=row["date_read"],
        ))
    return [LenderRules(r["lender_id"], r["lender_name"], by_lender[r["lender_id"]])
            for r in lender_rows]


def load_all(rules_file="lender_rules.csv"):
    """Load every lender and rule from the data folder."""
    _, lender_rows = read_csv(DATA_DIR / "lenders.csv")
    _, rule_rows = read_csv(DATA_DIR / rules_file)
    return build_lender_rules(lender_rows, rule_rows)
