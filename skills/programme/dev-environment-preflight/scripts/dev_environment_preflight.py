#!/usr/bin/env python3
"""Prove this machine can run a model-backed skill, by running one.

Three layers have to work and each fails differently, so each is reported
separately rather than as one "it works" or one traceback:

    runtime importable  -> a PYTHONPATH problem
    endpoint configured -> a setup problem
    endpoint answers    -> a server or key problem

Step 3 deliberately *causes* the unconfigured failure in a child process before
the real call, so the reader meets that message here — where it is expected and
explained — rather than on lesson forty where it reads as a broken repository.

Run it from the repository root:

    PYTHONPATH=skills/_runtime python3 \\
      skills/programme/dev-environment-preflight/scripts/dev_environment_preflight.py
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "_runtime"))

import cyber_commons_skill_runtime as rt  # noqa: E402

SKILL = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"

# Small enough to be cheap on any tier, specific enough that a wrong answer is
# obvious rather than plausible. The model is asked to apply this skill's own
# procedure, which is also the mechanism every other skill uses.
TASK = """\
A developer machine reports:

    python3        3.12.3
    git            2.43.0
    OPENAI_BASE_URL  set
    MODEL            set
    OPENAI_API_KEY   set
    the runtime imported, and a test call to the endpoint returned a reply

Decide whether this machine is ready to run model-backed agent skills, and
fill in the contract. The unconfigured-failure demonstration exited 2, one
model call was made, and the reply had no contract violations.
"""


def rule(label: str) -> None:
    print(f"\n{label}\n{'-' * len(label)}")


def main() -> int:
    rule("[1] the runtime")
    print(f"runtime       : {rt.__name__}")
    print(f"resolved from : {pathlib.Path(rt.__file__).parent}")

    rule("[2] the configuration")
    base = os.environ.get("OPENAI_BASE_URL")
    print(f"endpoint      : {base or '(not set)'}")
    print(f"model         : {os.environ.get('MODEL') or '(not set)'}")
    # Presence, never the value. This output is pasted into issues.
    print(f"api key set   : {'yes' if os.environ.get('OPENAI_API_KEY') else 'no'}")
    if not base:
        print("\nNothing is configured, so there is nothing to prove. "
              "The refusal below is what every skill will print:\n")
        try:
            rt.backend()
        except rt.NoModelConfigured as e:
            print(e)
        return 2

    rule("[3] the failure you will hit first, on purpose")
    # A child process with the endpoint removed. Demonstrating the failure is
    # cheaper than describing it, and the reader now recognises the message.
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_BASE_URL"}
    env["PYTHONPATH"] = str(pathlib.Path(rt.__file__).parent)
    proc = subprocess.run(
        [sys.executable, "-c",
         "import cyber_commons_skill_runtime as r; r.announce_backend()"],
        capture_output=True, text=True, env=env)
    first = next((l for l in proc.stdout.splitlines() if l.strip()), "")
    print(f"exit code     : {proc.returncode}   (2 is correct)")
    print(f"first line    : {first}")

    rule("[4] one real model call")
    instance, problems, kind, model = rt.run_with_model(SKILL.read_text(), TASK)
    print(f"answered by   : {model}  ({kind})")
    print(f"violations    : {len(problems)}")
    for p in problems:
        print(f"   {p}")

    rule("[5] the contract, as this model filled it in")
    print(json.dumps(instance, indent=2, sort_keys=True))

    ready = bool(instance.get("ready")) and not problems
    print(f"\nready: {ready} — "
          f"{'this machine can run any skill in the commons' if ready else 'not yet; see above'}")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
