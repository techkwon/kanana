# QA case layout

Eduflow QA cases are grouped under `qa/cases/<command>/<domain>.json`.

## File shape

```json
{
  "domain": "math",
  "command": "explain",
  "cases": [
    {
      "id": "explain-001",
      "topic": "피타고라스 정리",
      "learner_level": "middle",
      "expected_keywords": ["직각삼각형", "빗변"],
      "forbidden_keywords": ["!!", "The "]
    }
  ]
}
```

## Notes

- Shared metadata at the file level is merged into each case.
- `group` is derived from the relative file path without `.json`.
- `source_path` is recorded in reports so failures can be traced back to the source file quickly.
- You can run the whole tree or point `--cases` at a single grouped file for focused QA.
