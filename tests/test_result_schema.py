import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_SCHEMA = ROOT / "schemas" / "result.structured.schema.json"
LEGACY_RESULT_SCHEMA = ROOT / "schemas" / "result.schema.json"


class ResultStructuredOutputSchemaTests(unittest.TestCase):
    def test_legacy_v1_schema_keeps_sparse_historical_results_compatible(self) -> None:
        legacy = json.loads(LEGACY_RESULT_SCHEMA.read_text(encoding="utf-8"))
        claim = legacy["properties"]["claims"]["items"]
        avenue = legacy["properties"]["iteration"]["properties"]["avenues"]["items"]
        self.assertNotIn("statement_ref", claim["required"])
        self.assertEqual(
            avenue["required"],
            ["name", "objective", "outcome", "status"],
        )

    def test_schema_uses_the_openai_structured_outputs_subset(self) -> None:
        schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("type"), "object")
        self.assertNotIn("anyOf", schema)

        unsupported = {
            "allOf",
            "not",
            "dependentRequired",
            "dependentSchemas",
            "if",
            "then",
            "else",
            "uniqueItems",
            "minLength",
            "maxLength",
        }

        def walk(node: Any, path: str) -> None:
            if isinstance(node, list):
                for index, child in enumerate(node):
                    walk(child, f"{path}/{index}")
                return
            if not isinstance(node, dict):
                return

            forbidden = unsupported.intersection(node)
            self.assertFalse(forbidden, f"{path} uses unsupported keywords: {forbidden}")
            if "const" in node or "enum" in node:
                self.assertIn("type", node, f"{path} has const/enum without an explicit type")
            if node.get("type") == "object":
                properties = node.get("properties", {})
                self.assertIs(node.get("additionalProperties"), False, path)
                self.assertEqual(
                    set(node.get("required", [])),
                    set(properties),
                    f"{path} must require every declared property",
                )
            for key, child in node.items():
                walk(child, f"{path}/{key}")

        walk(schema, "$")


if __name__ == "__main__":
    unittest.main()
