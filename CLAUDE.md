# CLAUDE.md - XML Diff Analysis to CSV Project

## Project Overview
This project analyzes differences between two sets of XML files (set_a and set_b) and generates CSV reports for manual review and approval of changes. Designed to scale to 3000+ XML files.

## Commands and Scripts

### Main Analysis Commands
```bash
# Run workflow 1 (uses config.json for paths)
python3 src/run_workflow_1.py

# Run with custom paths (legacy mode)
python3 src/workflow_1_diff_analysis/xml_diff_analyzer.py <set_a_dir> <set_b_dir> <output_csv>

# Config-based mode (recommended)
python3 src/workflow_1_diff_analysis/xml_diff_analyzer.py <output_csv>
```

### Development Commands
```bash
# No linting/type checking setup yet - add as needed for scaling
# python3 -m flake8 src/
# mypy src/
```

### Testing
```bash
# Run workflow 1 on test data
python3 src/run_workflow_1.py

# Run workflow 2 (apply approved changes)
python3 src/run_workflow_2.py

# View results
cat output/xml_changes_*.csv | head -20
```

## Development Workflow
1. **Configure Datasets**: Update `config.json` with your dataset paths
2. **Run Workflow 1**: Execute `python3 src/run_workflow_1.py` to generate CSV
3. **Manual Review**: Review changes in CSV output with new `focused_changes` column
4. **Approval Process**: Update `approved` column to "approved" or "rejected"
5. **Save Reviewed CSV**: Copy reviewed CSV to `input/xml_changes.csv`
6. **Run Workflow 2**: Execute `python3 src/run_workflow_2.py` to apply approved changes
7. **Scale Up**: Apply same process to larger XML datasets

## File Structure
- `config.json` - Configuration file for dataset paths and diff settings
- `test_data/set_a/` - Original XML files (version 1.0)
- `test_data/set_b/` - Updated XML files (version 1.1)
- `test_data/consolidated_diff.patch` - Unified diff patch file (reference)
- `src/workflow_1_diff_analysis/xml_diff_analyzer.py` - Core analysis engine
- `src/workflow_2_csv_to_xml/csv_change_applicator.py` - Change application engine
- `src/run_workflow_1.py` - Workflow 1 runner (diff analysis)
- `src/run_workflow_2.py` - Workflow 2 runner (apply changes)
- `input/xml_changes.csv` - Manually reviewed CSV file (for workflow 2)
- `output/xml_changes_*.csv` - Generated timestamped change reports

## Key Features
- **Configurable Datasets**: Use `config.json` to specify dataset paths
- **Focused Change Detection**: New `focused_changes` column shows specific word changes with context
- **Scalable Architecture**: Handles 3000+ XML files efficiently
- **Precise Location Tracking**: XPath-like paths for exact change locations
- **Cross-Section Detection**: Tracks content moves between files
- **Memory Efficient**: Processes files individually
- **Structured Output**: CSV format for easy review workflow
- **Change Type Detection**: ADD, MODIFY, DELETE operations
- **Two-Workflow System**: Separate diff analysis and change application workflows

## Current Test Results
- **113 total changes** detected in sample data
- **7 additions** (new elements/tools)
- **1 deletion**
- **105 modifications** (content updates, version changes)

## CSV Output Schema
```
file_id,change_type,section_id,xml_path,old_content,new_content,focused_changes,approved
appendix_a_tools,ADD,appendix_a_tools,/tool[@name='Julia'],"","<tool name='Julia'>...","ADDED: '[Julia programming] language for'","approved,rejected,pending"
appendix_a_tools,MODIFY,appendix_a_tools,/version,1.0,1.1,"CHANGED: '[1.0]' → '[1.1]'","approved,rejected,pending"
```

## Next Steps for Scaling
1. Add error handling for malformed XML files
2. Implement batch processing for large datasets
3. Add progress reporting for long-running analyses
4. Create change application script (CSV → XML updates)
5. Add configuration file for custom change detection rules