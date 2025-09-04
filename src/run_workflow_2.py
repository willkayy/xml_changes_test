#!/usr/bin/env python3
"""
Main runner for Workflow 2: CSV to XML Application
"""

import sys
from pathlib import Path
from datetime import datetime

# Add workflow 2 to path
workflow_2_path = Path(__file__).parent / "workflow_2_csv_to_xml"
sys.path.insert(0, str(workflow_2_path))

from csv_change_applicator import CSVChangeApplicator

def main():
    print("=== WORKFLOW 2: CSV TO XML APPLICATION ===")
    print("Applying approved changes from CSV back to XML files...")
    print()
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    source_xml_dir = data_dir / "set_a"  # Use original set_a as source
    csv_input_dir = project_root / "input"
    csv_file = csv_input_dir / "xml_changes.csv"  # Read from input folder
    
    # Add datetime to output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_xml_dir = project_root / "output" / f"updated_xmls_{timestamp}"
    
    # Validate inputs
    if not source_xml_dir.exists():
        print(f"Error: Source XML directory not found: {source_xml_dir}")
        return 1
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        print(f"Please place the reviewed CSV file at: {csv_file}")
        print(f"(Copy from output/ folder after manual review)")
        return 1
    
    print(f"Applying CSV changes to XML files:")
    print(f"  Source XMLs: {source_xml_dir}")
    print(f"  CSV file: {csv_file}")
    print(f"  Output dir: {output_xml_dir}")
    print()
    
    # Create applicator and load changes
    applicator = CSVChangeApplicator(str(source_xml_dir), str(csv_file), str(output_xml_dir))
    
    print("Loading changes from CSV...")
    applicator.load_csv_changes()
    
    # Show summary of what will be processed
    summary = applicator.get_summary()
    print(f"Loaded changes from CSV:")
    print(f"  Approved changes: {summary['approved']}")
    print(f"  Rejected changes: {summary['rejected']}")
    print(f"  Pending changes: {summary['pending']}")
    print()
    
    if summary['approved'] == 0:
        print("No approved changes found. Update CSV file 'approved' column to 'approved' for changes you want to apply.")
        return 0
    
    # Apply changes
    print(f"Applying {summary['approved']} approved changes...")
    applicator.apply_all_changes()
    
    print(f"\nWorkflow 2 complete!")
    print(f"Updated XML files saved to: {output_xml_dir}")
    
    # List generated files
    if output_xml_dir.exists():
        xml_files = list(output_xml_dir.glob("*.xml"))
        print(f"Generated {len(xml_files)} XML files:")
        for xml_file in sorted(xml_files):
            print(f"  {xml_file.name}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())