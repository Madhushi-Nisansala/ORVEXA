# AI Pipeline

The planned pipeline is: receive input, classify type, extract content, detect language, identify intent, run deterministic risk checks, retrieve sources when needed, validate structured model output, and generate confirmed next steps.

```mermaid
flowchart LR
  Input[User input] --> Classify[Classify input]
  Classify --> Extract[Extract text/content]
  Extract --> Language[Detect language]
  Language --> Rules[Deterministic risk checks]
  Rules --> Model[Provider abstraction]
  Model --> Validate[Strict schema validation]
  Validate --> Explain[Explain facts, limits, and actions]
```

No AI provider or credentials are configured in Phase 1.
