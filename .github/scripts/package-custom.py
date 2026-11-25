"""Build the fork ZIP from tracked runtime files using the upstream packager."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
PACKAGER = ROOT / "others/program/release/generate_rime_all_schema_zip.py"
ARCHIVE = "rime-frost-schemas.zip"
CUSTOM_FILES = {"default.custom.yaml", "custom_phrase.txt"}
ROOT_FILES = CUSTOM_FILES | {"LICENSE", "essay.txt", "zh-moqi.gram"}
RUNTIME_SUFFIXES = {
    "cn_dicts": (".dict.yaml",),
    "cn_dicts_cell": (".dict.yaml",),
    "cn_dicts_common": (".dict.yaml",),
    "cn_dicts_wb": (".dict.yaml",),
    "en_dicts": (".dict.yaml", ".txt"),
    "lua": (".lua",),
    "opencc": (".json", ".ocd2", ".txt"),
}


def runtime_file(name):
    if any(part.startswith(".") or ".userdb" in part for part in name.split("/")):
        return False
    directory, separator, _ = name.partition("/")
    if separator:
        return name.endswith(RUNTIME_SUFFIXES.get(directory, ()))
    return name in ROOT_FILES or (
        name.endswith(".yaml")
        and not name.endswith(".custom.yaml")
        and name not in {"installation.yaml", "user.yaml"}
    )


def main(output_dir):
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    files = sorted({name for name in os.fsdecode(tracked).split("\0") if runtime_file(name)})
    if not CUSTOM_FILES.issubset(files):
        raise RuntimeError("The default patch and phrase template must be tracked")

    with TemporaryDirectory() as directory:
        stage = Path(directory)
        subprocess.run(
            ["git", "checkout-index", f"--prefix={stage}/", "--stdin", "-z"],
            cwd=ROOT, input=os.fsencode("\0".join(files) + "\0"), check=True,
        )
        for name in files:
            path = stage / name
            if path.is_symlink() or not path.is_file():
                raise RuntimeError(f"Expected a regular runtime file: {name}")
            # Stable ZIP timestamps for repeated builds of the same tree.
            os.utime(path, (946684800, 946684800))

        subprocess.run([sys.executable, str(PACKAGER)], cwd=stage, check=True)
        archive = stage / ARCHIVE
        with ZipFile(archive, "a", compression=ZIP_DEFLATED) as bundle:
            # Upstream excludes any root filename containing "custom".
            for name in sorted(CUSTOM_FILES):
                bundle.write(stage / name, name)
            if sorted(bundle.namelist()) != files or bundle.testzip() is not None:
                raise RuntimeError("ZIP inventory or integrity check failed")
        shutil.copyfile(archive, output_dir / ARCHIVE)
        print(f"Verified {len(files)} runtime files in {ARCHIVE}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
