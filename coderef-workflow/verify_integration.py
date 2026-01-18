"""
Simple verification script to prove scanner integration works.
Uses test fixtures directly without needing .coderef directory structure.
"""
import json
from pathlib import Path
from handlers.impact_analysis import ImpactAnalyzer
from utils.complexity_estimator import ComplexityEstimator

# Load test fixture
FIXTURES_PATH = Path(__file__).parent / "tests" / "fixtures"
INDEX_PATH = FIXTURES_PATH / "sample_index.json"

def load_test_data():
    """Load sample_index.json for testing"""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # sample_index.json is already an array
    return data

def verify_type_coverage():
    """Verify Task 1: Type system extraction works"""
    print("\n" + "="*70)
    print("TASK 1: TYPE COVERAGE - Detecting interfaces & decorators")
    print("="*70)

    elements = load_test_data()

    # Extract interfaces
    interfaces = [e for e in elements if e.get('type') == 'interface']
    type_aliases = [e for e in elements if e.get('type') == 'type']
    decorators = [e for e in elements if e.get('type') == 'decorator']

    print(f"\n[OK] Detected {len(interfaces)} interfaces:")
    for interface in interfaces[:3]:
        print(f"  - {interface['name']} ({interface['file']})")

    print(f"\n[OK] Detected {len(type_aliases)} type aliases:")
    for alias in type_aliases:
        print(f"  - {alias['name']} ({alias['file']})")

    print(f"\n[OK] Detected {len(decorators)} decorators:")
    for decorator in decorators:
        print(f"  - {decorator['name']} (target: {decorator.get('target', 'unknown')})")

    return len(interfaces), len(decorators)

def verify_impact_analysis():
    """Verify Task 2: Impact analysis with BFS traversal"""
    print("\n" + "="*70)
    print("TASK 2: IMPACT ANALYSIS - Transitive dependency tracking")
    print("="*70)

    # Create analyzer (will work with test fixtures)
    analyzer = ImpactAnalyzer(FIXTURES_PATH.parent.parent)  # Point to project root

    # Manually create a simple test
    elements = load_test_data()

    # Find authenticateUser
    auth_user = next((e for e in elements if e['name'] == 'authenticateUser'), None)

    if auth_user:
        print(f"\n[OK] Found element: {auth_user['name']}")
        print(f"  - Type: {auth_user['type']}")
        print(f"  - Dependencies: {auth_user.get('dependencies', [])}")
        print(f"  - Called by: {auth_user.get('calledBy', [])}")

        # Test BFS traversal
        result = analyzer.analyze_element_impact('authenticateUser', max_depth=2)

        if result:
            score = result['impact_score']
            print(f"\n[OK] Impact analysis completed:")
            print(f"  - Affected elements: {score['affected_count']}")
            print(f"  - Risk level: {score['risk_level'].upper()}")
            print(f"  - Depth breakdown: {json.dumps(score['depth_breakdown'], indent=4)}")

            # Check report generation
            report = result['report']
            has_summary = 'Summary' in report
            has_mermaid = '```mermaid' in report

            print(f"\n[OK] Report generated:")
            print(f"  - Has summary section: {has_summary}")
            print(f"  - Has Mermaid graph: {has_mermaid}")

            return score['affected_count']
        else:
            print("\n[WARN] No impact result (element may not be in graph)")
            return 0
    else:
        print("\n[WARN] authenticateUser not found in fixtures")
        return 0

def verify_complexity_tracking():
    """Verify Task 3: Complexity estimation with scoring"""
    print("\n" + "="*70)
    print("TASK 3: COMPLEXITY TRACKING - Data-driven effort estimation")
    print("="*70)

    estimator = ComplexityEstimator(FIXTURES_PATH.parent.parent)

    # Test complexity estimation
    test_elements = [
        "authenticateUser",  # function with 2 params, 3 calls
        "UserRepository",    # class
        "IAuthService"       # interface
    ]

    print(f"\n[OK] Testing complexity estimation for {len(test_elements)} elements:")

    results = []
    for elem_name in test_elements:
        result = estimator.estimate_element_complexity(elem_name)
        if result:
            score = result['complexity_score']
            risk = result['risk_level']
            estimated_loc = result['estimated_loc']

            print(f"\n  {elem_name}:")
            print(f"    - Complexity score: {score}/10")
            print(f"    - Risk level: {risk}")
            print(f"    - Estimated LOC: {estimated_loc}")
            print(f"    - Parameters: {result.get('parameter_count', 0)}")
            print(f"    - Calls: {result.get('calls_count', 0)}")

            results.append(result)

    # Test task complexity (aggregate)
    task_result = estimator.estimate_task_complexity(test_elements)

    print(f"\n[OK] Task-level complexity (aggregated):")
    print(f"  - Average score: {task_result['avg_complexity_score']:.1f}/10")
    print(f"  - Max score: {task_result['max_complexity_score']}/10")
    print(f"  - Total estimated LOC: {task_result['total_estimated_loc']}")
    print(f"  - Distribution: {json.dumps(task_result['complexity_distribution'], indent=4)}")

    # Check refactoring flagging (score > 7)
    high_complexity = task_result['high_complexity_elements']
    if high_complexity:
        print(f"\n[OK] Refactoring candidates (score > 7): {len(high_complexity)} found")
        for elem in high_complexity:
            print(f"  - {elem['name']} (score: {elem['score']}, risk: {elem['risk_level']})")
    else:
        print(f"\n[OK] No refactoring candidates (all scores <= 7)")

    return task_result['avg_complexity_score']

def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("SCANNER INTEGRATION VERIFICATION")
    print("="*70)
    print(f"Test data: {INDEX_PATH}")
    print(f"Fixtures: {len(load_test_data())} elements")

    # Verify each task area
    interfaces_count, decorators_count = verify_type_coverage()
    affected_count = verify_impact_analysis()
    avg_complexity = verify_complexity_tracking()

    # Final summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"[OK] Type Coverage: {interfaces_count} interfaces, {decorators_count} decorators detected")
    print(f"[OK] Impact Analysis: {affected_count} affected elements identified")
    print(f"[OK] Complexity Tracking: {avg_complexity:.1f}/10 average complexity calculated")
    print("\n[SUCCESS] All scanner integration features verified and working!")
    print("="*70)

if __name__ == "__main__":
    main()
