#!/usr/bin/env python3
"""
Dry-run test for detection confidence
Uses mock detection results
"""

def test_detection_dryrun():
    # Mock detection output (what we expect from DETECT-001)
    mock_detection_results = [
        {"file": "ButtonWidget.tsx", "detected": "top_level_widgets", "confidence": 90, "expected": "top_level_widgets"},
        {"file": "UserManager.ts", "detected": "stateful_containers", "confidence": 85, "expected": "stateful_containers"},
        {"file": "AppStore.ts", "detected": "global_state", "confidence": 92, "expected": "global_state"},
        {"file": "useAuth.ts", "detected": "custom_hooks", "confidence": 88, "expected": "custom_hooks"},
        {"file": "APIClient.ts", "detected": "api_clients", "confidence": 95, "expected": "api_clients"},
        {"file": "helper.py", "detected": "utility_modules", "confidence": 75, "expected": "utility_modules"},  # Below threshold
    ]

    # Test: Check confidence threshold
    passed = 0
    failed = 0

    print("Testing detection confidence (80% threshold):\n")

    for result in mock_detection_results:
        is_correct = result["detected"] == result["expected"]
        is_confident = result["confidence"] >= 80

        if is_correct and is_confident:
            print(f"[PASS] {result['file']:30s} confidence: {result['confidence']}%")
            passed += 1
        else:
            reason = "wrong type" if not is_correct else "confidence below 80%"
            print(f"[FAIL] {result['file']:30s} {reason}: {result['confidence']}%")
            failed += 1

    # Overall result
    accuracy = (passed / len(mock_detection_results)) * 100
    print(f"\nDetection accuracy: {accuracy:.1f}% ({passed}/{len(mock_detection_results)})")
    print(f"Target: 80%+ accuracy")

    return accuracy >= 80  # Need 80% accuracy

# Run dry-run
if __name__ == "__main__":
    result = test_detection_dryrun()
    print(f"\nDetection test dry-run: {'SUCCESS' if result else 'FAILED'}")
    exit(0 if result else 1)
