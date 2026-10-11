# Publication provenance and verification

This repository publishes the existing Agentic RAG Business Insight project and the current source repairs supplied in the local working directory.

## Provenance

- Original working project: `Agentic_RAG_Business-Insight-Analysis`.
- Original upstream: [WachirawitThaneesan/Agentic_RAG_Business-Insight-Analysis](https://github.com/WachirawitThaneesan/Agentic_RAG_Business-Insight-Analysis).
- Source branch: `auto1`; source HEAD at preparation: `5722b7d`.
- Original author identities and real commit dates are retained. Historical hashes change where publication filtering removes private runtime inputs.
- The supplied uncommitted source repairs are integrated in a new publication commit dated 11 October 2026. The original working directory and its remote were not changed.

The publication history omits user-uploaded PDFs/screenshots, runtime databases, browser profiles, logs, scratch directories, and credential files. It keeps the code, test fixtures, readable reports, and the selected research-evidence package. Filtering applies to the published branch's history, not only its latest directory listing. Other local staging branches are not published.

## Verification

96 focused checks passed both in the original working project and in this isolated publication checkout:

```powershell
python -m pytest backend/services/tests/test_api_fallback.py backend/services/tests/test_completed_upload_reuse.py backend/services/tests/test_sql_page_context.py backend/services/tests/test_warehouse_status.py backend/services/tests/test_answer_capture.py backend/services/tests/test_agent_evidence_budget.py backend/services/tests/test_runtime_cell_provenance.py backend/eval/tests/test_bounded_cloud_meter.py -q
```

These checks cover the recently repaired API fallback, completed-upload reuse, SQL page context, warehouse status, answer capture, evidence budget, cell provenance, and cloud metering behavior. They do not rerun cloud OCR, the full 498-question evaluation, or end-to-end ingestion against external services. There is an existing Pydantic class-config deprecation warning.

## Recorded evaluation scope

The [498-question research report](GEMINI_RAG_FULL498_REPORT_2026-10-08.md) records an 8 October 2026 development evaluation with AI review. It predates the latest publication repairs. Eight individual conservative metrics ranged from 85.96% to 96.69%; the stricter complete-answer contract was 302/498 (60.64%), and strict numerical relationships were 18/102 (17.65%). These are distinct measures, not one overall accuracy percentage. Independent human review and generalization to unseen reports remain open.

The [portfolio showcase](https://jakkrapat-project-lab.happy-bud-2264.chatgpt.site/#rag) displays recorded screenshots, architecture, source links, and the evaluation scope. It does not expose the FastAPI backend or forward visitor documents to cloud models.
