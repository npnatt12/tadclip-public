"""One Gemini policy for every script (2026-11-08 onboarding report: a 503 retried silently for minutes, a 429 looked like a hang).
503 / overloaded: one quick retry, then the next, lighter model. 429 per minute: one wait. 429 per day: stop at once with
the reset time; callers treat the shot as unchecked (flagged), never as passed.
Models: TADCLIP_GEMINI_MODELS="a,b" (default gemini-flash-latest, then gemini-flash-lite-latest)."""
import os
import time

MODELS = [m for m in os.environ.get("TADCLIP_GEMINI_MODELS", "gemini-flash-latest,gemini-flash-lite-latest").split(",") if m]
QUOTA_MSG = ("Gemini's free daily quota is used up (429). It resets at 15:00 Bangkok time; until then the Gemini checks are "
             "skipped and their shots are flagged as unchecked")


class Quota(RuntimeError):
    pass


def generate(client, contents, config=None, models=None, log=print):
    """client.models.generate_content with the policy above; returns the response or raises (Quota on the daily limit)."""
    last = None
    for m in models or MODELS:
        for wait in (0, 4):
            time.sleep(wait)
            try:
                return client.models.generate_content(model=m, contents=contents, config=config)
            except Exception as e:  # noqa: BLE001
                s, last = str(e), e
                if "429" in s or "RESOURCE_EXHAUSTED" in s:
                    if "PerDay" in s or "per day" in s.lower() or wait:
                        raise Quota(QUOTA_MSG) from e
                    time.sleep(30)  # per-minute limit: one wait, then the retry above
                elif not any(k in s for k in ("503", "UNAVAILABLE", "500", "INTERNAL", "overloaded", "high demand")):
                    raise  # a real error (bad key, bad request): no point retrying
        log(f"  (Gemini {m} is busy: trying the next model)")
    raise last


if __name__ == "__main__":  # the policy without the network
    class E(Exception):
        pass

    class C:
        def __init__(self, errs):
            self.errs, self.calls, self.models = list(errs), [], self

        def generate_content(self, model, contents, config):
            self.calls.append(model)
            if self.errs:
                raise E(self.errs.pop(0))
            return "ok:" + model

    time.sleep = lambda s: None
    c = C(["503 UNAVAILABLE", "503 UNAVAILABLE"])
    assert generate(c, "x", log=lambda *_: None) == "ok:gemini-flash-lite-latest" and len(c.calls) == 3
    try:
        generate(C(["429 RESOURCE_EXHAUSTED GenerateRequestsPerDayPerProjectPerModel"]), "x")
        raise SystemExit("daily 429 must stop at once")
    except Quota:
        pass
    c = C(["429 RESOURCE_EXHAUSTED per minute"])
    assert generate(c, "x") == "ok:gemini-flash-latest" and len(c.calls) == 2
    try:
        generate(C(["400 API key not valid"]), "x")
        raise SystemExit("a bad key must not retry")
    except E:
        pass
    print("ok")
