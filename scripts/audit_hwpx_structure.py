from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print non-content HWPX structure counts for private sample files."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    for path in args.paths:
        print(_audit(path))
    return 0


def _audit(path: Path) -> str:
    if not path.exists():
        return f"{path}: missing"

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        sections = [name for name in names if re.match(r"Contents/section\d+\.xml$", name)]
        header = _read_text(archive, "Contents/header.xml")
        section_text = "".join(_read_text(archive, section) for section in sections)
        preview = _read_text(archive, "Preview/PrvText.txt")
        mimetype = _read_text(archive, "mimetype").strip()

    parts = [
        f"{path.name}:",
        f"mimetype={mimetype or 'missing'}",
        f"entries={len(names)}",
        f"sections={len(sections)}",
        f"charPr={header.count('<hh:charPr')}",
        f"paraPr={header.count('<hh:paraPr')}",
        f"borderFill={header.count('<hh:borderFill')}",
        f"styles={header.count('<hh:style')}",
        f"paragraphs={section_text.count('<hp:p')}",
        f"tables={section_text.count('<hp:tbl')}",
        f"cells={section_text.count('<hp:tc')}",
        f"pictures={section_text.count('<hp:pic')}",
        f"previewChars={len(preview)}",
    ]
    return " ".join(parts)


def _read_text(archive: zipfile.ZipFile, name: str) -> str:
    if name not in archive.namelist():
        return ""
    return archive.read(name).decode("utf-8", errors="replace")


if __name__ == "__main__":
    raise SystemExit(main())
