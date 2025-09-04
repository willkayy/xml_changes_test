#!/usr/bin/env python3
"""
Main runner for Workflow 1: XML Diff Analysis
"""

import sys
from pathlib import Path
from datetime import datetime

# Add workflow 1 to path
workflow_1_path = Path(__file__).parent / "workflow_1_diff_analysis"
sys.path.insert(0, str(workflow_1_path))

from xml_diff_analyzer import XMLDiffAnalyzer

def main():
    print("=== WORKFLOW 1: XML DIFF ANALYSIS ===")
    print("Analyzing differences between XML sets and generating CSV...")
    print()
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    set_a_dir = data_dir / "set_a"
    set_b_dir = data_dir / "set_b"
    output_dir = project_root / "output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Add datetime to CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = output_dir / f"xml_changes_{timestamp}.csv"
    
    # Validate input directories
    if not set_a_dir.exists():
        print(f"Error: set_a directory not found: {set_a_dir}")
        return 1
    
    if not set_b_dir.exists():
        print(f"Error: set_b directory not found: {set_b_dir}")
        return 1
    
    print(f"Analyzing XML changes between:")
    print(f"  Set A: {set_a_dir}")
    print(f"  Set B: {set_b_dir}")
    print(f"  Output: {output_csv}")
    print()
    
    # Run analysis
    analyzer = XMLDiffAnalyzer(str(set_a_dir), str(set_b_dir))
    
    print("Starting analysis...")
    analyzer.analyze_changes()
    
    print("Exporting to CSV...")
    analyzer.export_to_csv(str(output_csv))
    
    # Print summary
    summary = analyzer.get_summary()
    total_changes = len(analyzer.changes)
    
    print(f"\nAnalysis complete!")
    print(f"Total changes found: {total_changes}")
    
    if summary:
        print("\nChange breakdown:")
        for change_type, count in sorted(summary.items()):
            print(f"  {change_type:10}: {count:4} changes")
    
    print(f"\nResults saved to: {output_csv}")
    
    # Show first few changes as preview
    if analyzer.changes:
        print("\nFirst 3 changes preview:")
        for i, change in enumerate(analyzer.changes[:3]):
            print(f"  {i+1}. [{change.change_type}] {change.file_id} - {change.xml_path}")
            if change.old_content and len(change.old_content) > 100:
                print(f"     Old: {change.old_content[:100]}...")
            else:
                print(f"     Old: {change.old_content}")
            
            if change.new_content and len(change.new_content) > 100:
                print(f"     New: {change.new_content[:100]}...")
            else:
                print(f"     New: {change.new_content}")
            print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())