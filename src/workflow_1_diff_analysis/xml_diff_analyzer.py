#!/usr/bin/env python3
"""
XML Diff Analyzer - Compares XML files and generates CSV output for change review
"""

import xml.etree.ElementTree as ET
import csv
import sys
import json
import difflib
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class XMLChange:
    file_id: str
    change_type: str  # ADD, MODIFY, DELETE, MOVE
    section_id: str
    xml_path: str
    old_content: str
    new_content: str
    focused_changes: str = ""  # Specific word changes with context
    approved: str = ""  # Will be populated with dropdown options


class XMLDiffAnalyzer:
    def __init__(self, set_a_dir: str = None, set_b_dir: str = None, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.set_a_dir = Path(set_a_dir) if set_a_dir else Path(self.config['dataset_paths']['set_a'])
        self.set_b_dir = Path(set_b_dir) if set_b_dir else Path(self.config['dataset_paths']['set_b'])
        self.changes: List[XMLChange] = []
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration if file not found
            return {
                "dataset_paths": {"set_a": "data/set_a", "set_b": "data/set_b"},
                "focused_diff": {"context_words": 2, "min_word_length": 3, "ignore_case": True}
            }
    
    def get_xml_path(self, element, root) -> str:
        """Generate XPath-like string for an element"""
        path_parts = []
        current = element
        
        # Build path from element to root
        while current != root and current is not None:
            tag = current.tag
            # Add attributes if they help identify the element
            if 'id' in current.attrib:
                tag += f"[@id='{current.attrib['id']}']"
            elif 'name' in current.attrib:
                tag += f"[@name='{current.attrib['name']}']"
            elif 'type' in current.attrib:
                tag += f"[@type='{current.attrib['type']}']"
            
            path_parts.insert(0, tag)
            current = current.getparent() if hasattr(current, 'getparent') else None
        
        return "/" + "/".join(path_parts) if path_parts else "/"
    
    def element_to_string(self, element) -> str:
        """Convert XML element to string representation"""
        if element is None:
            return ""
        return ET.tostring(element, encoding='unicode', method='xml').strip()
    
    def get_element_text_content(self, element) -> str:
        """Get the text content of an element including all child text"""
        if element is None:
            return ""
        
        text_parts = []
        if element.text:
            text_parts.append(element.text.strip())
        
        for child in element:
            child_text = self.get_element_text_content(child)
            if child_text:
                text_parts.append(child_text)
            if child.tail:
                text_parts.append(child.tail.strip())
        
        return " ".join(text_parts).strip()
    
    def get_focused_changes(self, old_text: str, new_text: str) -> str:
        """Extract specific word changes with context for better readability"""
        if not old_text and not new_text:
            return ""
        
        if not old_text:
            return f"ADDED: {new_text[:100]}..."
        
        if not new_text:
            return f"REMOVED: {old_text[:100]}..."
        
        # Split into words for comparison
        old_words = re.findall(r'\S+', old_text)
        new_words = re.findall(r'\S+', new_text)
        
        # Use difflib to find differences
        differ = difflib.SequenceMatcher(None, old_words, new_words)
        changes = []
        
        context_words = self.config.get('focused_diff', {}).get('context_words', 2)
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'replace':
                # Get context around the change
                start_context = max(0, i1 - context_words)
                end_context = min(len(old_words), i2 + context_words)
                
                old_context = ' '.join(old_words[start_context:i1]) + ' [' + ' '.join(old_words[i1:i2]) + '] ' + ' '.join(old_words[i2:end_context])
                new_context = ' '.join(new_words[max(0, j1 - context_words):j1]) + ' [' + ' '.join(new_words[j1:j2]) + '] ' + ' '.join(new_words[j2:min(len(new_words), j2 + context_words)])
                
                changes.append(f"CHANGED: '{old_context.strip()}' → '{new_context.strip()}'")
                
            elif tag == 'delete':
                # Get context around deletion
                start_context = max(0, i1 - context_words)
                end_context = min(len(old_words), i2 + context_words)
                
                context = ' '.join(old_words[start_context:i1]) + ' [' + ' '.join(old_words[i1:i2]) + '] ' + ' '.join(old_words[i2:end_context])
                changes.append(f"REMOVED: '{context.strip()}'")
                
            elif tag == 'insert':
                # Get context around insertion
                start_context = max(0, j1 - context_words)
                end_context = min(len(new_words), j2 + context_words)
                
                context = ' '.join(new_words[start_context:j1]) + ' [' + ' '.join(new_words[j1:j2]) + '] ' + ' '.join(new_words[j2:end_context])
                changes.append(f"ADDED: '{context.strip()}'")
        
        return ', '.join(changes) if changes else "No specific word changes detected"
    
    def compare_elements(self, elem_a, elem_b, file_id: str, root_a, root_b):
        """Compare two XML elements and record changes"""
        if elem_a is None and elem_b is None:
            return
        
        xml_path = ""
        section_id = file_id
        
        # Handle new elements (ADD)
        if elem_a is None and elem_b is not None:
            xml_path = self.get_xml_path(elem_b, root_b)
            change = XMLChange(
                file_id=file_id,
                change_type="ADD",
                section_id=section_id,
                xml_path=xml_path,
                old_content="",
                new_content=self.element_to_string(elem_b)
            )
            self.changes.append(change)
            return
        
        # Handle deleted elements (DELETE)
        if elem_a is not None and elem_b is None:
            xml_path = self.get_xml_path(elem_a, root_a)
            change = XMLChange(
                file_id=file_id,
                change_type="DELETE",
                section_id=section_id,
                xml_path=xml_path,
                old_content=self.element_to_string(elem_a),
                new_content=""
            )
            self.changes.append(change)
            return
        
        # Handle modified elements (MODIFY)
        if elem_a is not None and elem_b is not None:
            xml_path = self.get_xml_path(elem_a, root_a)
            
            # Compare attributes
            if elem_a.attrib != elem_b.attrib:
                old_attrs = str(elem_a.attrib)
                new_attrs = str(elem_b.attrib)
                change = XMLChange(
                    file_id=file_id,
                    change_type="MODIFY",
                    section_id=section_id,
                    xml_path=xml_path + "/@attributes",
                    old_content=old_attrs,
                    new_content=new_attrs
                )
                self.changes.append(change)
            
            # Compare text content
            old_text = self.get_element_text_content(elem_a)
            new_text = self.get_element_text_content(elem_b)
            
            if old_text != new_text:
                focused_changes = self.get_focused_changes(old_text, new_text)
                change = XMLChange(
                    file_id=file_id,
                    change_type="MODIFY",
                    section_id=section_id,
                    xml_path=xml_path,
                    old_content=old_text,
                    new_content=new_text,
                    focused_changes=focused_changes
                )
                self.changes.append(change)
    
    def compare_xml_files(self, file_a: Path, file_b: Path) -> None:
        """Compare two XML files and record all changes"""
        file_id = file_a.stem
        
        try:
            tree_a = ET.parse(file_a)
            root_a = tree_a.getroot()
        except Exception as e:
            print(f"Error parsing {file_a}: {e}")
            return
        
        try:
            tree_b = ET.parse(file_b)
            root_b = tree_b.getroot()
        except Exception as e:
            print(f"Error parsing {file_b}: {e}")
            return
        
        # Compare root elements first
        self.compare_elements(root_a, root_b, file_id, root_a, root_b)
        
        # Get all elements from both trees for detailed comparison
        all_elements_a = {self.get_xml_path(elem, root_a): elem for elem in root_a.iter()}
        all_elements_b = {self.get_xml_path(elem, root_b): elem for elem in root_b.iter()}
        
        # Find all unique paths
        all_paths = set(all_elements_a.keys()) | set(all_elements_b.keys())
        
        for path in all_paths:
            elem_a = all_elements_a.get(path)
            elem_b = all_elements_b.get(path)
            
            # Skip if we already compared at root level
            if path == "/document":
                continue
                
            self.compare_elements(elem_a, elem_b, file_id, root_a, root_b)
    
    def find_matching_files(self) -> List[Tuple[Path, Path]]:
        """Find matching XML files between set_a and set_b"""
        files_a = {f.name: f for f in self.set_a_dir.glob("*.xml")}
        files_b = {f.name: f for f in self.set_b_dir.glob("*.xml")}
        
        matching_pairs = []
        
        # Find common files
        common_files = set(files_a.keys()) & set(files_b.keys())
        for filename in common_files:
            matching_pairs.append((files_a[filename], files_b[filename]))
        
        # Handle files only in set_b (new files)
        new_files = set(files_b.keys()) - set(files_a.keys())
        for filename in new_files:
            matching_pairs.append((None, files_b[filename]))
        
        # Handle files only in set_a (deleted files)
        deleted_files = set(files_a.keys()) - set(files_b.keys())
        for filename in deleted_files:
            matching_pairs.append((files_a[filename], None))
        
        return matching_pairs
    
    def analyze_changes(self) -> None:
        """Analyze all changes between set_a and set_b"""
        matching_files = self.find_matching_files()
        
        for file_a, file_b in matching_files:
            if file_a is None:  # New file
                file_id = file_b.stem
                try:
                    tree_b = ET.parse(file_b)
                    root_b = tree_b.getroot()
                    change = XMLChange(
                        file_id=file_id,
                        change_type="ADD",
                        section_id=file_id,
                        xml_path="/document",
                        old_content="",
                        new_content=self.element_to_string(root_b)
                    )
                    self.changes.append(change)
                except Exception as e:
                    print(f"Error processing new file {file_b}: {e}")
            
            elif file_b is None:  # Deleted file
                file_id = file_a.stem
                try:
                    tree_a = ET.parse(file_a)
                    root_a = tree_a.getroot()
                    change = XMLChange(
                        file_id=file_id,
                        change_type="DELETE",
                        section_id=file_id,
                        xml_path="/document",
                        old_content=self.element_to_string(root_a),
                        new_content=""
                    )
                    self.changes.append(change)
                except Exception as e:
                    print(f"Error processing deleted file {file_a}: {e}")
            
            else:  # Compare existing files
                self.compare_xml_files(file_a, file_b)
    
    def export_to_csv(self, output_file: str) -> None:
        """Export all changes to CSV format with approval dropdown options"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file_id', 'change_type', 'section_id', 'xml_path', 'old_content', 'new_content', 'focused_changes', 'approved']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for change in self.changes:
                # Set approved column with dropdown options format
                approved_options = "approved,rejected,pending"
                
                writer.writerow({
                    'file_id': change.file_id,
                    'change_type': change.change_type,
                    'section_id': change.section_id,
                    'xml_path': change.xml_path,
                    'old_content': change.old_content,
                    'new_content': change.new_content,
                    'focused_changes': change.focused_changes,
                    'approved': approved_options
                })
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of changes"""
        summary = {}
        for change in self.changes:
            change_type = change.change_type
            summary[change_type] = summary.get(change_type, 0) + 1
        return summary


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Legacy mode: explicit paths provided
        set_a_dir = sys.argv[1]
        set_b_dir = sys.argv[2]
        output_csv = sys.argv[3]
        analyzer = XMLDiffAnalyzer(set_a_dir, set_b_dir)
    elif len(sys.argv) == 2:
        # Config mode: only output file provided
        output_csv = sys.argv[1]
        analyzer = XMLDiffAnalyzer()  # Will use config file
    else:
        print("Usage: python xml_diff_analyzer.py [<set_a_dir> <set_b_dir>] <output_csv>")
        print("  With config file: python xml_diff_analyzer.py <output_csv>")
        print("  Direct paths: python xml_diff_analyzer.py <set_a_dir> <set_b_dir> <output_csv>")
        sys.exit(1)
    
    analyzer.analyze_changes()
    analyzer.export_to_csv(output_csv)
    
    summary = analyzer.get_summary()
    print(f"Analysis complete. Found {len(analyzer.changes)} total changes:")
    for change_type, count in summary.items():
        print(f"  {change_type}: {count}")
    print(f"Results saved to: {output_csv}")