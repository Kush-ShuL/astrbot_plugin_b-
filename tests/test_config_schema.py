"""配置文件回归测试：无需安装 AstrBot 或业务依赖。"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ConfigSchemaTests(unittest.TestCase):
    def test_config_schema_is_a_complete_json_object(self):
        schema = json.loads((ROOT / "_conf_schema.json").read_text(encoding="utf-8"))
        self.assertIsInstance(schema, dict)
        self.assertTrue(schema)


if __name__ == "__main__":
    unittest.main()
