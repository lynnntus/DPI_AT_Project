"""Unit tests for smart wait/timeout feature."""
import sys
import time
from unittest.mock import patch

def test_parse_timeout():
    print("=== Test 1: _parse_timeout - valid values ===")
    from ui_runner import _parse_timeout, _DEFAULT_TIMEOUT
    assert _parse_timeout("10") == 10.0
    assert _parse_timeout("5") == 5.0
    assert _parse_timeout("1") == 1.0
    assert _parse_timeout("0.5") == _DEFAULT_TIMEOUT, "< 1 should fallback"
    assert _parse_timeout("0") == _DEFAULT_TIMEOUT, "0 should fallback"
    assert _parse_timeout("-1") == _DEFAULT_TIMEOUT, "negative should fallback"
    assert _parse_timeout("") == _DEFAULT_TIMEOUT, "empty should fallback"
    assert _parse_timeout(None) == _DEFAULT_TIMEOUT, "None should fallback"
    assert _parse_timeout("abc") == _DEFAULT_TIMEOUT, "non-numeric should fallback"
    print("  PASS - all parse cases correct")


def test_match_first_try():
    print("=== Test 2: _wait_and_verify - match on first try ===")
    with patch('ui_runner.capture_check_region') as mock_cap:
        mock_cap.return_value = {
            'Label_ID': 'TC001', 'Expected': 'Hello',
            'Detected': 'Hello', 'Match': '✅', 'ImagePath': 'x.jpg'
        }
        from ui_runner import _wait_and_verify
        start = time.time()
        r = _wait_and_verify({'TC No.': 'TC001'}, 'folder', 5)
        elapsed = time.time() - start
        assert r['Match'] == '✅'
        assert elapsed < 1, f'Immediate match took {elapsed:.1f}s'
        assert mock_cap.call_count == 1
        print(f'  PASS - match first try, {elapsed:.2f}s, 1 call')


def test_match_after_retries():
    print("=== Test 3: _wait_and_verify - match after retries ===")
    with patch('ui_runner.capture_check_region') as mock_cap:
        fail_r = {'Label_ID': 'TC001', 'Expected': 'Hi', 'Detected': 'X', 'Match': '❌', 'ImagePath': 'x.jpg'}
        pass_r = {'Label_ID': 'TC001', 'Expected': 'Hi', 'Detected': 'Hi', 'Match': '✅', 'ImagePath': 'x.jpg'}
        mock_cap.side_effect = [fail_r, fail_r, pass_r]
        from ui_runner import _wait_and_verify
        start = time.time()
        r = _wait_and_verify({'TC No.': 'TC001'}, 'folder', 10)
        elapsed = time.time() - start
        assert r['Match'] == '✅'
        assert mock_cap.call_count == 3
        print(f'  PASS - match after 3 calls, {elapsed:.2f}s')


def test_timeout():
    print("=== Test 4: _wait_and_verify - timeout ===")
    with patch('ui_runner.capture_check_region') as mock_cap:
        fail_r = {'Label_ID': 'TC001', 'Expected': 'Hi', 'Detected': 'Wrong', 'Match': '❌', 'ImagePath': 'x.jpg'}
        mock_cap.return_value = fail_r
        from ui_runner import _wait_and_verify
        start = time.time()
        r = _wait_and_verify({'TC No.': 'TC001'}, 'folder', 2)
        elapsed = time.time() - start
        assert r['Match'] == '❌'
        assert elapsed >= 2.0, f'Timeout too early: {elapsed:.1f}s'
        assert elapsed < 4.0, f'Timeout too late: {elapsed:.1f}s'
        print(f'  PASS - timeout after {elapsed:.2f}s, {mock_cap.call_count} retries')


def test_only_verify_retried():
    print("=== Test 5: action not retried, only verify ===")
    with patch('ui_runner.capture_check_region') as mock_cap:
        fail_r = {'Label_ID': 'TC001', 'Expected': 'Hi', 'Detected': 'X', 'Match': '❌', 'ImagePath': 'x.jpg'}
        pass_r = {'Label_ID': 'TC001', 'Expected': 'Hi', 'Detected': 'Hi', 'Match': '✅', 'ImagePath': 'x.jpg'}
        mock_cap.side_effect = [fail_r, pass_r]
        from ui_runner import _wait_and_verify
        r = _wait_and_verify({'TC No.': 'TC001'}, 'folder', 5)
        assert r['Match'] == '✅'
        assert mock_cap.call_count == 2, "Only capture_check_region retried, not the action"
        print(f'  PASS - only verify retried ({mock_cap.call_count} calls)')


if __name__ == '__main__':
    test_parse_timeout()
    test_match_first_try()
    test_match_after_retries()
    test_timeout()
    test_only_verify_retried()
    print()
    print("ALL 5 UNIT TESTS PASSED")
