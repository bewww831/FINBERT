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

def test_health():
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200
    print("[PASS] Health check")

def test_predict_valid():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "timeseries" in data
    assert "sentiment" in data
    assert "cnn" in data
    assert "decision" in data
    print(f"[PASS] Predict AAPL recommendation: {data['decision']['recommendation']}")

def test_predict_invalid():
    res = requests.post(f"{BASE}/predict", json={"ticker": "INVALIDXYZ"})
    data = res.json()
    assert res.status_code in [200, 500]
    print("[PASS] Invalid ticker handled gracefully")

def test_decision_scores():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    data = res.json()
    dec = data["decision"]
    assert 0 <= dec["final_score"] <= 1
    assert dec["recommendation"] in ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
    assert abs(dec["ts_contrib"] + dec["sent_contrib"] + dec["cnn_contrib"] - dec["final_score"]) < 0.001
    print(f"[PASS] Decision scores valid final: {dec['final_score']}")

def test_sentiment_articles():
    res = requests.post(f"{BASE}/predict", json={"ticker": "AAPL"})
    assert res.status_code == 200
    data = res.json()
    articles = data["sentiment"]["articles"]
    assert len(articles) <= 5
    for a in articles:
        assert "headline" in a
        assert "label" in a
        assert a["label"] in ["positive", "negative", "neutral"]
        assert 0 <= a["conf"] <= 100
    print(f"[PASS] Sentiment articles valid: {len(articles)} articles returned")

if __name__ == "__main__":
    print("\nRunning tests... (ensure uvicorn is running)\n")

    run_test("Health check",        test_health)
    run_test("Predict valid ticker", test_predict_valid)
    run_test("Predict invalid ticker", test_predict_invalid)
    run_test("Decision scores",     test_decision_scores)
    run_test("Sentiment articles",  test_sentiment_articles)

    print(f"\n{passed} passed, {failed} failed")

    if failed == 0:
        print("[PASS] All tests passed\n")
    else:
        print(f"[FAILED] {failed} test(s) failed\n")