# CLAUDE.md - XML Diff Analysis to CSV Project

## Project Overview
This project analyzes differences between two sets of XML files (set_a and set_b) and generates CSV reports for manual review and approval of changes. Designed to scale to 3000+ XML files.

## Commands and Scripts

### Main Analysis Commands
```bash
# Run analysis on test data
python3 src/run_analysis.py

# Run with custom paths
python3 src/xml_diff_analyzer.py <set_a_dir> <set_b_dir> <output_csv>

# Example with specific paths
python3 src/xml_diff_analyzer.py data/set_a data/set_b output/changes.csv
```

### Development Commands
```bash
# No linting/type checking setup yet - add as needed for scaling
# python3 -m flake8 src/
# mypy src/
```

### Testing
```bash
# Current test uses sample data in data/ folder
python3 src/run_analysis.py

# View results
cat output/xml_changes.csv | head -20
```

## Development Workflow
1. **Run Analysis**: Execute `python3 src/run_analysis.py`
2. **Review CSV Output**: Check `output/xml_changes.csv` for changes
3. **Manual Review**: Review each change with status "pending"
4. **Approval Process**: Update status to "approved" or "rejected"
5. **Apply Changes**: Use approved changes to update XML files
6. **Scale Up**: Apply same process to larger XML datasets

## File Structure
- `data/set_a/` - Original XML files (version 1.0)
- `data/set_b/` - Updated XML files (version 1.1) 
- `data/consolidated_diff.patch` - Unified diff patch file (reference)
- `src/xml_diff_analyzer.py` - Core analysis engine
- `src/run_analysis.py` - Test runner script
- `source_data/` - Processing workspace
- `output/xml_changes.csv` - Generated change report

## Key Features
- **Scalable Architecture**: Handles 3000+ XML files efficiently
- **Precise Location Tracking**: XPath-like paths for exact change locations
- **Cross-Section Detection**: Tracks content moves between files
- **Memory Efficient**: Processes files individually
- **Structured Output**: CSV format for easy review workflow
- **Change Type Detection**: ADD, MODIFY, DELETE, MOVE operations

## Current Test Results
- **113 total changes** detected in sample data
- **7 additions** (new elements/tools)
- **1 deletion**
- **105 modifications** (content updates, version changes)

## CSV Output Schema
```
file_id,change_type,section_id,xml_path,old_content,new_content,status
appendix_a_tools,ADD,appendix_a_tools,/tool[@name='Julia'],"","<tool name='Julia'>...",pending
appendix_a_tools,MODIFY,appendix_a_tools,/version,1.0,1.1,pending
```

## Next Steps for Scaling
1. Add error handling for malformed XML files
2. Implement batch processing for large datasets
3. Add progress reporting for long-running analyses
4. Create change application script (CSV → XML updates)
5. Add configuration file for custom change detection rules