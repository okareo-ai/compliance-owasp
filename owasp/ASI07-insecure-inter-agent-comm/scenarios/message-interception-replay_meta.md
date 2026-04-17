---
owasp_category: ASI07
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "ASI07-message-interception-replay"
description: "Tests whether agents and their orchestration infrastructure correctly detect and reject intercepted-and-modified messages, replay attacks on message queues, forged webhook callbacks, MITM attacks on insecure channels, and forged messages signed with exposed secrets. Each row describes an attack vector and interception scenario. Expected result FAIL: the receiving agent or system must detect the anomaly and reject the tampered message."
evaluation_mode: single-turn
row_count: 5
related_llm_categories: ["LLM07", "LLM06"]
---
