# Vision Model — CORRECTION

**Date:** 2026-04-21
**Status:** ✅ RESOLVED — No action needed

## The Issue
DMob reported vision was "text-only, no vision" and suggested switching models.

## The Reality
Vision is ALREADY configured in config.yaml:

```yaml
auxiliary:
  vision:
    provider: nous
    model: xiaomi/mimo-v2-omni
```

MiMo V2 Omni is the multimodal variant — handles images natively through the Nous subscription. No model switch needed.

## Lesson Learned
Always check `config.yaml` before reporting missing capabilities. The `auxiliary.vision` section was already set up.
