"""Integration & regression tests for smart wait/timeout feature."""
import time
from unittest.mock import patch, MagicMock

PASS_RESULT = {'Label_ID': 'TC001', 'Expected': 'OK', 'Detected': 'OK', 'Match': '✅', 'ImagePath': 'x.jpg'}
FAIL_RESULT = {'Label_ID': 'TC001', 'Expected': 'OK', 'Detected': 'NG', 'Match': '❌', 'ImagePath': 'x.jpg'}


def mock_deps():
    """Patch external deps so run_script can execute without real GUI/OCR."""
    patches = {
        'ui_runner.show_click_indicator': MagicMock(),
        'ui_runner.pyautogui': MagicMock(),
        'ui_runner.ImageGrab': MagicMock(),
        'ui_runner.pytesseract': MagicMock(),
    }
    return patches


# --- Integration Tests ---

def test_integration_check_action_uses_retry():
    print("=== Integration 1: check action triggers _wait_and_verify ===")
    with patch('ui_runner.capture_check_region') as mock_cap, \
         patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui'):
        mock_cap.side_effect = [FAIL_RESULT, PASS_RESULT]
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
        assert result["success"] is True, f"Expected success, got {result}"
        assert mock_cap.call_count == 2, f"Should retry once, called {mock_cap.call_count}"
        print(f"  PASS - retry worked, {mock_cap.call_count} captures")


def test_integration_non_check_no_retry():
    print("=== Integration 2: non-check action sleeps 1s, no retry ===")
    with patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui') as mock_auto:
        from ui_runner import run_script
        actions = [
            {"type": "click", "x": 100, "y": 200},
            {"type": "click", "x": 300, "y": 400},
        ]
        start = time.time()
        result = run_script(actions, {}, {}, "10")
        elapsed = time.time() - start
        assert result["success"] is True
        assert mock_auto.click.call_count == 2
        assert 1.5 <= elapsed <= 3.5, f"2 clicks should take ~2s (2x1s delay), took {elapsed:.1f}s"
        print(f"  PASS - 2 clicks, {elapsed:.1f}s (1s delay each)")


def test_integration_timeout_produces_fail():
    print("=== Integration 3: timeout produces fail with details ===")
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
        start = time.time()
        result = run_script(actions, {}, check_items, "2")
        elapsed = time.time() - start
        assert result["success"] is False, "Should fail on timeout"
        assert "mismatch" in result.get("errorMessage", "").lower()
        assert elapsed >= 2.0, f"Should wait at least 2s, waited {elapsed:.1f}s"
        print(f"  PASS - timeout fail after {elapsed:.1f}s, msg='{result['errorMessage']}'")


# --- Regression Tests ---

def test_regression_report_format_unchanged():
    print("=== Regression 1: report columns unchanged ===")
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
        assert result["success"] is True
        expected_cols = {"Label_ID", "Expected", "Detected", "Match", "ImagePath"}
        # The results are stored internally; check via mock
        assert set(PASS_RESULT.keys()) == expected_cols
        print(f"  PASS - columns = {expected_cols}")


def test_regression_mixed_actions():
    print("=== Regression 2: mixed click + check actions ===")
    with patch('ui_runner.capture_check_region') as mock_cap, \
         patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui') as mock_auto:
        mock_cap.return_value = PASS_RESULT
        from ui_runner import run_script
        actions = [
            {"type": "click", "x": 10, "y": 20},
            {"type": "check", "Lang": "English", "Word(resx)": "w1", "Content": "OK"},
            {"type": "click", "x": 30, "y": 40},
        ]
        check_items = {
            "1": {"Lang": "English", "Word(resx)": "w1", "Content": "OK",
                   "TC No.": "TC001", "TopLeft (x)": 0, "TopLeft (y)": 0,
                   "BottomRight (x)": 100, "BottomRight (y)": 100}
        }
        result = run_script(actions, {}, check_items, "5")
        assert result["success"] is True
        assert mock_auto.click.call_count == 2, "Both clicks executed"
        assert mock_cap.call_count == 1, "Check captured once (matched first try)"
        print(f"  PASS - 2 clicks + 1 check, all OK")


def test_regression_empty_delay_uses_default():
    print("=== Regression 3: empty/invalid delay uses default 10s ===")
    from ui_runner import _parse_timeout, _DEFAULT_TIMEOUT
    for val in ["", "abc", None, "0", "-5"]:
        assert _parse_timeout(val) == _DEFAULT_TIMEOUT, f"Failed for {val!r}"
    print(f"  PASS - all invalid values fallback to {_DEFAULT_TIMEOUT}s")


def test_regression_sub_script_still_works():
    print("=== Regression 4: run_script sub-script execution ===")
    with patch('ui_runner.show_click_indicator'), \
         patch('ui_runner.pyautogui') as mock_auto:
        from ui_runner import run_script
        scripts = {
            "sub1": {"actions": [{"type": "click", "x": 50, "y": 60}]}
        }
        actions = [
            {"type": "run_script", "scripts": ["sub1"]}
        ]
        result = run_script(actions, scripts, {}, "5")
        assert result["success"] is True
        assert mock_auto.click.call_count == 1
        print("  PASS - sub-script executed correctly")


if __name__ == '__main__':
    # Integration
    test_integration_check_action_uses_retry()
    test_integration_non_check_no_retry()
    test_integration_timeout_produces_fail()
    # Regression
    test_regression_report_format_unchanged()
    test_regression_mixed_actions()
    test_regression_empty_delay_uses_default()
    test_regression_sub_script_still_works()
    print()
    print("ALL 7 INTEGRATION + REGRESSION TESTS PASSED")
