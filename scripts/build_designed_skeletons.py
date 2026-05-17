from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]

HWPX_ENTRIES = {
    "mimetype",
    "version.xml",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
    "Preview/PrvText.txt",
    "settings.xml",
    "META-INF/container.xml",
    "META-INF/container.rdf",
    "META-INF/manifest.xml",
}

NAVY = "#004D80"
ORANGE = "#EF8009"
LIGHT_NAVY = "#E8F1F7"
LIGHT_ORANGE = "#FFF3E8"
GRAY = "#F4F6F8"


@dataclass(frozen=True)
class SkeletonSpec:
    form_id: str
    ko_name: str
    title: str
    subtitle: str
    blocks: list[str]


def main() -> int:
    specs = [_progress_brief(), _invoice(), _staff_profile()]
    for spec in specs:
        output = ROOT / "templates" / "forms" / spec.form_id / "skeleton" / "skeleton.hwpx"
        output.parent.mkdir(parents=True, exist_ok=True)
        _write_hwpx(spec, output)
        print(f"built {output.relative_to(ROOT)}")
    return 0


def _progress_brief() -> SkeletonSpec:
    return SkeletonSpec(
        form_id="progress_brief",
        ko_name="중간보고",
        title="Progress Brief",
        subtitle="Korea Speaks signature report layout",
        blocks=[
            _header_box(
                "KOREA SPEAKS / PROGRESS BRIEF",
                "중간보고",
                "Project: {{project_name}} | Period: {{reporting_period}} | Date: {{report_date}}",
            ),
            _key_summary_box(
                "핵심 요약",
                [
                    "진행 요약: {{progress_summary}}",
                    "주요 이슈: {{key_issue}}",
                    "다음 조치: {{next_action}}",
                ],
            ),
            _two_column_table(
                "진행 현황",
                "향후 조치",
                [
                    ("프로젝트", "{{project_name}}"),
                    ("보고 기간", "{{reporting_period}}"),
                    ("작성일", "{{report_date}}"),
                    ("진행 요약", "{{progress_summary}}"),
                    ("주요 이슈", "{{key_issue}}"),
                    ("담당/작성", "{{prepared_by}}"),
                ],
                [
                    ("다음 조치", "{{next_action}}"),
                    ("의사결정 필요", "{{key_issue}}"),
                    ("공유 대상", "{{prepared_by}}"),
                    ("후속 일정", "{{reporting_period}}"),
                    ("보고 메모", "{{progress_summary}}"),
                    ("문서 상태", "Draft / slot-ready"),
                ],
            ),
            _footer_note(
                "Slot-ready skeleton. Replace tokens only; keep source forms in the "
                "private data repo."
            ),
        ],
    )


def _invoice() -> SkeletonSpec:
    return SkeletonSpec(
        form_id="invoice",
        ko_name="청구서",
        title="Invoice",
        subtitle="Clean financial request layout",
        blocks=[
            _header_box(
                "KOREA SPEAKS / INVOICE",
                "청구서",
                "Invoice No. {{invoice_number}} | Date: {{invoice_date}}",
            ),
            _key_summary_box(
                "청구 정보",
                [
                    "수신처: {{client_name}}",
                    "청구번호: {{invoice_number}}",
                    "청구일: {{invoice_date}}",
                ],
            ),
            _amount_table(
                [
                    ("공급가액", "{{supply_amount}}"),
                    ("부가세", "{{tax_amount}}"),
                    ("합계", "{{total_amount}}"),
                ]
            ),
            _footer_note(
                "Payment account, seal, and real company details are supplied from the "
                "private data repository."
            ),
        ],
    )


def _staff_profile() -> SkeletonSpec:
    return SkeletonSpec(
        form_id="staff_profile",
        ko_name="직원정보",
        title="Staff Profile",
        subtitle="Internal staff information card",
        blocks=[
            _header_box(
                "KOREA SPEAKS / STAFF PROFILE",
                "직원정보",
                "Name: {{staff_name}} | Role: {{role_title}}",
            ),
            _two_column_table(
                "기본 정보",
                "정산 정보",
                [
                    ("이름", "{{staff_name}}"),
                    ("역할", "{{role_title}}"),
                    ("이메일", "{{email}}"),
                    ("연락처", "{{phone}}"),
                ],
                [
                    ("은행", "{{bank_name}}"),
                    ("예금주", "{{account_holder}}"),
                    ("연락처", "{{phone}}"),
                    ("확인자", "{{staff_name}}"),
                ],
            ),
            _key_summary_box(
                "운영 메모",
                [
                    "프로젝트 투입 전 연락처와 정산 정보를 확인합니다.",
                    "민감한 실계좌 값은 public repository에 저장하지 않습니다.",
                ],
            ),
            _footer_note("This is a placeholder skeleton for slot mapping and smoke tests."),
        ],
    )


def _header_box(kicker: str, heading: str, meta: str) -> str:
    return "\n".join(
        [
            f"[HEADER_BOX fill={NAVY} accent={ORANGE}]",
            kicker,
            heading,
            meta,
            "[/HEADER_BOX]",
        ]
    )


def _key_summary_box(title: str, lines: list[str]) -> str:
    body = "\n".join(f"- {line}" for line in lines)
    return "\n".join(
        [
            f"[KEY_SUMMARY_BOX fill={LIGHT_ORANGE} border={ORANGE}]",
            title,
            body,
            "[/KEY_SUMMARY_BOX]",
        ]
    )


def _two_column_table(
    left_title: str,
    right_title: str,
    left_rows: list[tuple[str, str]],
    right_rows: list[tuple[str, str]],
) -> str:
    rows = [f"| {left_title} | {right_title} |", "| --- | --- |"]
    for left, right in zip(_format_rows(left_rows), _format_rows(right_rows)):
        rows.append(f"| {left} | {right} |")
    return "\n".join(
        [
            f"[TWO_COLUMN_TABLE fill={LIGHT_NAVY} border={NAVY}]",
            *rows,
            "[/TWO_COLUMN_TABLE]",
        ]
    )


def _amount_table(rows: list[tuple[str, str]]) -> str:
    output = [
        f"[AMOUNT_TABLE fill={GRAY} total_accent={NAVY}]",
        "| 항목 | 금액 |",
        "| --- | ---: |",
    ]
    output.extend(f"| {label} | {value} |" for label, value in rows)
    output.append("[/AMOUNT_TABLE]")
    return "\n".join(output)


def _format_rows(rows: list[tuple[str, str]]) -> list[str]:
    return [f"{label}: {value}" for label, value in rows]


def _footer_note(text: str) -> str:
    return f"[FOOTER_NOTE]\n{text}\n[/FOOTER_NOTE]"


def _write_hwpx(spec: SkeletonSpec, output: Path) -> None:
    plain_text = _plain_text(spec)
    entries = {
        "mimetype": "application/hwp+zip",
        "version.xml": _version_xml(),
        "Contents/content.hpf": _content_hpf(spec),
        "Contents/header.xml": _header_xml(),
        "Contents/section0.xml": _section_xml(spec),
        "Preview/PrvText.txt": plain_text,
        "settings.xml": _settings_xml(),
        "META-INF/container.xml": _container_xml(),
        "META-INF/container.rdf": _container_rdf(spec),
        "META-INF/manifest.xml": _manifest_xml(),
    }
    missing = HWPX_ENTRIES.difference(entries)
    if missing:
        raise RuntimeError(f"missing HWPX entries: {', '.join(sorted(missing))}")
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("mimetype", entries["mimetype"], compress_type=zipfile.ZIP_STORED)
        for name, content in entries.items():
            if name == "mimetype":
                continue
            archive.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)


def _plain_text(spec: SkeletonSpec) -> str:
    return "\n\n".join([spec.title, spec.ko_name, spec.subtitle, *spec.blocks])


def _version_xml() -> str:
    return dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <hv:version xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version"
          app="kspeaks-form-filler" hwpx="5.1.3"/>
        """
    )


def _content_hpf(spec: SkeletonSpec) -> str:
    return dedent(
        f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <opf:package xmlns:opf="http://www.idpf.org/2007/opf/"
          xmlns:dc="http://purl.org/dc/elements/1.1/" version="1.0">
          <opf:metadata>
            <dc:title>{escape(spec.title)} / {escape(spec.ko_name)}</dc:title>
            <dc:creator>kspeaks-form-filler</dc:creator>
            <dc:description>{escape(spec.subtitle)}</dc:description>
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
    )


def _header_xml() -> str:
    return dedent(
        f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">
          <hh:docOption lineSpacing="160" defaultFont="Malgun Gothic"/>
          <hh:theme>
            <hh:color name="kspeaks_navy" value="{NAVY}"/>
            <hh:color name="kspeaks_orange" value="{ORANGE}"/>
            <hh:color name="light_navy" value="{LIGHT_NAVY}"/>
            <hh:color name="light_orange" value="{LIGHT_ORANGE}"/>
          </hh:theme>
        </hh:head>
        """
    )


def _section_xml(spec: SkeletonSpec) -> str:
    paragraphs = "\n".join(
        _paragraph(text, idx) for idx, text in enumerate(_plain_text(spec).splitlines())
    )
    return dedent(
        f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
          xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
          xmlns:ks="https://kspeaks.example/schema/skeleton">
          <ks:design formId="{escape(spec.form_id)}" koName="{escape(spec.ko_name)}"
            lineSpacing="160" primary="{NAVY}" accent="{ORANGE}">
            <ks:note>
              Generalized public skeleton. Visual markers map to HWPX tables and fills
              when a real source form is available.
            </ks:note>
          </ks:design>
        {paragraphs}
        </hs:sec>
        """
    )


def _paragraph(text: str, idx: int) -> str:
    if not text:
        text = " "
    escaped = escape(text)
    return (
        f'  <hp:p id="{idx}" paraPrIDRef="0" styleIDRef="0">'
        f'<hp:run charPrIDRef="0"><hp:t>{escaped}</hp:t></hp:run></hp:p>'
    )


def _settings_xml() -> str:
    return dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <settings>
          <lineSpacing unit="percent">160</lineSpacing>
          <outputFormat>hwpx</outputFormat>
        </settings>
        """
    )


def _container_xml() -> str:
    return dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>
          </rootfiles>
        </container>
        """
    )


def _container_rdf(spec: SkeletonSpec) -> str:
    return dedent(
        f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:dc="http://purl.org/dc/elements/1.1/">
          <rdf:Description rdf:about="Contents/content.hpf">
            <dc:title>{escape(spec.title)}</dc:title>
            <dc:format>application/hwp+zip</dc:format>
          </rdf:Description>
        </rdf:RDF>
        """
    )


def _manifest_xml() -> str:
    return dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <manifest xmlns="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
          <file-entry full-path="/" media-type="application/hwp+zip"/>
          <file-entry full-path="Contents/content.hpf" media-type="application/xml"/>
          <file-entry full-path="Contents/header.xml" media-type="application/xml"/>
          <file-entry full-path="Contents/section0.xml" media-type="application/xml"/>
          <file-entry full-path="Preview/PrvText.txt" media-type="text/plain"/>
        </manifest>
        """
    )


if __name__ == "__main__":
    raise SystemExit(main())
