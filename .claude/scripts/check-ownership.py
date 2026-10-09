#!/usr/bin/env python3
"""Verifica que los archivos modificados pertenezcan al rol que los escribe.

La propiedad se declara en .claude/ownership.json. Regla de resolucion: gana el
patron mas especifico (el prefijo mas largo que coincide). Las entradas que
terminan en "/" son prefijos de directorio; el resto son rutas exactas.

Uso:
  check-ownership.py --role documentador              # revisa el diff vs la base
  check-ownership.py --role tester --staged           # revisa solo el indice
  check-ownership.py --role devops infra/main.tf      # revisa rutas concretas
  check-ownership.py --who en/index.md docs/qa/a.md   # imprime el dueno de cada ruta
  check-ownership.py --audit                          # busca patrones duplicados
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / ".claude" / "ownership.json"


def load_rules() -> list[tuple[str, str]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    rules: list[tuple[str, str]] = []
    for role, spec in data["roles"].items():
        for pattern in spec.get("owns", []):
            rules.append((pattern, role))
    return rules


def owner_of(path: str, rules: list[tuple[str, str]]) -> tuple[str | None, str | None]:
    best: tuple[str, str] | None = None
    for pattern, role in rules:
        matches = path.startswith(pattern) if pattern.endswith("/") else path == pattern
        if matches and (best is None or len(pattern) > len(best[0])):
            best = (pattern, role)
    return (best[1], best[0]) if best else (None, None)


def changed_paths(staged: bool, base: str) -> list[str]:
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRD"]
    else:
        merge_base = subprocess.run(
            ["git", "merge-base", "HEAD", base],
            cwd=REPO, capture_output=True, text=True,
        )
        ref = merge_base.stdout.strip() or base
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMRD", ref]
    out = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def audit(rules: list[tuple[str, str]]) -> int:
    seen: dict[str, list[str]] = {}
    for pattern, role in rules:
        seen.setdefault(pattern, []).append(role)
    clashes = {p: r for p, r in seen.items() if len(r) > 1}
    for pattern, roles in sorted(clashes.items()):
        print(f"SOLAPAMIENTO: '{pattern}' reclamado por {', '.join(sorted(roles))}")
    if clashes:
        return 1
    print(f"OK: {len(rules)} patrones, ninguno duplicado.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--role", help="rol que firma los cambios")
    parser.add_argument("--who", action="store_true", help="solo imprime el dueno de cada ruta")
    parser.add_argument("--audit", action="store_true", help="busca patrones reclamados por dos roles")
    parser.add_argument("--staged", action="store_true", help="revisa el indice en lugar del diff completo")
    parser.add_argument("--base", default="origin/master", help="rama base del diff (por defecto origin/master)")
    parser.add_argument("paths", nargs="*", help="rutas a revisar; si se omiten, se toman del diff")
    args = parser.parse_args()

    rules = load_rules()

    if args.audit:
        return audit(rules)

    paths = args.paths or changed_paths(args.staged, args.base)

    if args.who:
        for path in paths:
            role, pattern = owner_of(path, rules)
            print(f"{path}\t{role or '(sin dueno)'}\t{pattern or '-'}")
        return 0

    if not args.role:
        parser.error("se requiere --role (o usa --who / --audit)")

    if args.role not in {role for _, role in rules}:
        print(f"Rol desconocido: {args.role}", file=sys.stderr)
        return 2

    if not paths:
        print("Sin cambios que revisar.")
        return 0

    violations: list[tuple[str, str | None]] = []
    for path in paths:
        role, _ = owner_of(path, rules)
        if role != args.role:
            violations.append((path, role))

    if violations:
        print(f"El rol '{args.role}' modifico {len(violations)} ruta(s) que no le pertenecen:\n")
        for path, role in violations:
            print(f"  {path}  ->  dueno: {role or '(sin dueno declarado)'}")
        print("\nPide el cambio al rol dueno, o actualiza .claude/ownership.json (coordinador).")
        return 1

    print(f"OK: las {len(paths)} ruta(s) modificadas pertenecen a '{args.role}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
