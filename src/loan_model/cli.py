"""Run the model on one applicant profile stored as JSON."""
import argparse
import json

from .engine import decide, format_decision
from .models import Applicant
from .rules import load_all


def main():
    parser = argparse.ArgumentParser(description="Personal loan eligibility check")
    parser.add_argument("profile", help="path to a JSON applicant profile")
    args = parser.parse_args()
    with open(args.profile, encoding="utf-8") as f:
        applicant = Applicant(**json.load(f))
    print(format_decision(applicant, decide(applicant, load_all())))


if __name__ == "__main__":
    main()
