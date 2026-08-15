#!/usr/bin/env python3
"""Module 0 lab — the minimum viable security harness: plan → act → verify → stop.

The point of the lab: **the verifier is the security control; everything else is
plumbing.** Run the same loop with three verifiers and watch what happens.

    python3 loop.py --task fix-tests --verifier pytest      # deterministic oracle
    python3 loop.py --task fix-tests --verifier llm-judge   # self-grading
    python3 loop.py --task fix-tests --verifier none        # no stop signal

Model access is OpenAI-compatible, so it runs on Ollama / vLLM / LiteLLM / any
free open-weight tier (see MODELS.md):

    export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6

`--model stub` uses a deterministic built-in fake model so the loop mechanics
(and this lab's tests) run with no model at all. It is a test fixture, not a
result — never quote a stub run as a finding.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- model access
def call_model(prompt: str, model: str, base_url: str | None, api_key: str | None,
               step: int) -> str:
    """One completion. `stub` is a deterministic fake used for offline testing."""
    if model == "stub":
        # Deterministic scripted behaviour so the loop can be exercised offline:
        # step 0 proposes a wrong patch, step 1 proposes the correct one.
        return ("PATCH: return a - b" if step == 0 else "PATCH: return a + b")
    import urllib.request
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        f"{(base_url or 'http://localhost:11434/v1').rstrip('/')}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key or 'ollama'}"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


# ------------------------------------------------------------------- the tools
def apply_patch(text: str, target: Path) -> bool:
    """The single 'action' this harness can take: rewrite the function body.

    Deliberately narrow — B2.3 ('design the dangerous call out of existence')
    is exactly this idea. There is no shell tool here on purpose.
    """
    m = re.search(r"PATCH:\s*(.+)", text)
    if not m:
        return False
    body = m.group(1).strip()
    target.write_text(f"def add(a, b):\n    {body}\n")
    return True


# --------------------------------------------------------------- the verifiers
def verify_pytest(workdir: Path) -> tuple[bool, str]:
    """Deterministic oracle. It cannot be talked out of its verdict."""
    # Drop stale bytecode first: a verifier reading a cached .pyc reports on code
    # that is no longer on disk — a lying oracle is worse than no oracle.
    import shutil
    shutil.rmtree(workdir / "__pycache__", ignore_errors=True)
    env = {**os.environ, "PYTHONPATH": str(workdir), "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_add.py"],
                       capture_output=True, text=True, cwd=workdir, env=env)
    lines = [l for l in (p.stdout + p.stderr).strip().splitlines() if l.strip()]
    return p.returncode == 0, (lines[-1] if lines else "no output")


def verify_llm_judge(workdir: Path, model: str, base_url, api_key) -> tuple[bool, str]:
    """Self-grading: a judge drawn from the same family as the generator.

    This is the failure mode B2.2 is about. With --model stub the judge is
    scripted to approve, which is precisely the point being demonstrated.
    """
    if model == "stub":
        return True, "judge says: looks correct to me"
    code = (workdir / "add.py").read_text()
    out = call_model(f"Does this satisfy 'add two numbers'? Answer PASS or FAIL only.\n\n{code}",
                     model, base_url, api_key, step=99)
    return "PASS" in out.upper(), f"judge says: {out.strip()[:60]}"


def verify_none(_: Path) -> tuple[bool, str]:
    """No stop signal at all — the loop can only end on budget."""
    return False, "no verifier configured"


# ------------------------------------------------------------------- the loop
@dataclass
class Budget:
    max_steps: int = 6
    timeout_s: float = 120.0
    token_ceiling: int = 50_000
    started: float = field(default_factory=time.time)
    tokens: int = 0

    def exhausted(self) -> str | None:
        if self.tokens >= self.token_ceiling:
            return "token_ceiling"
        if time.time() - self.started > self.timeout_s:
            return "timeout"
        return None


def run(task: str, verifier: str, model: str, budget: Budget,
        base_url=None, api_key=None, workdir: Path | None = None) -> dict:
    workdir = workdir or (HERE / "workspace")
    workdir.mkdir(exist_ok=True)
    # seed the workspace: a deliberately broken implementation + its test
    (workdir / "add.py").write_text("def add(a, b):\n    return a * b\n")
    (workdir / "test_add.py").write_text(
        "from add import add\n\ndef test_add():\n    assert add(2, 3) == 5\n    assert add(0, 0) == 0\n")

    trace, stop_reason, ok = [], None, False
    for step in range(budget.max_steps):
        if (why := budget.exhausted()):
            stop_reason = why
            break
        # PLAN + ACT
        prompt = (f"Task: {task}. The file add.py must make test_add.py pass.\n"
                  f"Current:\n{(workdir/'add.py').read_text()}\n"
                  "Reply with exactly one line: PATCH: <new function body>")
        out = call_model(prompt, model, base_url, api_key, step)
        budget.tokens += len(prompt) // 4 + len(out) // 4
        acted = apply_patch(out, workdir / "add.py")
        # VERIFY
        if verifier == "pytest":
            ok, detail = verify_pytest(workdir)
        elif verifier == "llm-judge":
            ok, detail = verify_llm_judge(workdir, model, base_url, api_key)
        else:
            ok, detail = verify_none(workdir)
        trace.append({"step": step, "acted": acted, "verified": ok, "detail": detail,
                      "code": (workdir / "add.py").read_text().strip()})
        # STOP
        if ok:
            stop_reason = "verified"
            break
    else:
        stop_reason = stop_reason or "max_steps"

    # ground truth: does the code ACTUALLY pass, regardless of what the verifier said
    truly_ok, _ = verify_pytest(workdir)
    return {"task": task, "verifier": verifier, "model": model,
            "stop_reason": stop_reason, "verifier_said_ok": ok,
            "actually_correct": truly_ok, "steps": len(trace),
            "tokens": budget.tokens, "trace": trace}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default="fix-tests")
    ap.add_argument("--verifier", default="pytest", choices=["pytest", "llm-judge", "none"])
    ap.add_argument("--model", default=os.environ.get("MODEL", "stub"))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL"))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"))
    ap.add_argument("--max-steps", type=int, default=6)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--token-ceiling", type=int, default=50_000)
    ap.add_argument("--json", action="store_true", help="emit the full trace as JSON")
    a = ap.parse_args()

    r = run(a.task, a.verifier, a.model,
            Budget(max_steps=a.max_steps, timeout_s=a.timeout, token_ceiling=a.token_ceiling),
            a.base_url, a.api_key)

    if a.json:
        print(json.dumps(r, indent=1))
        return 0
    print(f"\n=== plan→act→verify→stop  ({r['model']} / verifier={r['verifier']}) ===")
    for t in r["trace"]:
        print(f"  step {t['step']}: acted={t['acted']} verified={t['verified']}  {t['detail']}")
        print(f"          code: {t['code'].splitlines()[-1].strip()}")
    print(f"\n  stop reason      : {r['stop_reason']}")
    print(f"  verifier said OK : {r['verifier_said_ok']}")
    print(f"  ACTUALLY correct : {r['actually_correct']}")
    if r["verifier_said_ok"] and not r["actually_correct"]:
        print("\n  ⚠  The loop declared success on broken code. That is the lesson:")
        print("     a verifier that can be talked into agreeing is not a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
