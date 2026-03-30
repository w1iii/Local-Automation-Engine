import json
import os
from pathlib import Path


class Rules:
    def __init__(self):
        pass
        self.rules = []

    def load_rules(self):
        try:
            with open("rules.json", "r") as f:
                # rules = f["rules"]
                data = json.load(f)
                rules = data["rules"]
                # for ext in rules:
                #     print(f"{ext.get('ext')} -> {ext.get('dest')}")
                self.rules = rules
                return rules
        except TypeError:
            print("'_io.TextIOWrapper' object is not subscriptable")

    def test_rules(self, file):
        print("test rules: ", file)

    def find_destination(self, file):
        filename = Path(file).name
        rules = self.load_rules()
        for rule in rules:
            if filename.endswith(rule.get("ext")):
                return rule.get("dest")

    def filesize(self, file):
        filesize = os.path.getsize(file)
        if filesize >= 5000000000:
            return False
        return True
