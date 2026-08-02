SHELL := /bin/bash
REPO_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
WRAPPER  := $(REPO_DIR)/scripts/run_vulnbench.sh
CRON_LINE := 0 6 * * * /usr/bin/env bash $(WRAPPER)

.PHONY: build questions bench verify schedule schedule-show unschedule

build:
	.venv/bin/python ingest/build_datasource.py --only secllmholmes terragoat

questions:
	.venv/bin/python questions/loader.py

bench:
	.venv/bin/python bench/run_benchmark.py \
		--findings $${FINDINGS:-data/mantis_findings.sample.jsonl} \
		--harness mantis --run-id manual-$$(date +%F) \
		--gt-source secllmholmes-handcrafted

verify:
	.venv/bin/python bench/run_benchmark.py \
		--findings data/mantis_findings.sample.jsonl \
		--harness mantis --run-id verify \
		--gt-source secllmholmes-handcrafted --min-acc 0.80

# Install the nightly cron entry idempotently: existing crontab lines are kept,
# any previous run_vulnbench.sh line is replaced, never duplicated.
schedule:
	@( crontab -l 2>/dev/null | grep -vF "run_vulnbench.sh" ; echo "$(CRON_LINE)" ) | crontab -
	@echo "installed:" ; crontab -l | grep -F "run_vulnbench.sh"

schedule-show:
	@echo "$(CRON_LINE)"

unschedule:
	@( crontab -l 2>/dev/null | grep -vF "run_vulnbench.sh" ) | crontab - || true
	@echo "removed vulnbench cron entry (if present)"
