# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-11-08

### Added

- `assess_write` / `should_write`: pure write gate covering empty input,
  length bounds, line count, error dumps, link-only text, questions and
  chitchat. Returns the verdict plus the metrics that produced it.
- `assess_attribution`: flags relation-subject and pet-subject facts without
  rewriting them.
- `safe_assess_write`: fail-open wrapper that always logs the exception.
- `MemoryHygieneConfig` for thresholds and known pet names.
- 27 tests, including the negative examples that must not be rejected.
