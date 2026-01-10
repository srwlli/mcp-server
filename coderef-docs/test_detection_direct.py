#!/usr/bin/env python3
"""
Direct test of detection module - bypasses slash command routing issue.

Tests the 3-stage detection algorithm implementation directly.
"""

import sys
from pathlib import Path

# Add generators directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.detection_module import ElementTypeDetector, DetectionResult

def test_detection_confidence():
    """Test detection on 20 element types with confidence scoring."""

    # Initialize detector
    detector = ElementTypeDetector()

    # Test cases for all 20 element types (from element-type-mapping.json)
    test_cases = [
        # Priority 1 (P1) - 5 types
        {
            "filename": "ButtonWidget.tsx",
            "code_sample": "export const ButtonWidget: React.FC = () => { ... }",
            "expected_type": "top_level_widgets",
            "priority": 1
        },
        {
            "filename": "UserManager.ts",
            "code_sample": "class UserManager { private state: User[] = []; ... }",
            "expected_type": "stateful_containers",
            "priority": 1
        },
        {
            "filename": "AppStore.ts",
            "code_sample": "const appStore = createStore({ ... })",
            "expected_type": "global_state",
            "priority": 1
        },
        {
            "filename": "useAuth.ts",
            "code_sample": "export function useAuth() { return useState(...) }",
            "expected_type": "custom_hooks",
            "priority": 1
        },
        {
            "filename": "APIClient.ts",
            "code_sample": "class APIClient { async fetch() { ... } }",
            "expected_type": "api_clients",
            "priority": 1
        },

        # Priority 2 (P2) - 5 types
        {
            "filename": "User.ts",
            "code_sample": "interface User { id: string; name: string; }",
            "expected_type": "data_models",
            "priority": 2
        },
        {
            "filename": "helpers.ts",
            "code_sample": "export function formatDate(date: Date) { ... }",
            "expected_type": "utility_modules",
            "priority": 2
        },
        {
            "filename": "CONSTANTS.ts",
            "code_sample": "export const API_URL = 'https://api.example.com';",
            "expected_type": "constants",
            "priority": 2
        },
        {
            "filename": "errors.ts",
            "code_sample": "export class ValidationError extends Error { ... }",
            "expected_type": "error_definitions",
            "priority": 2
        },
        {
            "filename": "types.ts",
            "code_sample": "export type RequestPayload = { ... }",
            "expected_type": "type_definitions",
            "priority": 2
        },

        # Priority 3 (P3) - 5 types
        {
            "filename": "validation.ts",
            "code_sample": "export function validateEmail(email: string): boolean { ... }",
            "expected_type": "validation",
            "priority": 3
        },
        {
            "filename": "authMiddleware.ts",
            "code_sample": "export function authMiddleware(req, res, next) { ... }",
            "expected_type": "middleware",
            "priority": 3
        },
        {
            "filename": "transformers.ts",
            "code_sample": "export function transformUserData(raw: any): User { ... }",
            "expected_type": "transformers",
            "priority": 3
        },
        {
            "filename": "eventHandlers.ts",
            "code_sample": "export function handleClick(event: MouseEvent) { ... }",
            "expected_type": "event_handlers",
            "priority": 3
        },
        {
            "filename": "AuthService.ts",
            "code_sample": "class AuthService { login() { ... } logout() { ... } }",
            "expected_type": "services",
            "priority": 3
        },

        # Priority 4 (P4) - 5 types
        {
            "filename": "config.ts",
            "code_sample": "export const config = { database: { ... }, api: { ... } }",
            "expected_type": "configuration",
            "priority": 4
        },
        {
            "filename": "ThemeProvider.tsx",
            "code_sample": "export const ThemeProvider: React.FC = ({ children }) => { ... }",
            "expected_type": "context_providers",
            "priority": 4
        },
        {
            "filename": "decorators.ts",
            "code_sample": "@Logger export class Service { ... }",
            "expected_type": "decorators",
            "priority": 4
        },
        {
            "filename": "UserFactory.ts",
            "code_sample": "export class UserFactory { create() { return new User(); } }",
            "expected_type": "factories",
            "priority": 4
        },
        {
            "filename": "EventObserver.ts",
            "code_sample": "class EventObserver { observe(event) { ... } notify() { ... } }",
            "expected_type": "observers",
            "priority": 4
        }
    ]

    # Run tests
    results = []
    passed = 0
    failed = 0
    confidence_scores = []

    print("Testing Element Type Detection (20 types)\n")
    print(f"{'Filename':<25} {'Expected':<20} {'Detected':<20} {'Conf':<5} {'Stage':<6} {'Result':<6}")
    print("=" * 100)

    for test_case in test_cases:
        filename = test_case["filename"]
        code = test_case["code_sample"]
        expected = test_case["expected_type"]
        priority = test_case["priority"]

        try:
            # Run detection
            result: DetectionResult = detector.detect(file_path=filename, code_content=code)

            # Check result
            is_correct = result.element_type == expected
            is_confident = result.confidence >= 80.0
            status = "PASS" if (is_correct and is_confident) else "FAIL"

            if status == "PASS":
                passed += 1
            else:
                failed += 1

            confidence_scores.append(result.confidence)

            # Print result
            detection_method_short = result.detection_method.split(":")[0] if ":" in result.detection_method else result.detection_method
            print(f"{filename:<25} {expected:<20} {result.element_type:<20} {result.confidence:>4.0f}% {detection_method_short:<6} {status:<6}")

            results.append({
                "filename": filename,
                "expected_type": expected,
                "detected_type": result.element_type,
                "confidence": result.confidence,
                "detection_method": result.detection_method,
                "priority": priority,
                "pass": status == "PASS"
            })

        except Exception as e:
            print(f"{filename:<25} {expected:<20} ERROR: {str(e)}")
            failed += 1
            results.append({
                "filename": filename,
                "expected_type": expected,
                "error": str(e),
                "pass": False
            })

    # Summary
    print("=" * 100)
    total = passed + failed
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nRESULTS:")
    print(f"  Total tests:      {total}")
    print(f"  Passed:           {passed}")
    print(f"  Failed:           {failed}")
    print(f"  Pass rate:        {pass_rate:.1f}%")
    print(f"  Avg confidence:   {avg_confidence:.1f}%")
    print(f"\nTarget: >=80% pass rate, >=80% average confidence")

    # CR-2 decision
    if pass_rate >= 80 and avg_confidence >= 80:
        print("\n[PASS] CR-2: Detection confidence meets requirements")
        return True, results
    else:
        print(f"\n[FAIL] CR-2: Detection {'pass rate' if pass_rate < 80 else 'confidence'} below 80% threshold")
        return False, results

if __name__ == "__main__":
    import json

    success, results = test_detection_confidence()

    # Save results
    output = {
        "test_category": "TEST-DETECTION",
        "test_date": "2026-01-03",
        "results": results,
        "critical_requirement_met": success
    }

    output_path = Path(__file__).parent.parent.parent / "Desktop" / "assistant" / "coderef" / "workorder" / "resource-sheet-consolidation" / "testing" / "detection-results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    sys.exit(0 if success else 1)
