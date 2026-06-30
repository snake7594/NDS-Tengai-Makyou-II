#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_overflow.py — 3줄 초과 대사 화면 전체 검출 및 자동 수정.

유효 줄 수 계산:
  - split_screens_pairs 로 화면 단위 분리
  - 화면 내 각 줄(0x0D 00 기준): 1 + ko.count('\n')
  - from_segments 는 ko 의 '\n' → 0x0D 00 으로 변환하므로
    ko '\n' 포함 줄도 게임에서 여러 줄로 표시됨

수정 방법:
  - 화면의 모든 ko 를 '\n' 으로 묶어 평탄화(flatten)
  - greedy_wrap(limit=18) 으로 재줄바꿈 → ≤3줄
  - 여전히 3줄 초과면 앞 3줄만 보존
  - rebuild_segs 로 세그먼트 재조립
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import narr_reflow as nr

HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, "translation.json")
MAX_L = nr.MAX_LINES_PER_SCREEN   # 3
MAX_W = nr.MAX_LINE                # 18


def eff_lines(screen_lines):
    """화면 줄 리스트 → 유효 줄 수 (ko 기준)."""
    return sum(1 + (ln.get("ko") or "").count("\n") for ln in screen_lines)


def screen_ko(screen_lines):
    """화면의 ko 전체를 '\n' 구분 단일 문자열로."""
    return "\n".join(ln.get("ko") or "" for ln in screen_lines)


def has_ko(screen_lines):
    return any((ln.get("ko") or "").strip() for ln in screen_lines)


def fix_ko(ko_str):
    """ko_str(줄들 '\n' 구분) → greedy_wrap 후 '\n' 구분 문자열(≤3줄)."""
    flat = " ".join(ko_str.split("\n"))
    lines = nr.greedy_wrap(flat.strip(), MAX_W)
    if len(lines) > MAX_L:
        lines = lines[:MAX_L]
    return "\n".join(lines)


def has_inline11(segs):
    for s in segs:
        if "c" in s:
            ops = bytes.fromhex(s["c"])
            for j in range(0, len(ops), 2):
                if ops[j] == 0x11:
                    return True
    return False


def has_decode_err(segs):
    return any("〓" in s.get("jp", "") for s in segs)


def scan_and_fix():
    d = json.load(open(JSON, encoding="utf-8"))
    total_entries = sum(len(f["entries"]) for f in d["files"])
    violations = []
    fixed = 0
    skipped = 0

    for fi, f in enumerate(d["files"]):
        for ei, e in enumerate(f["entries"]):
            segs = e["segs"]

            # 인라인 0x11 or 디코드오류 → 구조 위험, 건너뜀
            if has_inline11(segs) or has_decode_err(segs):
                skipped += 1
                continue

            screens = nr.split_screens_pairs(segs)
            if not screens:
                continue

            # 위반 여부 체크
            bad = [(si, s) for si, s in enumerate(screens)
                   if has_ko(s) and eff_lines(s) > MAX_L]
            if not bad:
                continue

            # 위반 기록
            for si, s in bad:
                violations.append({
                    "path": f["path"], "ei": ei, "si": si,
                    "eff": eff_lines(s),
                    "ko": screen_ko(s),
                })

            # 수정: 모든 화면의 ko 준비 (위반화면만 fix_ko)
            fixed_screens = []
            for si, s in enumerate(screens):
                ko = screen_ko(s)
                if has_ko(s) and eff_lines(s) > MAX_L:
                    ko = fix_ko(ko)
                fixed_screens.append(ko)

            try:
                new_segs = nr.rebuild_segs(segs, fixed_screens)
                e["segs"] = new_segs
                fixed += 1
            except Exception as ex:
                print(f"  rebuild 실패 {f['path']}[{ei}]: {ex}")

    print(f"전체 엔트리: {total_entries:,}")
    print(f"건너뜀 (inline/decode): {skipped}")
    print(f"3줄 초과 화면 발견: {len(violations)}")
    print(f"수정된 엔트리: {fixed}")
    print()

    # 위반 샘플 출력
    for v in violations[:20]:
        lines_preview = v['ko'].replace('\n', '↵')[:60]
        print(f"  [{v['path']}] ei={v['ei']} si={v['si']} "
              f"({v['eff']}줄): {lines_preview}")
    if len(violations) > 20:
        print(f"  ... 외 {len(violations)-20}건")

    if fixed > 0:
        bak = JSON + ".pre_overflow_fix.bak"
        if not os.path.isfile(bak):
            import shutil
            shutil.copy2(JSON, bak)
        json.dump(d, open(JSON, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"\n백업: {bak}")
        print(f"저장: {JSON}")
    return len(violations), fixed


if __name__ == "__main__":
    scan_and_fix()
