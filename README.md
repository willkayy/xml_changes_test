# XML Diff Analysis to CSV

A scalable tool for analyzing changes between XML document sets and generating CSV reports for manual review and approval. Designed to handle 3000+ XML files with section-based change tracking.

## Purpose

This project processes two sets of XML files to:
1. **Identify Differences**: Compare set_a (v1.0) with set_b (v1.1) XML documents
2. **Generate CSV Reports**: Create detailed change summaries that can be manually reviewed
3. **Enable Approval Workflow**: Provide structured data for approving/rejecting individual changes
4. **Scale to Large Projects**: Handle thousands of XML files efficiently

## Project Structure

```
xml_changes_test/
├── data/
│   ├── set_a/                    # Original XML files (v1.0)
│   ├── set_b/                    # Updated XML files (v1.1)
│   └── consolidated_diff.patch   # Unified diff patch
├── src/                          # Analysis scripts
│   ├── workflow_1_diff_analysis/ # XML diff analysis
│   ├── workflow_2_csv_to_xml/    # CSV to XML application
│   ├── run_workflow_1.py         # Main workflow 1 runner
│   └── run_workflow_2.py         # Main workflow 2 runner
├── input/                        # Manually reviewed CSV files
│   └── xml_changes.csv           # Place reviewed CSV here
├── output/                       # Generated files with timestamps
│   ├── xml_changes_YYYYMMDD_HHMMSS.csv    # Generated change reports
│   └── updated_xmls_YYYYMMDD_HHMMSS/      # Updated XML files
└── source_data/                  # Processing workspace
```

## How to Run

```bash
# Run analysis on test data
python3 src/run_analysis.py

# Or run directly with custom paths
python3 src/xml_diff_analyzer.py data/set_a data/set_b output/changes.csv
```

## CSV Output Format

The generated CSV contains the following columns:
- **file_id**: XML filename (e.g., "appendix_a_tools")
- **change_type**: ADD, MODIFY, DELETE, or MOVE
- **section_id**: Section identifier (currently same as file_id)
- **xml_path**: XPath-like location of the change
- **old_content**: Original XML content
- **new_content**: Updated XML content
- **status**: "pending" (ready for manual review/approval)

## Test Results

Analysis of the sample data detected:
- **113 total changes** between set_a and set_b
- **7 additions** (new elements like Julia tool, Looker platform)
- **1 deletion** 
- **105 modifications** (version updates, enhanced content)

## Change Types Detected

- **Version Updates**: All files updated from 1.0 to 1.1
- **Content Enhancements**: Added libraries (seaborn, plotly, tidyverse)
- **New Tools**: Julia programming language, Looker BI platform
- **Database Extensions**: Snowflake added to SQL variants
- **New Files**: chapter6_ethics.xml (Data Ethics and Responsible AI)
- **Reference Updates**: Updated index entries and page numbers

## Scalability Features

- **Memory Efficient**: Processes files individually for large datasets
- **XPath Tracking**: Precise location identification for changes
- **Cross-Section Detection**: Tracks content moves between files
- **Structured Output**: CSV format for easy review and processing
- **Error Handling**: Robust parsing with detailed error reporting

This system is designed to scale to projects with 3000+ XML files while maintaining accuracy and performance.