#!/usr/bin/env python3
"""Survey the official Korean Pokemon Gold/Silver implementation.

The input ROMs are opened read-only.  Outputs contain offsets, hashes,
statistics, and inferred structural metadata only; no ROM payload is copied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


BANK_SIZE = 0x4000
TILE_SIZE = 16
KOREAN_FONT_BANK_FIRST = 0x78
KOREAN_FONT_BANK_LAST = 0x7A
KOREAN_CODE_HIGH_FIRST = 0x01
KOREAN_CODE_HIGH_LAST = 0x0A

EXPECTED_FILES = {
    "KR_GOLD": "Pocket Monsters Geum (Korea).gbc",
    "KR_SILVER": "Pocket Monsters Eun (Korea).gbc",
    "JP_GOLD_0": "Pocket Monsters Kin (Japan).gbc",
    "JP_GOLD_A": "Pocket Monsters Kin (Japan) (Rev A).gbc",
    "JP_SILVER_0": "Pocket Monsters Gin (Japan).gbc",
    "JP_SILVER_A": "Pocket Monsters Gin (Japan) (Rev A).gbc",
    "EN_GOLD": "Pokemon - Gold Version (USA, Europe).gbc",
    "EN_SILVER": "Pokemon - Silver Version (USA, Europe).gbc",
}


def digest(data: bytes, name: str = "sha256") -> str:
    return hashlib.new(name, data).hexdigest()


def banks(data: bytes) -> list[bytes]:
    if len(data) % BANK_SIZE:
        raise ValueError("ROM size is not aligned to 16 KiB banks")
    return [data[i : i + BANK_SIZE] for i in range(0, len(data), BANK_SIZE)]


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    return -sum((n / len(data)) * math.log2(n / len(data)) for n in counts.values())


def difference_ranges(left: bytes, right: bytes) -> tuple[int, int]:
    differing = 0
    ranges = 0
    active = False
    for a, b in zip(left, right):
        changed = a != b
        differing += changed
        if changed and not active:
            ranges += 1
        active = changed
    differing += abs(len(left) - len(right))
    if len(left) != len(right):
        ranges += 1
    return differing, ranges


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_all(data: bytes, needle: bytes) -> list[int]:
    result: list[int] = []
    start = 0
    while True:
        pos = data.find(needle, start)
        if pos < 0:
            return result
        result.append(pos)
        start = pos + 1


def tile_metrics(chunk: bytes) -> dict:
    tiles = [chunk[i : i + TILE_SIZE] for i in range(0, len(chunk), TILE_SIZE)]
    nonblank = [tile for tile in tiles if any(tile)]
    if not nonblank:
        return {
            "tile_count": len(tiles),
            "nonblank_tiles": 0,
            "blank_tiles": len(tiles),
            "unique_nonblank_tiles": 0,
            "unique_nonblank_ratio": 0.0,
            "top_two_rows_blank_ratio": 0.0,
        }
    return {
        "tile_count": len(tiles),
        "nonblank_tiles": len(nonblank),
        "blank_tiles": len(tiles) - len(nonblank),
        "unique_nonblank_tiles": len(set(nonblank)),
        "unique_nonblank_ratio": len(set(nonblank)) / len(nonblank),
        "top_two_rows_blank_ratio": sum(tile[:4] == bytes(4) for tile in nonblank)
        / len(nonblank),
    }


def load_inputs(root: Path) -> tuple[dict[str, Path], dict[str, bytes]]:
    paths = {key: root / filename for key, filename in EXPECTED_FILES.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required ROMs:\n" + "\n".join(missing))
    return paths, {key: path.read_bytes() for key, path in paths.items()}


def build_exact_match_index(all_banks: dict[str, list[bytes]]) -> dict[str, list[tuple[str, int]]]:
    index: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for edition, chunks in all_banks.items():
        for bank, chunk in enumerate(chunks):
            if any(chunk):
                index[digest(chunk)].append((edition, bank))
    return index


def survey_bank_map(all_banks: dict[str, list[bytes]]) -> list[dict]:
    gold = all_banks["KR_GOLD"]
    silver = all_banks["KR_SILVER"]
    exact_index = build_exact_match_index(all_banks)
    rows: list[dict] = []
    for bank, (g, s) in enumerate(zip(gold, silver)):
        changed, ranges = difference_ranges(g, s)
        if not any(g) and not any(s):
            relationship = "BOTH_BLANK"
        elif g == s:
            relationship = "KR_SHARED_IDENTICAL"
        else:
            relationship = "KR_VERSION_SPECIFIC"
        g_matches = [
            f"{edition}:0x{number:02X}"
            for edition, number in exact_index.get(digest(g), [])
            if edition != "KR_GOLD"
        ] if any(g) else []
        s_matches = [
            f"{edition}:0x{number:02X}"
            for edition, number in exact_index.get(digest(s), [])
            if edition != "KR_SILVER"
        ] if any(s) else []
        rows.append(
            {
                "bank_hex": f"0x{bank:02X}",
                "relationship": relationship,
                "differing_bytes": changed,
                "difference_ranges": ranges,
                "gold_sha256": digest(g),
                "silver_sha256": digest(s),
                "gold_nonzero_bytes": sum(value != 0 for value in g),
                "silver_nonzero_bytes": sum(value != 0 for value in s),
                "gold_entropy": f"{entropy(g):.6f}",
                "silver_entropy": f"{entropy(s):.6f}",
                "gold_exact_nonblank_matches": " ".join(g_matches),
                "silver_exact_nonblank_matches": " ".join(s_matches),
            }
        )
    return rows


def survey_font_candidates(gold_banks: list[bytes], silver_banks: list[bytes]) -> list[dict]:
    rows: list[dict] = []
    for bank, (g, s) in enumerate(zip(gold_banks, silver_banks)):
        metrics = tile_metrics(g)
        likely = (
            metrics["nonblank_tiles"] >= 512
            and metrics["unique_nonblank_ratio"] == 1.0
            and metrics["top_two_rows_blank_ratio"] == 1.0
        )
        rows.append(
            {
                "bank_hex": f"0x{bank:02X}",
                **metrics,
                "gold_silver_identical": g == s,
                "font_candidate": likely,
                "bank_sha256": digest(g),
            }
        )
    return rows


def survey_font_layout(gold: bytes, silver: bytes) -> tuple[list[dict], set[tuple[int, int]]]:
    start = KOREAN_FONT_BANK_FIRST * BANK_SIZE
    end = (KOREAN_FONT_BANK_LAST + 1) * BANK_SIZE
    font = gold[start:end]
    silver_font = silver[start:end]
    if font != silver_font:
        raise ValueError("Korean Gold/Silver font region differs")
    rows: list[dict] = []
    valid_codes: set[tuple[int, int]] = set()
    for page in range(12):
        page_bytes = font[page * 0x1000 : (page + 1) * 0x1000]
        page_tiles = [page_bytes[i : i + TILE_SIZE] for i in range(0, 0x1000, TILE_SIZE)]
        for low, tile in enumerate(page_tiles):
            if KOREAN_CODE_HIGH_FIRST <= page <= KOREAN_CODE_HIGH_LAST and any(tile):
                valid_codes.add((page, low))
        absolute_tile = page * 256
        rows.append(
            {
                "page_hex": f"0x{page:02X}",
                "role": (
                    "BASE_GLYPH_PAGE"
                    if page in (0x00, 0x0B)
                    else "TWO_BYTE_GLYPH_PAGE"
                ),
                "bank_hex": f"0x{KOREAN_FONT_BANK_FIRST + absolute_tile // 1024:02X}",
                "bank_tile_offset_hex": f"0x{absolute_tile % 1024:03X}",
                "file_offset_hex": f"0x{start + page * 0x1000:06X}",
                "nonblank_slots": sum(any(tile) for tile in page_tiles),
                "blank_slots": sum(not any(tile) for tile in page_tiles),
                "unique_tiles": len(set(page_tiles)),
                "sha256": digest(page_bytes),
            }
        )
    rows[0]["duplicate_base_page"] = rows[0]["sha256"] == rows[11]["sha256"]
    rows[11]["duplicate_base_page"] = rows[0]["sha256"] == rows[11]["sha256"]
    for row in rows[1:11]:
        row["duplicate_base_page"] = False
    return rows, valid_codes


def survey_two_byte_usage(data: bytes, valid_codes: set[tuple[int, int]]) -> list[dict]:
    rows: list[dict] = []
    for bank, chunk in enumerate(banks(data)):
        occurrences: list[tuple[int, int]] = []
        i = 0
        while i + 1 < len(chunk):
            pair = (chunk[i], chunk[i + 1])
            if pair in valid_codes:
                occurrences.append(pair)
                i += 2
            else:
                i += 1
        rows.append(
            {
                "bank_hex": f"0x{bank:02X}",
                "candidate_two_byte_occurrences": len(occurrences),
                "unique_candidate_codes": len(set(occurrences)),
                "terminator_0x50_count": chunk.count(0x50),
                "space_0x7F_count": chunk.count(0x7F),
                "control_0x59_count": chunk.count(0x59),
                "pair_byte_coverage": f"{(2 * len(occurrences) / BANK_SIZE):.6f}",
            }
        )
    return rows


def survey_bank_reference_candidates(data: bytes) -> list[dict]:
    """Find ROM0 triplets shaped as [important bank, little-endian ROM address].

    Restricting this mechanical scan to ROM0 and the confirmed Korean text/font
    banks keeps the evidence set reviewable and avoids treating arbitrary data
    bytes throughout the 2 MiB ROM as pointers.
    """
    rows: list[dict] = []
    important_banks = {0x68, 0x69, 0x6C, 0x78, 0x79, 0x7A}
    for offset in range(BANK_SIZE - 2):
        bank = data[offset]
        address = data[offset + 1] | (data[offset + 2] << 8)
        if bank in important_banks and 0x4000 <= address <= 0x7FFF:
            rows.append(
                {
                    "file_offset_hex": f"0x{offset:06X}",
                    "containing_bank_hex": f"0x{offset // BANK_SIZE:02X}",
                    "candidate_target_bank_hex": f"0x{bank:02X}",
                    "candidate_target_address_hex": f"0x{address:04X}",
                }
            )
    return rows


def survey_name_tables(gold: bytes, silver: bytes) -> tuple[list[dict], dict]:
    # The code at 0x3604 loads an eight-entry bank/address dispatch table at
    # ROM0:35C3.  Four entries point to Bank 6C.  Their consecutive boundaries
    # expose the item, trainer class, fixed-width species, and move-name tables.
    dispatch_offset = 0x35C3
    dispatch_count = 8
    entries: list[dict] = []
    for index in range(dispatch_count):
        pos = dispatch_offset + index * 3
        bank = gold[pos]
        address = gold[pos + 1] | (gold[pos + 2] << 8)
        entries.append(
            {
                "dispatch_index": index,
                "file_offset_hex": f"0x{pos:06X}",
                "bank_hex": f"0x{bank:02X}",
                "address_hex": f"0x{address:04X}",
            }
        )
    anchors = [0x4000, 0x49A1, 0x4C4A, 0x564A]
    actual = sorted(
        entry["address_hex"]
        for entry in entries
        if entry["bank_hex"] == "0x6C"
    )
    expected = sorted(f"0x{address:04X}" for address in anchors)
    if actual != expected:
        raise ValueError(f"Unexpected Bank 6C dispatch anchors: {actual}")
    bank_gold = gold[0x6C * BANK_SIZE : 0x6D * BANK_SIZE]
    bank_silver = silver[0x6C * BANK_SIZE : 0x6D * BANK_SIZE]
    if bank_gold != bank_silver:
        raise ValueError("Korean Gold/Silver Bank 6C differs")
    last_move_byte = max(i for i, value in enumerate(bank_gold[0x164A:]) if value) + 0x164A + 1
    regions = [
        ("ITEM_NAMES", 0x4000, 0x49A1, "TERMINATED", 256),
        ("TRAINER_CLASS_NAMES", 0x49A1, 0x4C4A, "TERMINATED", 67),
        ("POKEMON_NAME_SLOTS", 0x4C4A, 0x564A, "FIXED_10_BYTES", 256),
        ("MOVE_NAMES", 0x564A, 0x4000 + last_move_byte, "TERMINATED", 251),
    ]
    table_rows: list[dict] = []
    for role, start, end, storage, expected_records in regions:
        chunk = bank_gold[start - 0x4000 : end - 0x4000]
        observed_records = len(chunk) // 10 if storage == "FIXED_10_BYTES" else chunk.count(0x50)
        table_rows.append(
            {
                "role": role,
                "bank_hex": "0x6C",
                "start_address_hex": f"0x{start:04X}",
                "end_address_exclusive_hex": f"0x{end:04X}",
                "file_offset_hex": f"0x{0x6C * BANK_SIZE + start - 0x4000:06X}",
                "size_bytes": len(chunk),
                "storage": storage,
                "observed_records": observed_records,
                "expected_records": expected_records,
                "record_count_matches": observed_records == expected_records,
                "sha256": digest(chunk),
            }
        )
    evidence = {
        "dispatch_table_file_offset_hex": "0x0035C3",
        "dispatch_loader_signature_file_offset_hex": "0x003604",
        "fixed_name_copy_signature_file_offset_hex": "0x00365F",
        "fixed_name_bank": "0x6C",
        "fixed_name_address": "0x4C4A",
        "fixed_name_record_size": 10,
        "gold_silver_dispatch_bytes_identical": gold[0x35C3:0x35DB] == silver[0x35C3:0x35DB],
        "gold_silver_bank_6c_identical": bank_gold == bank_silver,
    }
    return entries + table_rows, evidence


def build_report(
    inputs: dict[str, bytes],
    bank_rows: list[dict],
    font_candidates: list[dict],
    font_layout: list[dict],
    valid_codes: set[tuple[int, int]],
    usage_rows: list[dict],
    name_rows: list[dict],
    evidence: dict,
) -> str:
    shared = sum(row["relationship"] == "KR_SHARED_IDENTICAL" for row in bank_rows)
    versioned = sum(row["relationship"] == "KR_VERSION_SPECIFIC" for row in bank_rows)
    blank = sum(row["relationship"] == "BOTH_BLANK" for row in bank_rows)
    detected_font_banks = [row["bank_hex"] for row in font_candidates if row["font_candidate"]]
    table_rows = [row for row in name_rows if "role" in row]
    ranked_usage = sorted(
        usage_rows,
        key=lambda row: row["candidate_two_byte_occurrences"],
        reverse=True,
    )[:12]
    changed_banks = [row["bank_hex"] for row in bank_rows if row["relationship"] == "KR_VERSION_SPECIFIC"]
    lines = [
        "# GS Korean 구현 구조 조사 — 1단계",
        "",
        "## 결론",
        "",
        "한국 정식판 금·은을 읽기 전용으로 다시 조사한 결과, 두 ROM은 128개 뱅크 중 "
        f"공통 비공백 {shared}개, 버전별 {versioned}개, 양쪽 공통 공백 {blank}개로 나뉜다.",
        "",
        f"자동 글꼴 탐지 조건을 단독으로 만족한 뱅크는 `{', '.join(detected_font_banks)}`다. "
        "세 뱅크는 금·은에서 바이트 단위로 동일하고, 8×8/16바이트 타일 배열로 해석하면 "
        f"상위 바이트 `01–0A`에 대응하는 비공백 2바이트 글리프 슬롯이 {len(valid_codes):,}개다.",
        "",
        "## 원본 식별",
        "",
        "| 판본 | 크기 | SHA-1 | SHA-256 |",
        "| --- | ---: | --- | --- |",
        f"| 한국판 금 | {len(inputs['KR_GOLD']):,} | `{digest(inputs['KR_GOLD'], 'sha1')}` | `{digest(inputs['KR_GOLD'])}` |",
        f"| 한국판 은 | {len(inputs['KR_SILVER']):,} | `{digest(inputs['KR_SILVER'], 'sha1')}` | `{digest(inputs['KR_SILVER'])}` |",
        "",
        "## 금·은 뱅크 관계",
        "",
        f"- 공통 비공백 뱅크: {shared}개",
        f"- 버전별 변경 뱅크: {versioned}개",
        f"- 양쪽 모두 00으로 채워진 뱅크: {blank}개",
        f"- 변경 뱅크: `{', '.join(changed_banks)}`",
        "",
        "공백 뱅크는 물리적으로 00이라는 뜻일 뿐이다. 호출 코드와 포인터에서 참조되지 않는다는 "
        "사실까지 확인하기 전에는 자유 공간으로 판정하지 않는다.",
        "",
        "## 한글 글꼴과 2바이트 코드 구조",
        "",
        "| 페이지 | 역할 | 뱅크 | 타일 시작 | 비공백 슬롯 |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in font_layout:
        lines.append(
            f"| `{row['page_hex']}` | {row['role']} | `{row['bank_hex']}` | "
            f"`{row['bank_tile_offset_hex']}` | {row['nonblank_slots']} |"
        )
    lines += [
        "",
        "페이지 `00`과 `0B`는 해시가 같은 기본 글리프 페이지다. 페이지 `01–0A`는 "
        "2바이트 코드의 상위 바이트와 직접 대응하는 연속 글리프 페이지로 확인됐다. "
        "현재 단계에서는 2,353개 슬롯을 Unicode 음절에 단정적으로 대응하지 않는다. "
        "다음 단계에서 문자 순서와 실제 문자열을 교차 검증한다.",
        "",
        "## Bank 6C 명칭 테이블",
        "",
        "ROM0의 `0x35C3` 디스패치 테이블과 이를 읽는 `0x3604` 코드가 Bank 6C의 "
        "네 주소를 직접 참조한다. `0x365F`의 루틴은 Bank 6C를 선택하고 `0x4C4A`에서 "
        "인덱스당 10바이트를 복사하므로 고정 길이 포켓몬 이름 슬롯 구조가 코드로 확인된다.",
        "",
        "| 구역 | 주소 범위 | 저장 형식 | 관측 레코드 | 검증 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in table_rows:
        lines.append(
            f"| {row['role']} | `{row['start_address_hex']}–{row['end_address_exclusive_hex']}` | "
            f"{row['storage']} | {row['observed_records']} | "
            f"{'일치' if row['record_count_matches'] else '불일치'} |"
        )
    lines += [
        "",
        "이 네 구역은 금·은에서 완전히 동일하다. 가변 길이 구역은 `0x50` 종료 코드 수로, "
        "포켓몬 이름 구역은 `256 × 10바이트` 경계로 레코드 수를 검증했다.",
        "",
        "## 2바이트 문자열 밀도가 높은 뱅크",
        "",
        "| 뱅크 | 유효 코드쌍 출현 | 고유 코드 | `50` | `7F` |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in ranked_usage:
        lines.append(
            f"| `{row['bank_hex']}` | {row['candidate_two_byte_occurrences']:,} | "
            f"{row['unique_candidate_codes']:,} | {row['terminator_0x50_count']} | "
            f"{row['space_0x7F_count']} |"
        )
    lines += [
        "",
        "이 표는 글꼴 슬롯과 일치하는 바이트쌍을 기계적으로 센 후보 통계다. 코드나 그래픽 안의 "
        "우연한 바이트쌍도 포함될 수 있으므로 각 뱅크의 기능은 포인터와 호출 루틴으로 확정한다.",
        "",
        "## 다음 단계",
        "",
        "1. `01–0A` 코드 2,353개를 Unicode 한글 음절과 왕복 대응시킨다.",
        "2. Bank 6C 네 명칭 구역 830개 레코드를 UTF-8로 완전 추출한다.",
        "3. 금·은 재삽입 결과가 각각 원본 SHA-1과 일치하는지 검증한다.",
        "4. Bank 68–69의 도감 문자열 구조와 포인터를 추적한다.",
        "5. 글꼴 로더와 실제 출력 루틴을 따라 Bank 78–7A 선택 계산을 확정한다.",
        "",
        "## 재현",
        "",
        "```bash",
        "python3 gs_korean_structure_scan.py /path/to/rom-folder /path/to/output",
        "```",
        "",
        "원본 ROM은 수정하지 않으며 산출물에는 ROM 바이트나 추출 글꼴 이미지가 포함되지 않는다.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    paths, inputs = load_inputs(args.rom_root)
    all_banks = {key: banks(value) for key, value in inputs.items()}
    if len(all_banks["KR_GOLD"]) != 128 or len(all_banks["KR_SILVER"]) != 128:
        raise ValueError("Expected 128-bank Korean ROMs")

    bank_rows = survey_bank_map(all_banks)
    font_candidates = survey_font_candidates(all_banks["KR_GOLD"], all_banks["KR_SILVER"])
    font_layout, valid_codes = survey_font_layout(inputs["KR_GOLD"], inputs["KR_SILVER"])
    usage_rows = survey_two_byte_usage(inputs["KR_GOLD"], valid_codes)
    reference_rows = survey_bank_reference_candidates(inputs["KR_GOLD"])
    name_rows, evidence = survey_name_tables(inputs["KR_GOLD"], inputs["KR_SILVER"])

    output = args.output
    write_csv(output / "kr_bank_map.csv", bank_rows)
    write_json(output / "kr_bank_map.json", bank_rows)
    write_csv(output / "font_bank_candidates.csv", font_candidates)
    write_json(output / "font_bank_candidates.json", font_candidates)
    write_csv(output / "font_layout.csv", font_layout)
    write_json(output / "font_layout.json", font_layout)
    write_csv(output / "two_byte_usage_by_bank.csv", usage_rows)
    write_json(output / "two_byte_usage_by_bank.json", usage_rows)
    write_csv(output / "bank_reference_candidates.csv", reference_rows)
    write_json(output / "bank_reference_candidates.json", reference_rows)
    write_csv(output / "bank_6c_name_tables.csv", name_rows)
    write_json(output / "bank_6c_name_tables.json", name_rows)
    write_json(output / "implementation_evidence.json", evidence)
    report = build_report(
        inputs,
        bank_rows,
        font_candidates,
        font_layout,
        valid_codes,
        usage_rows,
        name_rows,
        evidence,
    )
    (output / "GS_KOREAN_IMPLEMENTATION_PHASE1_KO.md").write_text(report, encoding="utf-8")
    summary = {
        "input_files": {key: str(path) for key, path in paths.items()},
        "korean_bank_count": 128,
        "shared_nonblank_banks": sum(row["relationship"] == "KR_SHARED_IDENTICAL" for row in bank_rows),
        "version_specific_banks": sum(row["relationship"] == "KR_VERSION_SPECIFIC" for row in bank_rows),
        "both_blank_banks": sum(row["relationship"] == "BOTH_BLANK" for row in bank_rows),
        "font_banks": [row["bank_hex"] for row in font_candidates if row["font_candidate"]],
        "valid_two_byte_glyph_slots": len(valid_codes),
        "bank_6c_record_count": sum(row["observed_records"] for row in name_rows if "role" in row),
        "evidence": evidence,
    }
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
