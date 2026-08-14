#!/usr/bin/env python3
"""Validate the DeepSeek Harness bundle's structured and text files."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKIPPED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
TEXT_SUFFIXES = {".json", ".md", ".mjs", ".py", ".toml", ".txt", ".yaml", ".yml"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class DuplicateKeyError(ValueError):
    """Raised when a JSON or YAML object contains a duplicate key."""


class CordisLoader(yaml.SafeLoader):
    """Safe YAML loader that retains Cordis's scalar ``!!js`` expressions."""


def construct_cordis_js(loader: CordisLoader, node: yaml.ScalarNode) -> str:
    return loader.construct_scalar(node)


CordisLoader.add_constructor("tag:yaml.org,2002:js", construct_cordis_js)


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def construct_unique_mapping(
    loader: CordisLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


CordisLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_cordis_yaml(text: str) -> Any:
    return yaml.load(text, Loader=CordisLoader)


def repository_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not SKIPPED_DIRECTORIES.intersection(path.relative_to(ROOT).parts)
    )


def validate_text(path: Path, errors: list[str]) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None

    relative = path.relative_to(ROOT)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{relative}: not valid UTF-8 ({exc})")
        return None

    if text and not text.endswith("\n"):
        errors.append(f"{relative}: missing final newline")
    for number, line in enumerate(text.splitlines(), start=1):
        if line != line.rstrip():
            errors.append(f"{relative}:{number}: trailing whitespace")
    return text


def validate_json(path: Path, text: str, errors: list[str]) -> None:
    try:
        json.loads(text, object_pairs_hook=reject_duplicate_json_keys)
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")


def validate_yaml(path: Path, text: str, errors: list[str]) -> None:
    try:
        load_cordis_yaml(text)
    except (yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML ({exc})")


def markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    elif " " in target:
        target = target.split(" ", maxsplit=1)[0]
    return urllib.parse.unquote(target.split("#", maxsplit=1)[0])


def validate_markdown_links(path: Path, text: str, errors: list[str]) -> None:
    for match in MARKDOWN_LINK.finditer(text):
        target = markdown_target(match.group(1))
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {target!r}")


def validate_skill(path: Path, text: str, errors: list[str]) -> None:
    relative = path.relative_to(ROOT)
    if not text.startswith("---\n"):
        errors.append(f"{relative}: missing YAML frontmatter")
        return
    try:
        frontmatter, body = text[4:].split("\n---\n", maxsplit=1)
        metadata = load_cordis_yaml(frontmatter)
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"{relative}: invalid YAML frontmatter ({exc})")
        return
    if not isinstance(metadata, dict):
        errors.append(f"{relative}: frontmatter must be a mapping")
        return
    if metadata.get("name") != path.parent.name:
        errors.append(f"{relative}: skill name must match directory name {path.parent.name!r}")
    if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
        errors.append(f"{relative}: skill description must be a non-empty string")
    if not body.strip():
        errors.append(f"{relative}: skill body must not be empty")


def main() -> int:
    errors: list[str] = []
    files = repository_files()

    required = {
        ROOT / "CHANGELOG.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "LICENSE",
        ROOT / "SECURITY.md",
        ROOT / "SUPPORT.md",
        ROOT / ".github/CODEOWNERS",
        ROOT / ".github/dependabot.yml",
        ROOT / ".github/pull_request_template.md",
        ROOT / ".github/ISSUE_TEMPLATE/bug_report.yml",
        ROOT / ".github/ISSUE_TEMPLATE/config.yml",
        ROOT / ".github/ISSUE_TEMPLATE/feature_request.yml",
    }
    for path in sorted(required):
        if not path.is_file():
            errors.append(f"missing required file {path.relative_to(ROOT)}")

    for path in files:
        text = validate_text(path, errors)
        suffix = path.suffix.lower()
        if text is not None and suffix == ".json":
            validate_json(path, text, errors)
        elif text is not None and suffix in {".yaml", ".yml"}:
            validate_yaml(path, text, errors)

        if text is not None and suffix == ".md":
            validate_markdown_links(path, text, errors)
        if text is not None and path.name == "SKILL.md":
            validate_skill(path, text, errors)

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} repository files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
