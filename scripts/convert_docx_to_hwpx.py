from __future__ import annotations

import argparse
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HP_NS = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"

HWPX_NAMESPACES = {
    "ha": "http://www.hancom.co.kr/hwpml/2011/app",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hp10": "http://www.hancom.co.kr/hwpml/2016/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hhs": "http://www.hancom.co.kr/hwpml/2011/history",
    "hm": "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf": "http://www.hancom.co.kr/schema/2011/hpf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf/",
    "ooxmlchart": "http://www.hancom.co.kr/hwpml/2016/ooxmlchart",
    "hwpunitchar": "http://www.hancom.co.kr/hwpml/2016/HwpUnitChar",
    "epub": "http://www.idpf.org/2007/ops",
    "config": "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
}

for prefix, uri in HWPX_NAMESPACES.items():
    ET.register_namespace(prefix, uri)


@dataclass(frozen=True)
class Block:
    kind: str
    text: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experimental DOCX text extraction to HWPX package spike."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument(
        "--allow-experimental",
        action="store_true",
        help="Required. This converter is not production-ready and may create unusable HWPX.",
    )
    parser.add_argument(
        "--carrier-hwpx",
        type=Path,
        help="Existing renderable HWPX package to reuse while replacing paragraph text.",
    )
    args = parser.parse_args()
    if not args.allow_experimental:
        raise SystemExit(
            "DOCX->HWPX conversion is experimental and not production-ready. "
            "Use --allow-experimental only for local spike testing."
        )

    source = args.source
    output = args.output or Path("outputs") / f"{source.stem}.hwpx"
    blocks = read_docx_blocks(source)
    if args.carrier_hwpx:
        write_hwpx_from_carrier(args.carrier_hwpx, output, blocks)
    else:
        write_hwpx(source, output, blocks)

    paragraph_count = sum(1 for block in blocks if block.kind == "paragraph")
    table_row_count = sum(1 for block in blocks if block.kind == "table_row")
    print(f"source={source}")
    print(f"output={output}")
    print(f"paragraphs={paragraph_count}")
    print(f"table_rows={table_row_count}")
    return 0


def read_docx_blocks(path: Path) -> list[Block]:
    with zipfile.ZipFile(path) as archive:
        document_xml = archive.read("word/document.xml")
    root = ET.fromstring(document_xml)
    body = root.find(f"{W_NS}body")
    if body is None:
        raise ValueError("DOCX body not found")

    blocks: list[Block] = []
    for child in body:
        tag = _strip_ns(child.tag)
        if tag == "p":
            text = _paragraph_text(child)
            if text:
                blocks.append(Block("paragraph", text))
        elif tag == "tbl":
            rows = _table_rows(child)
            for row in rows:
                if any(cell.strip() for cell in row):
                    blocks.append(Block("table_row", " | ".join(cell.strip() for cell in row)))
    return blocks


def write_hwpx(source: Path, output: Path, blocks: list[Block]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    title = source.stem
    plain_text = "\n".join(block.text for block in blocks)
    entries = {
        "mimetype": "application/hwp+zip",
        "version.xml": _version_xml(),
        "Contents/content.hpf": _content_hpf(title),
        "Contents/header.xml": _header_xml(),
        "Contents/section0.xml": _section_xml(title, blocks),
        "Preview/PrvText.txt": plain_text[:4000],
        "settings.xml": _settings_xml(),
        "META-INF/container.xml": _container_xml(),
        "META-INF/container.rdf": _container_rdf(title),
        "META-INF/manifest.xml": _manifest_xml(),
    }

    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("mimetype", entries["mimetype"], compress_type=zipfile.ZIP_STORED)
        for name, content in entries.items():
            if name == "mimetype":
                continue
            archive.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)


def write_hwpx_from_carrier(carrier: Path, output: Path, blocks: list[Block]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text_items = _expand_blocks(blocks)
    plain_text = "\n".join(text_items)

    with zipfile.ZipFile(carrier) as source_archive:
        section_xml = source_archive.read("Contents/section0.xml")
        rendered_section = _replace_hwp_paragraph_text(section_xml, text_items)

        with zipfile.ZipFile(output, "w") as output_archive:
            for info in source_archive.infolist():
                content = source_archive.read(info.filename)
                if info.filename == "Contents/section0.xml":
                    content = rendered_section
                elif info.filename == "Preview/PrvText.txt":
                    content = plain_text[:4000].encode("utf-8")
                output_archive.writestr(info, content)


def _replace_hwp_paragraph_text(section_xml: bytes, text_items: list[str]) -> bytes:
    root = ET.fromstring(section_xml)
    paragraphs = root.findall(f".//{HP_NS}p")
    text_paragraphs = [paragraph for paragraph in paragraphs if _direct_text_nodes(paragraph)]
    if len(text_items) > len(text_paragraphs):
        raise ValueError(
            f"Carrier HWPX has {len(text_paragraphs)} text paragraphs, but conversion needs "
            f"{len(text_items)} paragraphs"
        )

    item_idx = 0
    for paragraph in paragraphs:
        text_nodes = _direct_text_nodes(paragraph)
        if not text_nodes:
            continue
        replacement = text_items[item_idx] if item_idx < len(text_items) else " "
        item_idx += 1
        text_nodes[0].text = replacement or " "
        for extra_node in text_nodes[1:]:
            extra_node.text = ""

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _direct_text_nodes(paragraph: ET.Element) -> list[ET.Element]:
    return paragraph.findall(f"./{HP_NS}run/{HP_NS}t")


def _expand_blocks(blocks: list[Block]) -> list[str]:
    expanded: list[str] = []
    for block in blocks:
        max_chars = 54 if block.kind == "table_row" else 70
        expanded.extend(_wrap_text(block.text, max_chars=max_chars))
    return expanded


def _wrap_text(text: str, *, max_chars: int) -> list[str]:
    parts: list[str] = []
    for paragraph in text.splitlines() or [text]:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        while len(paragraph) > max_chars:
            split_at = paragraph.rfind(" ", 0, max_chars)
            if split_at < max_chars // 2:
                split_at = max_chars
            parts.append(paragraph[:split_at].strip())
            paragraph = paragraph[split_at:].strip()
        if paragraph:
            parts.append(paragraph)
    return parts


def _paragraph_text(element: ET.Element) -> str:
    chunks: list[str] = []
    for node in element.iter():
        tag = _strip_ns(node.tag)
        if tag == "t" and node.text:
            chunks.append(node.text)
        elif tag == "tab":
            chunks.append("\t")
        elif tag == "br":
            chunks.append("\n")
    return _normalize_text("".join(chunks))


def _table_rows(table: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.findall(f"{W_NS}tr"):
        row = []
        for tc in tr.findall(f"{W_NS}tc"):
            paragraphs = [_paragraph_text(p) for p in tc.findall(f"{W_NS}p")]
            row.append(" ".join(text for text in paragraphs if text))
        rows.append(row)
    return rows


def _normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _version_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<hv:version xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" '
        'app="kspeaks-form-filler" hwpx="5.1.3"/>'
    )


def _content_hpf(title: str) -> str:
    safe_title = escape(title)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<opf:package xmlns:opf="http://www.idpf.org/2007/opf/"
  xmlns:dc="http://purl.org/dc/elements/1.1/" version="1.0">
  <opf:metadata>
    <dc:title>{safe_title}</dc:title>
    <dc:creator>kspeaks-form-filler</dc:creator>
    <dc:description>DOCX to HWPX test conversion</dc:description>
  </opf:metadata>
  <opf:manifest>
    <opf:item id="header" href="header.xml" media-type="application/xml"/>
    <opf:item id="section0" href="section0.xml" media-type="application/xml"/>
  </opf:manifest>
  <opf:spine>
    <opf:itemref idref="section0"/>
  </opf:spine>
</opf:package>
"""


def _header_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">
  <hh:docOption lineSpacing="160" defaultFont="Malgun Gothic"/>
  <hh:theme>
    <hh:color name="kspeaks_navy" value="#004D80"/>
    <hh:color name="kspeaks_orange" value="#EF8009"/>
  </hh:theme>
</hh:head>
"""


def _section_xml(title: str, blocks: list[Block]) -> str:
    paragraphs = [
        _paragraph(0, title, kind="title"),
        _paragraph(1, "DOCX to HWPX test conversion", kind="meta"),
    ]
    for idx, block in enumerate(blocks, start=2):
        paragraphs.append(_paragraph(idx, block.text, kind=block.kind))
    body = "\n".join(paragraphs)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
  xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
  xmlns:ks="https://kspeaks.example/schema/docx-conversion">
  <ks:conversion source="docx" fidelity="text-and-table-row-order"/>
{body}
</hs:sec>
"""


def _paragraph(idx: int, text: str, *, kind: str) -> str:
    return (
        f'  <hp:p id="{idx}" paraPrIDRef="0" styleIDRef="0">'
        f'<hp:run charPrIDRef="0"><hp:t>{escape(text)}</hp:t></hp:run>'
        f'<ks:blockKind>{escape(kind)}</ks:blockKind></hp:p>'
    )


def _settings_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <lineSpacing unit="percent">160</lineSpacing>
  <outputFormat>hwpx</outputFormat>
</settings>
"""


def _container_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>
  </rootfiles>
</container>
"""


def _container_rdf(title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description rdf:about="Contents/content.hpf">
    <dc:title>{escape(title)}</dc:title>
    <dc:format>application/hwp+zip</dc:format>
  </rdf:Description>
</rdf:RDF>
"""


def _manifest_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <file-entry full-path="/" media-type="application/hwp+zip"/>
  <file-entry full-path="Contents/content.hpf" media-type="application/xml"/>
  <file-entry full-path="Contents/header.xml" media-type="application/xml"/>
  <file-entry full-path="Contents/section0.xml" media-type="application/xml"/>
  <file-entry full-path="Preview/PrvText.txt" media-type="text/plain"/>
</manifest>
"""


if __name__ == "__main__":
    raise SystemExit(main())
