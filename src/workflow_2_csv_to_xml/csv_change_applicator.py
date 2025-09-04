#!/usr/bin/env python3
"""
CSV Change Applicator - Applies approved changes from CSV back to XML files
"""

import xml.etree.ElementTree as ET
import csv
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ApprovedChange:
    file_id: str
    change_type: str
    section_id: str
    xml_path: str
    old_content: str
    new_content: str
    approved: str


class CSVChangeApplicator:
    def __init__(self, source_xml_dir: str, csv_file: str, output_xml_dir: str):
        self.source_xml_dir = Path(source_xml_dir)
        self.csv_file = Path(csv_file)
        self.output_xml_dir = Path(output_xml_dir)
        self.approved_changes: List[ApprovedChange] = []
        self.rejected_changes: List[ApprovedChange] = []
        
    def load_csv_changes(self) -> None:
        """Load changes from CSV file and filter by approval status"""
        with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Handle both old 'status' column and new 'approved' column for backward compatibility
                approved_value = row.get('approved', row.get('status', ''))
                
                change = ApprovedChange(
                    file_id=row['file_id'],
                    change_type=row['change_type'],
                    section_id=row['section_id'],
                    xml_path=row['xml_path'],
                    old_content=row['old_content'],
                    new_content=row['new_content'],
                    approved=approved_value
                )
                
                # Check if the value is exactly 'approved' or 'rejected' (not just contains)
                approved_clean = change.approved.strip().lower()
                if approved_clean == 'approved':
                    self.approved_changes.append(change)
                elif approved_clean == 'rejected':
                    self.rejected_changes.append(change)
    
    def find_element_by_path(self, root: ET.Element, xpath: str) -> Optional[ET.Element]:
        """Find element by XPath-like string"""
        if xpath == "/" or xpath == "/document":
            return root
        
        # Remove leading slash
        if xpath.startswith("/"):
            xpath = xpath[1:]
        
        # Split path into parts
        parts = xpath.split("/")
        current = root
        
        for part in parts:
            if not part:
                continue
                
            # Handle attribute paths
            if part.startswith("@"):
                return current  # Return parent for attribute changes
            
            # Handle element with attributes like tool[@name='Python']
            if "[" in part and "]" in part:
                element_name = part.split("[")[0]
                attr_part = part.split("[")[1].split("]")[0]
                
                if "@" in attr_part and "=" in attr_part:
                    attr_name = attr_part.split("@")[1].split("=")[0]
                    attr_value = attr_part.split("=")[1].strip("'\"")
                    
                    # Find child with matching attribute
                    found = None
                    for child in current:
                        if child.tag == element_name and child.get(attr_name) == attr_value:
                            found = child
                            break
                    
                    if found is not None:
                        current = found
                    else:
                        return None
                else:
                    # Handle other bracket syntax if needed
                    found = current.find(element_name)
                    if found is not None:
                        current = found
                    else:
                        return None
            else:
                # Simple element name
                found = current.find(part)
                if found is not None:
                    current = found
                else:
                    return None
        
        return current
    
    def create_element_from_xml_string(self, xml_string: str) -> Optional[ET.Element]:
        """Parse XML string and return element"""
        try:
            # Wrap in root if not already wrapped
            if not xml_string.strip().startswith("<?xml"):
                xml_string = f"<root>{xml_string}</root>"
                root = ET.fromstring(xml_string)
                if len(root) == 1:
                    return root[0]
                else:
                    return root
            else:
                return ET.fromstring(xml_string)
        except ET.ParseError as e:
            print(f"Error parsing XML string: {e}")
            print(f"XML content: {xml_string[:200]}...")
            return None
    
    def apply_change_to_element(self, root: ET.Element, change: ApprovedChange) -> bool:
        """Apply a single change to the XML tree"""
        try:
            if change.change_type == "ADD":
                return self.apply_add_change(root, change)
            elif change.change_type == "MODIFY":
                return self.apply_modify_change(root, change)
            elif change.change_type == "DELETE":
                return self.apply_delete_change(root, change)
            else:
                print(f"Unknown change type: {change.change_type}")
                return False
        except Exception as e:
            print(f"Error applying change {change.change_type} to {change.xml_path}: {e}")
            return False
    
    def apply_add_change(self, root: ET.Element, change: ApprovedChange) -> bool:
        """Apply ADD change - create new element"""
        if change.xml_path == "/" or change.xml_path == "/document":
            # Adding entire new file - this should be handled at file level
            return True
        
        # Find parent element
        parent_path = "/".join(change.xml_path.split("/")[:-1])
        if not parent_path:
            parent_path = "/"
        
        parent = self.find_element_by_path(root, parent_path)
        if parent is None:
            print(f"Could not find parent for ADD at {change.xml_path}")
            return False
        
        # Create new element from XML string
        new_element = self.create_element_from_xml_string(change.new_content)
        if new_element is not None:
            parent.append(new_element)
            return True
        
        return False
    
    def apply_modify_change(self, root: ET.Element, change: ApprovedChange) -> bool:
        """Apply MODIFY change - update element content"""
        element = self.find_element_by_path(root, change.xml_path)
        if element is None:
            print(f"Could not find element for MODIFY at {change.xml_path}")
            return False
        
        # Handle attribute modifications
        if change.xml_path.endswith("/@attributes"):
            # This is a more complex case - for now skip
            return True
        
        # For simple content modifications, update text
        if change.xml_path.endswith("/version"):
            element.text = change.new_content
        elif change.xml_path.endswith("/text"):
            element.text = change.new_content
        elif hasattr(element, 'text') and element.text:
            # Replace text content if it matches old content
            if change.old_content.strip() in str(element.text).strip():
                element.text = change.new_content
            else:
                # Try to find and replace in child elements
                self.update_element_text_recursive(element, change.old_content, change.new_content)
        
        return True
    
    def apply_delete_change(self, root: ET.Element, change: ApprovedChange) -> bool:
        """Apply DELETE change - remove element"""
        if change.xml_path == "/" or change.xml_path == "/document":
            # Deleting entire file - this should be handled at file level
            return True
        
        # Find parent and element to delete
        parent_path = "/".join(change.xml_path.split("/")[:-1])
        if not parent_path:
            parent_path = "/"
        
        parent = self.find_element_by_path(root, parent_path)
        element = self.find_element_by_path(root, change.xml_path)
        
        if parent is not None and element is not None:
            parent.remove(element)
            return True
        
        return False
    
    def update_element_text_recursive(self, element: ET.Element, old_text: str, new_text: str) -> None:
        """Recursively update text content in element and children"""
        if element.text and old_text in element.text:
            element.text = element.text.replace(old_text, new_text)
        
        if element.tail and old_text in element.tail:
            element.tail = element.tail.replace(old_text, new_text)
        
        for child in element:
            self.update_element_text_recursive(child, old_text, new_text)
    
    def apply_changes_to_file(self, file_id: str) -> bool:
        """Apply all approved changes for a specific file"""
        # Get all changes for this file
        file_changes = [c for c in self.approved_changes if c.file_id == file_id]
        if not file_changes:
            return True  # No changes to apply
        
        # Check if this is a new file (ADD with document root)
        new_file_changes = [c for c in file_changes if c.change_type == "ADD" and c.xml_path in ["/", "/document"]]
        if new_file_changes:
            # Create new file from scratch
            return self.create_new_file(file_id, new_file_changes[0])
        
        # Load existing file
        source_file = self.source_xml_dir / f"{file_id}.xml"
        if not source_file.exists():
            print(f"Source file not found: {source_file}")
            return False
        
        try:
            tree = ET.parse(source_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Error parsing {source_file}: {e}")
            return False
        
        # Apply all changes to this file
        success_count = 0
        for change in file_changes:
            if self.apply_change_to_element(root, change):
                success_count += 1
            else:
                print(f"Failed to apply change: {change.change_type} at {change.xml_path}")
        
        # Save modified file
        output_file = self.output_xml_dir / f"{file_id}.xml"
        try:
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"Applied {success_count}/{len(file_changes)} changes to {output_file}")
            return True
        except Exception as e:
            print(f"Error writing {output_file}: {e}")
            return False
    
    def create_new_file(self, file_id: str, change: ApprovedChange) -> bool:
        """Create a new XML file from scratch"""
        new_element = self.create_element_from_xml_string(change.new_content)
        if new_element is None:
            return False
        
        # Create tree and save
        tree = ET.ElementTree(new_element)
        output_file = self.output_xml_dir / f"{file_id}.xml"
        
        try:
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"Created new file: {output_file}")
            return True
        except Exception as e:
            print(f"Error creating new file {output_file}: {e}")
            return False
    
    def copy_unchanged_files(self) -> None:
        """Copy files that have no approved changes"""
        # Get list of files with changes
        changed_files = {change.file_id for change in self.approved_changes}
        
        # Copy all source files that weren't changed
        for source_file in self.source_xml_dir.glob("*.xml"):
            file_id = source_file.stem
            if file_id not in changed_files:
                output_file = self.output_xml_dir / source_file.name
                shutil.copy2(source_file, output_file)
                print(f"Copied unchanged file: {source_file.name}")
    
    def apply_all_changes(self) -> None:
        """Apply all approved changes and create output XML files"""
        # Create output directory
        self.output_xml_dir.mkdir(exist_ok=True, parents=True)
        
        # Get all unique file IDs that have changes
        file_ids_with_changes = {change.file_id for change in self.approved_changes}
        
        # Apply changes file by file
        success_count = 0
        for file_id in file_ids_with_changes:
            if self.apply_changes_to_file(file_id):
                success_count += 1
            else:
                print(f"Failed to process file: {file_id}")
        
        # Copy unchanged files
        self.copy_unchanged_files()
        
        print(f"\nProcessing complete:")
        print(f"  Successfully processed: {success_count}/{len(file_ids_with_changes)} changed files")
        print(f"  Total approved changes: {len(self.approved_changes)}")
        print(f"  Total rejected changes: {len(self.rejected_changes)}")
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of changes by approval status"""
        # Count total changes loaded
        total_changes = len(self.approved_changes) + len(self.rejected_changes)
        
        # Load all changes to count pending
        all_changes_count = 0
        with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_changes_count += 1
        
        pending_count = all_changes_count - total_changes
        
        summary = {
            'approved': len(self.approved_changes),
            'rejected': len(self.rejected_changes),
            'pending': pending_count
        }
        return summary


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python csv_change_applicator.py <source_xml_dir> <csv_file> <output_xml_dir>")
        sys.exit(1)
    
    source_xml_dir = sys.argv[1]
    csv_file = sys.argv[2]
    output_xml_dir = sys.argv[3]
    
    applicator = CSVChangeApplicator(source_xml_dir, csv_file, output_xml_dir)
    applicator.load_csv_changes()
    applicator.apply_all_changes()
    
    summary = applicator.get_summary()
    print(f"\nSummary:")
    for approval_status, count in summary.items():
        print(f"  {approval_status.capitalize()}: {count}")