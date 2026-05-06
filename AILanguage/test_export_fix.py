"""Unit tests for export Excel fix — run_script() returns results."""
from unittest.mock import patch, MagicMock

PASS_RESULT = {'Label_ID': 'TC001', 'Expected': 'OK', 'Detected': 'OK', 'Match': '✅', 'ImagePath': 'x.jpg'}
FAIL_RESULT = {'Label_ID': 'TC001', 'Expected': 'OK', 'Detected': 'NG', 'Match': '❌', 'ImagePath': 'x.jpg'}


def test_success_returns_results_key():
    print("=== Export 1: success path returns 'results' key ===")
    with patch('ui_runner.capture_check_region') as mock_cap, \
         patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui'):
        mock_cap.return_value = PASS_RESULT
        from ui_runner import run_script
        actions = [
            {"type": "check", "Lang": "English", "Word(resx)": "w1", "Content": "OK"}
        ]
        check_items = {
            "1": {"Lang": "English", "Word(resx)": "w1", "Content": "OK",
                   "TC No.": "TC001", "TopLeft (x)": 0, "TopLeft (y)": 0,
                   "BottomRight (x)": 100, "BottomRight (y)": 100}
        }
        result = run_script(actions, {}, check_items, "5")
        assert "results" in result, f"Missing 'results' key: {result.keys()}"
        assert isinstance(result["results"], list)
        assert len(result["results"]) == 1
        assert result["results"][0]["Label_ID"] == "TC001"
        print(f"  PASS - results key present, {len(result['results'])} item(s)")


def test_fail_result_returns_results_key():
    print("=== Export 2: _fail_result returns 'results' key ===")
    from ui_runner import _fail_result
    r = _fail_result("step1", "error msg")
    assert "results" in r, f"Missing 'results' key: {r.keys()}"
    assert r["results"] == [], f"Default should be [], got {r['results']}"
    print("  PASS - _fail_result has results=[]")


def test_fail_result_carries_partial_results():
    print("=== Export 3: _fail_result carries partial results ===")
    from ui_runner import _fail_result
    partial = [PASS_RESULT]
    r = _fail_result("step2", "error", results=partial)
    assert r["results"] == partial
    assert len(r["results"]) == 1
    print(f"  PASS - partial results carried, {len(r['results'])} item(s)")


def test_fail_path_returns_partial_results():
    print("=== Export 4: run_script fail path carries partial results ===")
    with patch('ui_runner.capture_check_region') as mock_cap, \
         patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui'):
        mock_cap.return_value = FAIL_RESULT
        from ui_runner import run_script
        actions = [
            {"type": "check", "Lang": "English", "Word(resx)": "w1", "Content": "OK"}
        ]
        check_items = {
            "1": {"Lang": "English", "Word(resx)": "w1", "Content": "OK",
                   "TC No.": "TC001", "TopLeft (x)": 0, "TopLeft (y)": 0,
                   "BottomRight (x)": 100, "BottomRight (y)": 100}
        }
        result = run_script(actions, {}, check_items, "2")
        assert result["success"] is False
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["Match"] == "❌"
        print(f"  PASS - fail path has {len(result['results'])} partial result(s)")


def test_no_check_returns_empty_results():
    print("=== Export 5: no check actions returns empty results ===")
    with patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui'):
        from ui_runner import run_script
        actions = [
            {"type": "click", "x": 10, "y": 20},
        ]
        result = run_script(actions, {}, {}, "5")
        assert result["success"] is True
        assert "results" in result
        assert result["results"] == []
        print("  PASS - empty results for non-check script")


def test_report_columns_unchanged():
    print("=== Export 6: report columns format unchanged ===")
    with patch('ui_runner.capture_check_region') as mock_cap, \
         patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui'):
        mock_cap.return_value = PASS_RESULT
        from ui_runner import run_script
        actions = [
            {"type": "check", "Lang": "English", "Word(resx)": "w1", "Content": "OK"}
        ]
        check_items = {
            "1": {"Lang": "English", "Word(resx)": "w1", "Content": "OK",
                   "TC No.": "TC001", "TopLeft (x)": 0, "TopLeft (y)": 0,
                   "BottomRight (x)": 100, "BottomRight (y)": 100}
        }
        result = run_script(actions, {}, check_items, "5")
        expected_cols = {"Label_ID", "Expected", "Detected", "Match", "ImagePath"}
        actual_cols = set(result["results"][0].keys())
        assert actual_cols == expected_cols, f"Columns mismatch: {actual_cols}"
        print(f"  PASS - columns = {expected_cols}")


if __name__ == '__main__':
    test_success_returns_results_key()
    test_fail_result_returns_results_key()
    test_fail_result_carries_partial_results()
    test_fail_path_returns_partial_results()
    test_no_check_returns_empty_results()
    test_report_columns_unchanged()
    print()
    print("ALL 6 EXPORT FIX TESTS PASSED")
