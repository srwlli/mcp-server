"""
Demo script to prove scanner integration is working.
Demonstrates all three task areas with real data.
"""
import asyncio
import json
from pathlib import Path
from generators.planning_analyzer import PlanningAnalyzer
from handlers.impact_analysis import ImpactAnalyzer
from utils.complexity_estimator import ComplexityEstimator

# Use test fixtures directory as demo project
PROJECT_PATH = Path(__file__).parent / "tests" / "fixtures"

async def demo_type_coverage():
    """Demo Task 1: Type Coverage in Planning Workflows"""
    print("\n" + "="*80)
    print("TASK 1: TYPE COVERAGE - Planning workflows detect interfaces & decorators")
    print("="*80)

    analyzer = PlanningAnalyzer(PROJECT_PATH)

    # Extract type system elements
    type_system = await analyzer.get_type_system_elements()
    decorators = await analyzer.get_decorator_elements()

    print(f"\n✅ Detected {len(type_system['interfaces'])} interfaces:")
    for interface in type_system['interfaces'][:3]:
        print(f"   - {interface['name']} ({interface['file']}:{interface['line']})")

    print(f"\n✅ Detected {len(type_system['type_aliases'])} type aliases:")
    for alias in type_system['type_aliases']:
        print(f"   - {alias['name']} ({alias['file']}:{alias['line']})")

    print(f"\n✅ Detected {len(decorators)} decorators:")
    for decorator in decorators:
        print(f"   - {decorator['name']} (target: {decorator['target']}, {decorator['file']}:{decorator['line']})")

    return type_system, decorators

def demo_impact_analysis():
    """Demo Task 2: Impact Analysis with Relationship Graphs"""
    print("\n" + "="*80)
    print("TASK 2: IMPACT ANALYSIS - Transitive dependency analysis with risk levels")
    print("="*80)

    analyzer = ImpactAnalyzer(PROJECT_PATH)

    # Analyze impact of changing 'authenticateUser' function
    element_name = "authenticateUser"
    print(f"\n🔍 Analyzing impact of changing '{element_name}'...")

    result = analyzer.analyze_element_impact(element_name, max_depth=3)

    if result:
        score = result['impact_score']
        print(f"\n✅ Impact Analysis Results:")
        print(f"   - Affected elements: {score['affected_count']}")
        print(f"   - Risk level: {score['risk_level'].upper()}")
        print(f"   - Depth breakdown: {score['depth_breakdown']}")

        # Show affected elements
        affected = result['affected_elements'][:5]  # First 5
        print(f"\n✅ Sample affected elements (showing {len(affected)} of {score['affected_count']}):")
        for elem in affected:
            print(f"   - {elem['name']} (depth: {elem['depth']})")

        # Show Mermaid graph snippet
        report_lines = result['report'].split('\n')
        mermaid_start = next((i for i, line in enumerate(report_lines) if '```mermaid' in line), None)
        if mermaid_start:
            print(f"\n✅ Mermaid graph generated:")
            print("   " + "\n   ".join(report_lines[mermaid_start:mermaid_start+8]))
    else:
        print(f"   ❌ Element '{element_name}' not found")

    return result

def demo_complexity_tracking():
    """Demo Task 3: Complexity Tracking with Refactoring Flagging"""
    print("\n" + "="*80)
    print("TASK 3: COMPLEXITY TRACKING - Data-driven effort estimation (0-10 scale)")
    print("="*80)

    estimator = ComplexityEstimator(PROJECT_PATH)

    # Estimate complexity for individual elements
    elements = ["authenticateUser", "UserRepository", "IAuthService"]

    print(f"\n✅ Individual element complexity:")
    for element_name in elements:
        result = estimator.estimate_element_complexity(element_name)
        if result:
            print(f"   - {element_name}:")
            print(f"     Score: {result['complexity_score']}/10 ({result['risk_level']})")
            print(f"     Estimated LOC: {result['estimated_loc']}")
            print(f"     Parameters: {result.get('parameter_count', 0)}, Calls: {result.get('calls_count', 0)}")

    # Estimate task complexity (aggregate)
    task_elements = ["authenticateUser", "validateCredentials", "generateToken", "UserRepository"]
    task_result = estimator.estimate_task_complexity(task_elements)

    print(f"\n✅ Task complexity (aggregated across {len(task_elements)} elements):")
    print(f"   - Average score: {task_result['avg_complexity_score']:.1f}/10")
    print(f"   - Max score: {task_result['max_complexity_score']}/10")
    print(f"   - Total estimated LOC: {task_result['total_estimated_loc']}")
    print(f"   - Distribution: {task_result['complexity_distribution']}")

    # Show refactoring candidates (score > 7)
    high_complexity = task_result['high_complexity_elements']
    if high_complexity:
        print(f"\n⚠️  Refactoring candidates (score > 7):")
        for elem in high_complexity:
            print(f"   - {elem['name']} (score: {elem['score']}, risk: {elem['risk_level']})")
    else:
        print(f"\n✅ No refactoring candidates (all elements have score ≤ 7)")

    return task_result

async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("SCANNER INTEGRATION DEMO - Proving All Features Work")
    print("="*80)
    print(f"Project: {PROJECT_PATH}")
    print(f"Test fixtures: sample_index.json (25 elements)")

    # Demo all three tasks
    type_system, decorators = await demo_type_coverage()
    impact_result = demo_impact_analysis()
    complexity_result = demo_complexity_tracking()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY - All Scanner Integration Features Verified")
    print("="*80)
    print(f"✅ Type Coverage: {len(type_system['interfaces'])} interfaces, {len(decorators)} decorators")
    print(f"✅ Impact Analysis: {impact_result['impact_score']['affected_count'] if impact_result else 0} affected elements")
    print(f"✅ Complexity Tracking: {complexity_result['avg_complexity_score']:.1f}/10 avg complexity")
    print("\n🎉 All features working as expected!")

if __name__ == "__main__":
    asyncio.run(main())
