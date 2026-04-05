import json
import os
from pathlib import Path

import typer

app = typer.Typer()
rules_file = Path("./rules.json")


class Rules:
    def __init__(self):
        self.rules = []

    @app.command(name="add")
    def add_rule(
        ext: str = typer.Option(..., help="ext"),
        dest: str = typer.Option(..., help="ext"),
    ):
        new_rule = {"ext": ext, "dest": dest}
        with open(rules_file, "r") as f:
            data = json.load(f)

        data["rules"].append(new_rule)

        with open(rules_file, "w") as f:
            json.dump(data, f, indent=4)

        with open(rules_file, "r") as f:
            data = json.load(f)
            for rules in data["rules"]:
                print(rules)

        print("rule added successfully")

    @app.command(name="delete")
    def delete_rule(
        ext: str = typer.Option(..., help="ext"),
    ):
        with open(rules_file, "r") as f:
            data = json.load(f)
        for i, rule in enumerate(data["rules"]):
            if rule["ext"] == ext:
                print(f"Found: {rule}")
                del data["rules"][i]
                break

        with open(rules_file, "w") as f:
            json.dump(data, f, indent=4)

        with open(rules_file, "r") as f:
            data = json.load(f)
            for rules in data["rules"]:
                print(rules)
        print("rule deleted successfully")

    def load_rules(self):
        try:
            with open("rules.json", "r") as f:
                data = json.load(f)
                rules = data["rules"]
                self.rules = rules
                return rules
        except FileNotFoundError:
            print("rules.json not found")
            return []
        except json.JSONDecodeError:
            print("Invalid JSON in rules.json")
            return []

    def test_rules(self, file):
        print("test rules: ", file)

    def find_destination(self, file):
        filename = Path(file).name
        rules = self.rules
        for rule in rules:
            if filename.endswith(rule.get("ext")):
                return rule.get("dest")

    def filesize(self, file):
        filesize = os.path.getsize(file)
        if filesize >= 5000000000:
            return False
        return True


if __name__ == "__main__":
    app()
