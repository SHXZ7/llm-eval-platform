# CI/CD for Model Behavior: How We Catch Prompt Regressions Before Production

## The Problem: Shipping Blind

Every week, engineering teams push new prompt versions to production hoping they work better. They don't. No one actually knows.

The honest truth: we have better testing for CSS changes than we do for LLM behavior. You ship a new prompt version, deploy it, wait 2 weeks, then realize—buried in support tickets—that technical support accuracy dropped 8%. By then, thousands of customers have been routed to the wrong category. Rollback. Incident report. Postmortem.

The core issue: **prompt changes are invisible**. They're configuration, not code. They don't go through CI/CD pipelines. They don't trigger test suites. They just... exist in a YAML file somewhere, and someone hopes they're better.

---

## Our Approach: CI/CD for Model Behavior

We treat LLM evaluation the same way we treat unit tests: **automated, fast, on every change**.

Here's the pipeline:

1. **Commit a new prompt** → YAML change in `app/llm/prompts/v3.yaml`
2. **CI/CD triggers** → GitHub Actions workflow runs
3. **Evaluate on golden dataset** → Run the new prompt against 100+ hand-verified test cases
4. **Compare results** → Calculate accuracy delta vs. baseline
5. **Check thresholds** → Warning if 3%+ drop, critical if 8%+ drop
6. **Detect slow drift** → Flag if last 7 runs average below 90% accuracy
7. **Send report** → HTML report + Slack alert with category breakdowns
8. **Block or merge** → Merge only if accuracy improves or stays stable

This means **every prompt change is tested automatically**. No guessing. No 2-week delays. You know before merging.

---

## Design Decision We're Proud Of: Separating Slow Drift from Per-Run Regressions

Here's where things get interesting—and where most teams get it wrong.

### The Naive Approach (Alert on Every Regression)

```python
if current_accuracy < previous_accuracy - 0.03:
    ALERT_ON_CALL()
```

**Problem:** This fires constantly. API flakiness, batch variance, randomness in LLM outputs—any single run might have noise. You get 100 alerts a month for things that don't matter. On-call gets burned out. Alerts stop being read.

### Our Approach: Two-Tier Detection

**Tier 1: Per-Run Comparison** (Immediate, but contextual)
- Compare new prompt directly to baseline
- Calculate accuracy delta
- If delta > 3%: warning (you see it, but it doesn't page)
- If delta > 8%: critical (page on-call)

**Tier 2: Slow Drift Detection** (The canary in the coal mine)
- Track last 7 runs in a moving window
- Calculate average accuracy over that window
- If moving average < 90%: drift detected
- **This is independent of per-run noise**

### Why This Matters

Scenario: Your prompt has a latent bug that only triggers on 2% of emails. Single run might miss it. But over 7 runs (700 emails), the effect becomes statistically clear. The moving average catches it even if each individual run looks "okay."

Conversely: Your API provider has a bad hour. Latency spikes. Accuracy dips 5% for one run. Per-run alert: warning. Slow drift: no drift detected (the moving average is still 91%). You don't page—it's noise.

### The Code

```python
# app/evals/drift_detector.py
def detect_slow_drift(historical_accuracies, thresholds):
    window_size = thresholds["drift_window_size"]  # 7
    drift_threshold = thresholds["drift_threshold"]  # 0.90
    
    recent_window = historical_accuracies[-window_size:]
    moving_average = mean(recent_window)
    
    drift_detected = moving_average < drift_threshold
    return {"drift_detected": drift_detected, "moving_average": moving_average}
```

**Why separate the logic?**
- **Accuracy delta** = how much did this change affect results
- **Slow drift** = are we gradually degrading across multiple runs
- Both matter, but for different reasons
- Mixing them causes alert fatigue or missed issues

This is production best practice: **measure signal AND trend**, not just threshold crossings.

---

## Other Design Decisions

### 1. **Environment Variable Overrides for Thresholds**
Containers should be configurable without rebuilding. Deploy the same image everywhere; change behavior with env vars.

```bash
docker run \
  -e WARNING_DELTA=0.05 \
  -e CRITICAL_DELTA=0.12 \
  llm-eval-platform
```

No rebuild. No config drift. Just env vars.

### 2. **Async Evaluation with Semaphores**
100 emails × network latency = 15+ minutes serially. We use `asyncio.Semaphore` to parallelize while respecting rate limits. ~3 minutes end-to-end.

### 3. **Category Breakdowns, Not Just Global Accuracy**
"Overall accuracy: 92%—looks good!" hides problems. Maybe technical support tanked to 78% but billing improved to 95%. You need the breakdown.

```python
breakdown = {
    "billing": 0.94,
    "technical": 0.78,
    "account": 0.91,
    "general": 0.88
}
```

Alert on the regression. Make it visible. Force the fix.

### 4. **Slack Alert + HTML Report Split**
- **Slack**: "CRITICAL: accuracy dropped 8%. Tech support: 78%. Check report."
- **HTML Report**: Full precision. Category tables, historical trends, per-case diffs, easy to audit.

Slack makes you aware. HTML makes you confident you're fixing the right thing.

### 5. **Versioned Prompts as Data, Not Code**
Prompts live in `app/llm/prompts/v{1,2,3}.yaml` with version, description, few-shot examples, and config. Non-engineers can iterate. Changes are tracked in git. Easy to compare versions side-by-side.

---

## What This Buys You

✅ **Catch regressions before they hit production**
- New prompt version? Evaluate immediately. Know if it's better within minutes.

✅ **Confidence in changes**
- Did my prompt tweak actually help? Data says yes/no. No guessing.

✅ **Detect slow degradation**
- Maybe one run is noise, but a 7-run trend is truth. Catch gradual drift before it matters.

✅ **Category-specific insights**
- Know exactly which email types are affected. Technical support down? Fix it there, not globally.

✅ **Production agility**
- Tune thresholds and report URLs without rebuilding. Deploy once, configure everywhere.

✅ **No false alarms**
- Smart two-tier detection prevents on-call burnout. Real issues get real alerts.

---

## Next: Try It

1. Add 5–10 test cases to `data/golden_dataset_small.json` (real emails from your domain)
2. Tweak a prompt in `app/llm/prompts/v2.yaml`
3. Run `python main.py`
4. Check the HTML report
5. Deploy with confidence

That's CI/CD for model behavior. That's how you ship LLM products without flying blind.
