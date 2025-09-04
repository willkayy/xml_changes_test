# XML Change Management Workflows

This directory contains two distinct workflows for managing XML file changes through CSV review and approval.

## Workflow Structure

```
src/
├── workflow_1_diff_analysis/     # Find differences and generate CSV
│   └── xml_diff_analyzer.py      # Core diff analysis engine
├── workflow_2_csv_to_xml/        # Apply CSV changes back to XML
│   └── csv_change_applicator.py  # Core change application engine
├── run_workflow_1.py             # Main entry point for workflow 1
├── run_workflow_2.py             # Main entry point for workflow 2
└── README.md                     # This file
```

## Workflow 1: XML Diff Analysis

**Purpose**: Compare two sets of XML files and generate a CSV report of all changes for manual review.

**Input**: 
- `data/set_a/` (original XML files)
- `data/set_b/` (updated XML files)

**Output**: 
- `output/xml_changes_YYYYMMDD_HHMMSS.csv` (timestamped change report)

**Usage**:
```bash
python3 src/run_workflow_1.py
```

**CSV Columns**:
- `file_id`: XML filename
- `change_type`: ADD, MODIFY, DELETE
- `section_id`: Section identifier
- `xml_path`: XPath location of change
- `old_content`: Original content
- `new_content`: Updated content
- `approved`: "approved,rejected,pending" (dropdown options for review)

## Workflow 2: CSV to XML Application

**Purpose**: Apply approved changes from the CSV back to XML files, creating updated versions.

**Input**: 
- `data/set_a/` (source XML files)
- `input/xml_changes.csv` (manually reviewed CSV file)

**Output**: 
- `output/updated_xmls_YYYYMMDD_HHMMSS/` (timestamped XML files with approved changes applied)

**Usage**:
```bash
python3 src/run_workflow_2.py
```

**Approval Options**:
- `approved`: Change will be applied to XML
- `rejected`: Change will be ignored  
- `pending`: Change will be ignored (default)

## Complete Process

1. **Run Workflow 1**: Generate timestamped CSV with all changes
   ```bash
   python3 src/run_workflow_1.py
   ```
   - Creates: `output/xml_changes_YYYYMMDD_HHMMSS.csv`

2. **Manual Review**: 
   - Take the generated CSV from `output/` folder
   - Edit it and replace "approved,rejected,pending" with your choice ("approved" or "rejected") for each change
   - **Important**: Save/copy the reviewed CSV as `input/xml_changes.csv`

3. **Run Workflow 2**: Apply approved changes to create timestamped updated XML files
   ```bash
   python3 src/run_workflow_2.py
   ```
   - Reads: `input/xml_changes.csv` (your reviewed file)
   - Creates: `output/updated_xmls_YYYYMMDD_HHMMSS/` with only approved changes applied

4. **Result**: Timestamped folders ensure no overwrites and clear version tracking

## Scalability Features

- **Memory Efficient**: Processes large datasets without loading everything into memory
- **Error Handling**: Robust parsing and detailed error reporting
- **Selective Application**: Only applies changes marked as "approved"
- **File Preservation**: Copies unchanged files to output directory
- **Change Tracking**: Maintains detailed logs of what was applied vs rejected

This workflow system is designed to scale to projects with 3000+ XML files while maintaining accuracy and providing full control over which changes are applied.