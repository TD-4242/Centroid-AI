#!/usr/bin/env python3
"""Read and write ~/.centroid-ai/config.json, shared by every Centroid-AI plugin."""
import copy
import json
import os
import sys
from pathlib import Path

DEFAULTS = {"manuals": {"autoDownload": "ask", "dir": None}, "mpucomp": {"path": None, "trusted": []}}
AUTO_DOWNLOAD = ("ask", "always", "never")


def home():
    return Path(os.environ.get("CENTROID_AI_HOME") or Path.home() / ".centroid-ai")


def config_path():
    return home() / "config.json"


def load():
    cfg = copy.deepcopy(DEFAULTS)
    try:
        data = json.loads(config_path().read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return cfg
    except json.JSONDecodeError as e:
        raise ValueError(f"{config_path()} is not valid JSON ({e.msg}, line {e.lineno}); "
                         "fix or delete it") from None
    if not isinstance(data, dict):
        raise ValueError(f"{config_path()} must be a JSON object; fix or delete it")
    for section, values in data.items():
        if isinstance(cfg.get(section), dict):
            if not isinstance(values, dict):
                raise ValueError(f"{config_path()}: section {section!r} must be a JSON object; "
                                 "fix or delete it")
            cfg[section].update(values)
        else:
            cfg[section] = values
    if not isinstance(cfg["mpucomp"].get("trusted"), list):
        raise ValueError(f"{config_path()}: mpucomp.trusted must be a JSON list; fix or delete it")
    return cfg


def set_value(key, value):
    if key == "manuals.autoDownload" and value not in AUTO_DOWNLOAD:
        raise ValueError(f"manuals.autoDownload must be one of {', '.join(AUTO_DOWNLOAD)}")
    if key == "mpucomp.trusted":
        if value is None:
            value = []
        elif not isinstance(value, list):
            raise ValueError("use `centroid_config.py trust <path>` to add a compiler; "
                             "`set mpucomp.trusted null` clears the list")
    section, _, name = key.partition(".")
    if not name:
        raise ValueError(f"key must look like section.name, got {key!r}")
    cfg = load()
    cfg.setdefault(section, {})[name] = value
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _norm(path):
    return os.path.normcase(str(Path(path).expanduser().resolve()))


def trust_compiler(path):
    if not Path(path).expanduser().is_file():
        raise ValueError(f"{path} is not an existing file")
    trusted = load()["mpucomp"]["trusted"]
    if not is_trusted(path):
        set_value("mpucomp.trusted", [*trusted, str(Path(path).expanduser().resolve())])


def is_trusted(path):
    return _norm(path) in {_norm(t) for t in load()["mpucomp"]["trusted"]}


def manuals_dir():
    env = os.environ.get("CENTROID_AI_MANUALS")
    if env:
        return Path(env).expanduser()
    configured = load()["manuals"].get("dir")
    return Path(configured).expanduser() if configured else home() / "manuals"


def main(argv):
    try:
        if argv[:1] == ["show"]:
            print(json.dumps(load(), indent=2))
        elif len(argv) == 2 and argv[0] == "get":
            section, _, name = argv[1].partition(".")
            print(json.dumps(load().get(section, {}).get(name)))
        elif len(argv) == 3 and argv[0] == "set":
            set_value(argv[1], None if argv[2] == "null" else argv[2])
        elif len(argv) == 2 and argv[0] == "trust":
            trust_compiler(argv[1])
        else:
            print("usage: centroid_config.py show | get <key> | set <key> <value> | trust <path>",
                  file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
