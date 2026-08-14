from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CordisLoader(yaml.SafeLoader):
    pass


CordisLoader.add_constructor(
    "tag:yaml.org,2002:js",
    lambda loader, node: loader.construct_scalar(node),
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_patch() -> list[dict]:
    with (ROOT / "cordis.patch.yml").open(encoding="utf-8") as handle:
        return yaml.load(handle, Loader=CordisLoader)


class DeepSeekPluginRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_json(ROOT / "package.json")
        self.patch = load_patch()
        self.rows = self.patch[0]["insert"]
        self.rows_by_id = {row["id"]: row for row in self.rows}

    def test_manifest_declares_a_patch_bundle(self) -> None:
        self.assertEqual(
            self.manifest["dsh"],
            {"bundle": {"patch": "./cordis.patch.yml"}},
        )
        self.assertIn("cordis.patch.yml", self.manifest["files"])
        self.assertIn("index.js", self.manifest["files"])
        self.assertIn("skills", self.manifest["files"])
        self.assertIn("dsh-plugin", self.manifest["keywords"])
        self.assertEqual(self.manifest["main"], "index.js")
        self.assertEqual(self.manifest["engines"]["node"], ">=20.19.0")
        self.assertEqual(
            self.manifest["dependencies"],
            {
                "@deepseek-ai/dsh-mcp-client": "^0.1.0-rc.6",
                "@deepseek-ai/dsh-skill-filesystem": "^0.1.0-rc.6",
            },
        )

    def test_manifest_repository_matches_this_repository(self) -> None:
        self.assertEqual(
            self.manifest["repository"]["url"],
            "git+https://github.com/superfly/sprites-deepseek-plugin.git",
        )

    def test_patch_contains_unique_rows(self) -> None:
        self.assertEqual(len(self.rows_by_id), len(self.rows))
        self.assertEqual(
            set(self.rows_by_id),
            {"sprites-mcp", "sprites-skill-filesystem"},
        )

    def test_mcp_row_uses_harness_mcp_client_and_oauth_bridge(self) -> None:
        row = self.rows_by_id["sprites-mcp"]
        config = row["config"]
        self.assertEqual(row["name"], "@deepseek-ai/dsh-mcp-client")
        self.assertEqual(config["transport"], "stdio")
        self.assertEqual(config["serverName"], "sprites")
        self.assertEqual(config["command"], "npx")
        self.assertEqual(config["args"][:3], ["-y", "mcp-remote@0.1.38", "https://sprites.dev/mcp"])
        self.assertIn("http-only", config["args"])
        self.assertGreaterEqual(config["toolCallTimeoutMs"], 60_000)

    def test_mcp_row_sends_only_static_client_attribution(self) -> None:
        args = self.rows_by_id["sprites-mcp"]["config"]["args"]
        headers = [args[index + 1] for index, value in enumerate(args) if value == "--header"]
        self.assertEqual(
            headers,
            [
                "Fly-Client-Interactive:false",
                "Fly-Client-Agent:deepseek-harness",
            ],
        )
        self.assertFalse(any(header.lower().startswith("authorization:") for header in headers))

        patch_text = (ROOT / "cordis.patch.yml").read_text(encoding="utf-8")
        self.assertIn("headers in its OAuth cache key", patch_text)
        self.assertIn("signs existing users out", patch_text)

    def test_skill_row_loads_the_package_entry(self) -> None:
        row = self.rows_by_id["sprites-skill-filesystem"]
        self.assertEqual(row, {"id": "sprites-skill-filesystem", "name": "dsh-sprites-plugin"})

    def test_entry_resolves_skills_relative_to_relocated_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir) / "elsewhere" / "dsh-sprites-plugin"
            package_root.mkdir(parents=True)
            shutil.copy2(ROOT / "index.js", package_root / "index.js")
            shutil.copytree(ROOT / "skills", package_root / "skills")

            mock_dependency = (
                package_root / "node_modules" / "@deepseek-ai" / "dsh-skill-filesystem"
            )
            mock_dependency.mkdir(parents=True)
            (mock_dependency / "package.json").write_text(
                json.dumps(
                    {
                        "name": "@deepseek-ai/dsh-skill-filesystem",
                        "type": "module",
                        "main": "index.js",
                    }
                ),
                encoding="utf-8",
            )
            (mock_dependency / "index.js").write_text(
                "export const name = 'skill-filesystem'\nexport function apply() {}\n",
                encoding="utf-8",
            )

            verification = package_root / "verify.mjs"
            verification.write_text(
                """
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import * as entry from './index.js'

const sentinel = Symbol('fiber')
let mounted
const result = entry.apply({
  plugin(plugin, config) {
    mounted = { plugin, config }
    return sentinel
  },
})

if (entry.name !== 'sprites-skills') throw new Error('wrong plugin name')
if (result !== sentinel) throw new Error('child fiber was not returned')
if (mounted.plugin.name !== 'skill-filesystem') throw new Error('wrong child plugin')
if (mounted.config.providerName !== 'sprites') throw new Error('wrong provider name')
if (mounted.config.includeDefaultRoots !== false) throw new Error('default roots enabled')
if (mounted.config.watch !== false) throw new Error('watch enabled')

const [skillRoot] = mounted.config.customSkillDirs
if (!existsSync(join(skillRoot, 'sprites', 'SKILL.md'))) {
  throw new Error(`packaged skill not found at ${skillRoot}`)
}
""".lstrip(),
                encoding="utf-8",
            )

            subprocess.run(["node", str(verification)], check=True, cwd=package_root)

    def test_packaged_skill_and_references_exist(self) -> None:
        skill_root = ROOT / "skills/sprites"
        self.assertTrue((skill_root / "SKILL.md").is_file())
        expected_references = {
            "auth-and-setup.md",
            "compute.md",
            "files.md",
            "safety.md",
            "services.md",
        }
        actual_references = {path.name for path in (skill_root / "references").glob("*.md")}
        self.assertEqual(actual_references, expected_references)

        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("requires a `sprite` argument", skill_text)
        self.assertIn("reuse the exact sprite name returned by the server", skill_text)

    def test_local_environment_is_ignored(self) -> None:
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".venv/", ignored)
        self.assertIn(".claude/", ignored)

    def test_open_source_community_files_exist(self) -> None:
        expected = {
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "SECURITY.md",
            "SUPPORT.md",
            ".github/CODEOWNERS",
            ".github/dependabot.yml",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        }
        for relative in expected:
            self.assertTrue((ROOT / relative).is_file(), relative)

        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 Fly.io, Inc.", license_text)


if __name__ == "__main__":
    unittest.main()
