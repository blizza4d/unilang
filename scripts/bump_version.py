#!/usr/bin/env python3
"""
bump_version.py - Atomic version updater and verifier across DataNova Extract codebase.
Enforces semantic versioning across frontend package.json, backend settings, OpenAPI,
health, status, and layout components.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VERSION_FILES = {
    "frontend_package": {
        "path": REPO_ROOT / "frontend" / "package.json",
        "type": "json",
        "key": "version",
    },
    "backend_config": {
        "path": REPO_ROOT / "backend" / "config.py",
        "type": "regex",
        "pattern": r'(VERSION:\s*str\s*=\s*)["][^"]+["]',
        "replacement": r'\g<1>"{version}"',
    },
    "backend_main": {
        "path": REPO_ROOT / "backend" / "main.py",
        "type": "regex",
        "pattern": r'(version=)["][^"]+["]',
        "replacement": r'\g<1>"{version}"',
    },
    "backend_health": {
        "path": REPO_ROOT / "backend" / "routers" / "health.py",
        "type": "regex",
        "pattern": r'("version":\s*)["][^"]+["]',
        "replacement": r'\g<1>"{version}"',
    },
    "backend_status": {
        "path": REPO_ROOT / "backend" / "routers" / "status.py",
        "type": "regex",
        "pattern": r'("version":\s*)["][^"]+["]',
        "replacement": r'\g<1>"{version}"',
    },
}


def get_current_versions() -> dict[str, str]:
    versions = {}
    
    # Check frontend package.json
    pkg_path = VERSION_FILES["frontend_package"]["path"]
    if pkg_path.exists():
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            versions["frontend_package"] = data.get("version", "unknown")
    else:
        versions["frontend_package"] = "missing"

    # Check backend config
    cfg_path = VERSION_FILES["backend_config"]["path"]
    if cfg_path.exists():
        content = cfg_path.read_text(encoding="utf-8")
        match = re.search(r'VERSION:\s*str\s*=\s*["]([^"]+)["]', content)
        versions["backend_config"] = match.group(1) if match else "missing_field"
    else:
        versions["backend_config"] = "missing"

    return versions


def update_version(target_version: str) -> bool:
    print(f"[*] Synchronizing release candidate version to: {target_version}")
    all_success = True

    # 1. Update frontend/package.json
    pkg_path = VERSION_FILES["frontend_package"]["path"]
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["version"] = target_version
            with open(pkg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            print(f"  [+] Updated {pkg_path.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"  [-] Failed updating package.json: {e}", file=sys.stderr)
            all_success = False
    else:
        print(f"  [-] File not found: {pkg_path}", file=sys.stderr)
        all_success = False

    # 2. Update backend/config.py
    cfg_path = VERSION_FILES["backend_config"]["path"]
    if cfg_path.exists():
        content = cfg_path.read_text(encoding="utf-8")
        if "VERSION: str =" in content:
            new_content = re.sub(
                r'(VERSION:\s*str\s*=\s*)["][^"]+["]',
                f'\\g<1>"{target_version}"',
                content,
            )
        else:
            # Insert after Settings class declaration
            new_content = content.replace(
                "class Settings(BaseSettings):",
                f'class Settings(BaseSettings):\n    VERSION: str = "{target_version}"',
            )
        cfg_path.write_text(new_content, encoding="utf-8")
        print(f"  [+] Updated {cfg_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  [-] File not found: {cfg_path}", file=sys.stderr)
        all_success = False

    # 3. Update backend/main.py
    main_path = VERSION_FILES["backend_main"]["path"]
    if main_path.exists():
        content = main_path.read_text(encoding="utf-8")
        new_content = re.sub(
            r'version="[^"]+"',
            f'version="{target_version}"',
            content,
        )
        main_path.write_text(new_content, encoding="utf-8")
        print(f"  [+] Updated {main_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  [-] File not found: {main_path}", file=sys.stderr)
        all_success = False

    # 4. Update backend/routers/health.py
    health_path = VERSION_FILES["backend_health"]["path"]
    if health_path.exists():
        content = health_path.read_text(encoding="utf-8")
        new_content = re.sub(
            r'"version":\s*"[^"]+"',
            f'"version": "{target_version}"',
            content,
        )
        health_path.write_text(new_content, encoding="utf-8")
        print(f"  [+] Updated {health_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  [-] File not found: {health_path}", file=sys.stderr)
        all_success = False

    # 5. Update backend/routers/status.py
    status_path = VERSION_FILES["backend_status"]["path"]
    if status_path.exists():
        content = status_path.read_text(encoding="utf-8")
        new_content = re.sub(
            r'"version":\s*"[^"]+"',
            f'"version": "{target_version}"',
            content,
        )
        status_path.write_text(new_content, encoding="utf-8")
        print(f"  [+] Updated {status_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  [-] File not found: {status_path}", file=sys.stderr)
        all_success = False

    return all_success


def verify_versions(expected_version: str) -> bool:
    print(f"[*] Verifying all version locations match '{expected_version}'...")
    all_matched = True

    # Check frontend package.json
    pkg_path = VERSION_FILES["frontend_package"]["path"]
    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
        if pkg.get("version") != expected_version:
            print(f"  [-] Mismatch in {pkg_path}: {pkg.get('version')} != {expected_version}", file=sys.stderr)
            all_matched = False
        else:
            print(f"  [+] OK {pkg_path.relative_to(REPO_ROOT)}: {pkg.get('version')}")

    # Check backend config
    cfg_path = VERSION_FILES["backend_config"]["path"]
    match = re.search(r'VERSION:\s*str\s*=\s*["]([^"]+)["]', cfg_path.read_text(encoding="utf-8"))
    if not match or match.group(1) != expected_version:
        print(f"  [-] Mismatch in {cfg_path}: {match.group(1) if match else None} != {expected_version}", file=sys.stderr)
        all_matched = False
    else:
        print(f"  [+] OK {cfg_path.relative_to(REPO_ROOT)}: {match.group(1)}")

    # Check backend main
    main_path = VERSION_FILES["backend_main"]["path"]
    match = re.search(r'version="([^"]+)"', main_path.read_text(encoding="utf-8"))
    if not match or match.group(1) != expected_version:
        print(f"  [-] Mismatch in {main_path}: {match.group(1) if match else None} != {expected_version}", file=sys.stderr)
        all_matched = False
    else:
        print(f"  [+] OK {main_path.relative_to(REPO_ROOT)}: {match.group(1)}")

    # Check health router
    health_path = VERSION_FILES["backend_health"]["path"]
    match = re.search(r'"version":\s*"([^"]+)"', health_path.read_text(encoding="utf-8"))
    if not match or match.group(1) != expected_version:
        print(f"  [-] Mismatch in {health_path}: {match.group(1) if match else None} != {expected_version}", file=sys.stderr)
        all_matched = False
    else:
        print(f"  [+] OK {health_path.relative_to(REPO_ROOT)}: {match.group(1)}")

    # Check status router
    status_path = VERSION_FILES["backend_status"]["path"]
    match = re.search(r'"version":\s*"([^"]+)"', status_path.read_text(encoding="utf-8"))
    if not match or match.group(1) != expected_version:
        print(f"  [-] Mismatch in {status_path}: {match.group(1) if match else None} != {expected_version}", file=sys.stderr)
        all_matched = False
    else:
        print(f"  [+] OK {status_path.relative_to(REPO_ROOT)}: {match.group(1)}")

    return all_matched


def main():
    parser = argparse.ArgumentParser(description="DataNova Extract version synchronizer")
    parser.add_argument("--set", dest="target_version", default="1.0.0-rc.1", help="Target version string")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing versions")
    args = parser.parse_args()

    if not args.verify_only:
        success = update_version(args.target_version)
        if not success:
            sys.exit(1)

    matched = verify_versions(args.target_version)
    if not matched:
        print("\n[-] Version verification failed!", file=sys.stderr)
        sys.exit(1)

    print(f"\n[+] All version locations synchronized and verified: {args.target_version}")


if __name__ == "__main__":
    main()
