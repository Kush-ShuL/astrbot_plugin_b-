"""保护安装依赖清单和修复版本，避免核心依赖冲突再次进入安装包。"""
from pathlib import Path
import re
import unittest

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version


ROOT = Path(__file__).resolve().parents[1]
CORE_PACKAGES = {
    "openai", "pydantic", "httpx", "pillow", "qrcode", "python-docx", "reportlab",
}


def read_requirements(text):
    requirements = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            requirements.append(Requirement(line))
    return requirements


class InstallationManifestTests(unittest.TestCase):
    def test_direct_requirements_do_not_redeclare_core_packages(self):
        requirements = read_requirements((ROOT / "requirements.txt").read_text(encoding="utf-8"))
        self.assertTrue(requirements)
        for requirement in requirements:
            with self.subTest(requirement=str(requirement)):
                self.assertNotIn(canonicalize_name(requirement.name), CORE_PACKAGES)
                self.assertIsNone(requirement.url)
                self.assertFalse(any(item.operator in {"==", "==="} for item in requirement.specifier))

    def test_guard_detects_historical_openai_pin_and_normalizes_names(self):
        requirements = read_requirements(
            "# openai is provided by AstrBot\nOpenAI==2.33.0\nHTTPX[socks]>=0.28.1\npython_docx>=1.2.0\n"
        )
        self.assertEqual(
            [canonicalize_name(item.name) for item in requirements],
            ["openai", "httpx", "python-docx"],
        )
        self.assertTrue(all(canonicalize_name(item.name) in CORE_PACKAGES for item in requirements))

    def test_release_version_is_new_and_consistent(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertGreater(Version(version), Version("3.1.5"))
        metadata = (ROOT / "metadata.yaml").read_text(encoding="utf-8")
        self.assertRegex(metadata, rf"(?m)^version: {re.escape(version)}\s*$")
        self.assertIn('astrbot_version: ">=4.29.1,<5"', metadata)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"> 版本: **{version}**", readme)
        self.assertIn(f"> Version: **{version}**", readme)
        self.assertIn(f"当前 {version}", readme)
        self.assertIn(f"current {version}", readme)
        self.assertIn(
            f"v{version} 依赖清单",
            (ROOT / "requirements.txt").read_text(encoding="utf-8"),
        )
        self.assertIn(f"版本: v{version} ", (ROOT / "cli/app.py").read_text(encoding="utf-8"))
        self.assertIn(f"## {version} —", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
