import time
import requests

BASE = "http://127.0.0.1:8000"

passed = 0
failed = 0

def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
    except AssertionError as e:
        print(f"[FAILED] {name}: assertion error: {e}")
        failed += 1
    except requests.exceptions.ConnectionError:
        print(f"[FAILED] {name}: could not connect to server")
        failed += 1
    except KeyError as e:
        print(f"[FAILED] {name}: missing key in response: {e}")
        failed += 1
    except Exception as e:
        print(f"[FAILED] {name}: unexpected error: {e}")
        failed += 1

# ── HEALTH ────────────────────────────────────────────────────

def test_health():
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200
    print("[PASS] Health check")

def test_health_response_time():
    start = time.time()
    requests.get(f"{BASE}/health")
    elapsed = time.time() - start
    assert elapsed < 1.0, f"health took {elapsed:.2f}s"
    print(f"[PASS] Health response time: {elapsed:.3f}s")

def test_health_models_listed():
    res = requests.get(f"{BASE}/health")
    data = res.json()
    assert "models" in data
    assert "xgboost"  in data["models"]
    assert "finbert"  in data["models"]
    assert "cnn"      in data["models"]
    print("[PASS] Health lists all three models")

# ── PREDICT — VALID ───────────────────────────────────────────

def test_predict_valid():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "timeseries" in data
    assert "sentiment"  in data
    assert "cnn"        in data
    assert "decision"   in data
    print(f"[PASS] Predict AAPL recommendation: {data['decision']['recommendation']}")

def test_predict_response_time():
    start = time.time()
    requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    elapsed = time.time() - start
    assert elapsed < 60.0, f"predict took {elapsed:.2f}s — exceeded 60s limit"
    print(f"[PASS] Predict response time: {elapsed:.1f}s")

def test_predict_response_structure():
    res  = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    data = res.json()
    # top-level keys
    for key in ["ticker", "status", "timeseries", "sentiment", "cnn", "decision"]:
        assert key in data, f"missing top-level key: {key}"
    # decision keys
    for key in ["ts_score", "sent_score", "cnn_score", "ts_contrib", "sent_contrib",
                "cnn_contrib", "final_score", "recommendation", "emoji", "explanation"]:
        assert key in data["decision"], f"missing decision key: {key}"
    # timeseries keys
    for key in ["buy", "hold", "sell", "label"]:
        assert key in data["timeseries"], f"missing timeseries key: {key}"
    # sentiment keys
    for key in ["positive", "neutral", "negative", "label", "headline", "articles"]:
        assert key in data["sentiment"], f"missing sentiment key: {key}"
    # cnn keys
    for key in ["bullish", "neutral", "bearish", "label"]:
        assert key in data["cnn"], f"missing cnn key: {key}"
    print("[PASS] Response structure complete — all keys present")

# ── PREDICT — INPUT EDGE CASES ────────────────────────────────

def test_predict_invalid():
    res  = requests.post(f"{BASE}/predict", json={"ticker": "INVALIDXYZ"})
    data = res.json()
    assert res.status_code in [200, 500]
    print("[PASS] Invalid ticker handled gracefully")

def test_predict_lowercase():
    res  = requests.post(f"{BASE}/predict", json={"ticker": "aapl"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["ticker"] == "AAPL"
    print("[PASS] Lowercase ticker normalised correctly")

def test_predict_with_spaces():
    res  = requests.post(f"{BASE}/predict", json={"ticker": " AAPL "})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["ticker"] == "AAPL"
    print("[PASS] Ticker with surrounding spaces handled correctly")

def test_predict_empty_ticker():
    res  = requests.post(f"{BASE}/predict", json={"ticker": ""})
    assert res.status_code in [200, 400, 422, 500]
    print("[PASS] Empty ticker handled gracefully")

# ── PROBABILITY DISTRIBUTIONS ─────────────────────────────────

def test_timeseries_probabilities_sum():
    res  = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    ts   = res.json()["timeseries"]
    total = ts["buy"] + ts["hold"] + ts["sell"]
    assert abs(total - 1.0) < 0.01, f"XGBoost probs sum to {total:.5f}, expected ~1.0"
    print(f"[PASS] XGBoost probabilities sum to ~1.0 ({total:.5f})")

def test_sentiment_probabilities_sum():
    res   = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    sent  = res.json()["sentiment"]
    total = sent["positive"] + sent["neutral"] + sent["negative"]
    assert abs(total - 1.0) < 0.01, f"FinBERT probs sum to {total:.5f}, expected ~1.0"
    print(f"[PASS] FinBERT probabilities sum to ~1.0 ({total:.5f})")

def test_cnn_probabilities_sum():
    res   = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    cnn   = res.json()["cnn"]
    total = cnn["bullish"] + cnn["neutral"] + cnn["bearish"]
    assert abs(total - 1.0) < 0.01, f"CNN probs sum to {total:.5f}, expected ~1.0"
    print(f"[PASS] CNN probabilities sum to ~1.0 ({total:.5f})")

# ── DECISION ENGINE ───────────────────────────────────────────

def test_decision_scores():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    data = res.json()
    dec  = data["decision"]
    assert 0 <= dec["final_score"] <= 1
    assert dec["recommendation"] in ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
    assert abs(dec["ts_contrib"] + dec["sent_contrib"] + dec["cnn_contrib"] - dec["final_score"]) < 0.001
    print(f"[PASS] Decision scores valid final: {dec['final_score']}")

def test_decision_score_ranges():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    dec = res.json()["decision"]
    assert 0 <= dec["ts_score"]   <= 1, "ts_score out of range"
    assert 0 <= dec["sent_score"] <= 1, "sent_score out of range"
    assert 0 <= dec["cnn_score"]  <= 1, "cnn_score out of range"
    assert dec["ts_contrib"]   <= 0.525, "ts_contrib exceeds its weight"
    assert dec["sent_contrib"] <= 0.325, "sent_contrib exceeds its weight"
    assert dec["cnn_contrib"]  <= 0.150, "cnn_contrib exceeds its weight"
    print("[PASS] All scores and contributions within valid ranges")

def test_decision_has_explanation():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    dec = res.json()["decision"]
    assert isinstance(dec["explanation"], str)
    assert len(dec["explanation"]) > 10
    assert isinstance(dec["emoji"], str)
    assert len(dec["emoji"]) > 0
    print("[PASS] Decision explanation and emoji present")

# ── SENTIMENT ARTICLES ────────────────────────────────────────

def test_sentiment_articles():
    res      = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    articles = res.json()["sentiment"]["articles"]
    assert len(articles) <= 5
    for a in articles:
        assert "headline" in a
        assert "label"    in a
        assert a["label"] in ["positive", "negative", "neutral"]
        assert 0 <= a["conf"] <= 100
    print(f"[PASS] Sentiment articles valid: {len(articles)} articles returned")

def test_sentiment_articles_have_url():
    res      = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    articles = res.json()["sentiment"]["articles"]
    for a in articles:
        assert "url" in a, "article missing url field"
    print(f"[PASS] Sentiment articles all contain url field")

# ── PRICES ENDPOINT ───────────────────────────────────────────

def test_prices_endpoint():
    res  = requests.get(f"{BASE}/prices")
    assert res.status_code == 200
    data = res.json()
    assert "prices" in data
    assert len(data["prices"]) > 0
    print(f"[PASS] Prices endpoint returned {len(data['prices'])} tickers")

def test_prices_structure():
    res    = requests.get(f"{BASE}/prices")
    prices = res.json()["prices"]
    for p in prices:
        assert "ticker" in p,           "price item missing ticker"
        assert "price"  in p,           "price item missing price"
        assert "change" in p,           "price item missing change"
        assert p["price"] > 0,          f"{p['ticker']} price is not positive"
        assert isinstance(p["change"], float), f"{p['ticker']} change is not a float"
    print(f"[PASS] Prices structure valid for all {len(prices)} tickers")

# ── MULTIPLE TICKERS ──────────────────────────────────────────

def test_predict_multiple_tickers():
    tickers = ["MSFT", "TSLA", "NVDA"]
    for ticker in tickers:
        res  = requests.post(f"{BASE}/predict", json={"ticker": ticker})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["ticker"] == ticker
        assert data["decision"]["recommendation"] in ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
        print(f"[PASS] Predict {ticker}: {data['decision']['recommendation']}")

# ── RUNNER ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nRunning tests... (ensure uvicorn is running)\n")

    print("── Health ──")
    run_test("Health check",               test_health)
    run_test("Health response time",       test_health_response_time)
    run_test("Health models listed",       test_health_models_listed)

    print("\n── Predict — Valid ──")
    run_test("Predict valid ticker",       test_predict_valid)
    run_test("Predict response time",      test_predict_response_time)
    run_test("Predict response structure", test_predict_response_structure)

    print("\n── Predict — Edge Cases ──")
    run_test("Predict invalid ticker",     test_predict_invalid)
    run_test("Predict lowercase ticker",   test_predict_lowercase)
    run_test("Predict ticker with spaces", test_predict_with_spaces)
    run_test("Predict empty ticker",       test_predict_empty_ticker)

    print("\n── Probability Distributions ──")
    run_test("XGBoost probabilities sum",  test_timeseries_probabilities_sum)
    run_test("FinBERT probabilities sum",  test_sentiment_probabilities_sum)
    run_test("CNN probabilities sum",      test_cnn_probabilities_sum)

    print("\n── Decision Engine ──")
    run_test("Decision scores",            test_decision_scores)
    run_test("Decision score ranges",      test_decision_score_ranges)
    run_test("Decision explanation",       test_decision_has_explanation)

    print("\n── Sentiment Articles ──")
    run_test("Sentiment articles valid",   test_sentiment_articles)
    run_test("Sentiment articles have url",test_sentiment_articles_have_url)

    print("\n── Prices Endpoint ──")
    run_test("Prices endpoint",            test_prices_endpoint)
    run_test("Prices structure",           test_prices_structure)

    print("\n── Multiple Tickers ──")
    run_test("Predict multiple tickers",   test_predict_multiple_tickers)

    print(f"\n{passed} passed, {failed} failed")

    if failed == 0:
        print("[PASS] All tests passed\n")
    else:
        print(f"[FAILED] {failed} test(s) failed\n")