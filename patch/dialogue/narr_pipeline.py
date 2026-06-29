#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""narr_pipeline.py — 나레이션 재번역 작업 추출/적용.

extract : translation.json -> _narr_jobs.json (대상 엔트리의 화면별 jp/기존ko)
apply   : 번역결과(results.json) -> translation.json 의 해당 엔트리 재조립
          (검증 통과분만; 실패는 원본 보존, 사유 로그). 백업 .prenarr.bak.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import narr_reflow as nr

HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, "translation.json")
JOBS = os.path.join(HERE, "_narr_jobs.json")


def extract():
    d = json.load(open(JSON, encoding="utf-8"))
    jobs = []
    jid = 0
    for fi, f in enumerate(d["files"]):
        for ei, e in enumerate(f["entries"]):
            ok, info = nr.is_target(f["path"], e["segs"])
            if not ok:
                continue
            pairs = nr.split_screens_pairs(e["segs"])
            screens_jp = ["".join(ln["jp"] for ln in sc) for sc in pairs]
            ref_ko = ["".join(ln["ko"] for ln in sc) for sc in pairs]
            jobs.append({
                "id": jid, "loc": [fi, ei], "path": f["path"],
                "speaker": bool(info["has_speaker"]),
                "screens": screens_jp, "ref": ref_ko,
            })
            jid += 1
    json.dump(jobs, open(JOBS, "w", encoding="utf-8"), ensure_ascii=False)
    tot_scr = sum(len(j["screens"]) for j in jobs)
    tot_jp = sum(len("".join(j["screens"])) for j in jobs)
    print(f"추출 완료: {len(jobs)}개 엔트리, {tot_scr}화면, {tot_jp:,}자 -> {JOBS}")


_HW2FW = str.maketrans(
    "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～０１２３４５６７８９"
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
)
# 전각 변환 후에도 shift_jis에 없는 문자 추가 처리
_EXTRA = {"＇": "", "＂": "", "·": "・", "～": "〜", "꽀": ""}

def _normalize_ko(text):
    """반각 ASCII→전각 변환, shift_jis 미지원 문자 치환/제거."""
    t = text.translate(_HW2FW)
    for ch, rep in _EXTRA.items():
        t = t.replace(ch, rep)
    return t


def _try_merge_screens(kor, njp):
    """LLM이 화면을 더 많이 반환한 경우 인접 화면 병합 시도.
    kor: LLM 결과 화면 리스트, njp: 원본 화면 수.
    병합 후 각 화면 줄수 <= MAX_LINES_PER_SCREEN 이어야 성공.
    """
    if len(kor) <= njp:
        return None
    # 초과분을 순서대로 이전 화면에 이어붙여 합산
    merged = list(kor)
    while len(merged) > njp:
        # 가장 짧은 인접쌍 병합
        best_i = None; best_total = 9999
        for i in range(len(merged) - 1):
            a_lines = merged[i].split("\n")
            b_lines = merged[i + 1].split("\n")
            total = len(a_lines) + len(b_lines)
            if total < best_total:
                best_total = total; best_i = i
        if best_i is None or best_total > nr.MAX_LINES_PER_SCREEN:
            return None
        combined = merged[best_i] + "\n" + merged[best_i + 1]
        if len(combined.split("\n")) > nr.MAX_LINES_PER_SCREEN:
            return None
        merged = merged[:best_i] + [combined] + merged[best_i + 2:]
    return merged if len(merged) == njp else None


def _coerce_screens(screens):
    """결과의 screens 를 ['l1\\n l2', ...] 형태(화면당 문자열)로 정규화."""
    out = []
    for sc in screens:
        if isinstance(sc, list):
            out.append("\n".join(str(x) for x in sc))
        else:
            out.append(str(sc))
    return out


def apply(results_path, sample_loc=None):
    jobs = json.load(open(JOBS, encoding="utf-8"))
    by_id = {j["id"]: j for j in jobs}
    res = json.load(open(results_path, encoding="utf-8"))
    # results: {"results":[{id,screens}]} 또는 [{id,screens}]
    items = res.get("results", res) if isinstance(res, dict) else res
    ks = nr.load_ks()
    d = json.load(open(JSON, encoding="utf-8"))

    applied = 0; skipped = []; fixed_wrap = 0
    touched = []
    for it in items:
        if not it or "id" not in it:
            continue
        jid = it["id"]; job = by_id.get(jid)
        if job is None:
            skipped.append((jid, "unknown id")); continue
        kor = _coerce_screens(it.get("screens") or [])
        kor = [_normalize_ko(s) for s in kor]
        njp = len(job["screens"])
        if len(kor) != njp:
            if len(kor) > njp:
                merged = _try_merge_screens(kor, njp)
                if merged:
                    kor = merged
                else:
                    skipped.append((jid, f"화면수 {len(kor)}!={njp}(병합실패)")); continue
            else:
                skipped.append((jid, f"화면수 {len(kor)}!={njp}")); continue
        # 빈 화면 방지
        if any(not s.strip() for s in kor):
            skipped.append((jid, "빈 화면")); continue
        # 검증 + 폴백 줄바꿈
        issues = nr.validate_korean(kor, ks)
        if issues:
            # 폭 초과만이면 그리디 재줄바꿈 시도
            kinds = set(i.split(":")[0][:2] for i in issues)
            kor2 = []
            ok_fix = True
            for s in kor:
                flat = " ".join(s.split("\n"))
                lines = nr.greedy_wrap(flat)
                if len(lines) > nr.MAX_LINES_PER_SCREEN:
                    ok_fix = False; break
                kor2.append("\n".join(lines))
            if ok_fix:
                issues2 = nr.validate_korean(kor2, ks)
                if not issues2:
                    kor = kor2; fixed_wrap += 1
                else:
                    skipped.append((jid, "검증실패:" + ";".join(issues2[:2]))); continue
            else:
                skipped.append((jid, "검증실패:" + ";".join(issues[:2]))); continue
        # 재조립
        fi, ei = job["loc"]
        try:
            new_segs = nr.rebuild_segs(d["files"][fi]["entries"][ei]["segs"], kor)
        except Exception as ex:
            skipped.append((jid, f"rebuild:{ex}")); continue
        d["files"][fi]["entries"][ei]["segs"] = new_segs
        applied += 1
        touched.append((job["path"], ei))

    bak = JSON + ".prenarr.bak"
    if not os.path.isfile(bak):
        json.dump(json.load(open(JSON, encoding="utf-8")),
                  open(bak, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(d, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"적용: {applied}개  (폴백 줄바꿈 보정 {fixed_wrap})  스킵: {len(skipped)}")
    for s in skipped[:25]:
        print("  스킵", s)
    if len(skipped) > 25:
        print(f"  ... 외 {len(skipped)-25}건")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "extract":
        extract()
    elif cmd == "apply":
        apply(sys.argv[2])
    else:
        print("사용: narr_pipeline.py extract | apply <results.json>")
