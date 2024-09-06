"""
Enhanced XML File Modification Script with lxml and Configurable Options
------------------------------------------------------------------------

This script parses and modifies XML files in a specified input directory based on
rules provided in a config.json file. The script handles both regular nodes and 
XML attributes using XPath. It can validate XML against a schema, recover from 
errors, handle CDATA sections, and format the output XML based on configuration.
For each processed XML file, a corresponding .log file is generated containing 
details about the changes applied or skipped.

Features:
- Dynamic handling of XML nodes and attributes using lxml.
- Optional XML schema validation.
- Error recovery for malformed XML.
- CDATA section handling.
- Pretty-printing of XML output.
- Logs for each processed XML file.

Requirements:
- Python 3.x
- lxml library for enhanced XML processing
- A valid config.json file with the modification rules.

Developer:  Duane Robinson
Date: 09/06/2024

Usage:
- Place the script, the config.json, and the XML files in the appropriate directories.
- Run the script using `python xml_modifier.py`.
"""

import os
import json
from lxml import etree

def load_config(config_path):
    """
    Load the configuration JSON file.
    
    Parameters:
    config_path (str): The path to the configuration file.

    Returns:
    dict: The loaded configuration as a Python dictionary.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def validate_xml_with_schema(tree, schema_path, log_file):
    """
    Validate the given XML tree against an XML schema (XSD).
    
    Parameters:
    tree (ElementTree): The XML tree to validate.
    schema_path (str): The path to the XML schema file (.xsd).
    log_file (file): The log file to write validation results.

    Returns:
    bool: True if the XML is valid, False otherwise.
    """
    try:
        with open(schema_path, 'rb') as schema_file:
            schema_root = etree.XML(schema_file.read())
            schema = etree.XMLSchema(schema_root)
            schema.assertValid(tree)
            log_file.write(f"XML is valid according to schema {schema_path}\n")
            return True
    except etree.DocumentInvalid as e:
        log_file.write(f"XML validation failed: {str(e)}\n")
        return False

def parse_and_modify_xml(file_path, mappings, log_file, namespaces=None, handle_cdata=False):
    """
    Parse an XML file and modify it according to the given mappings using lxml.
    
    Parameters:
    file_path (str): The path to the XML file to be processed.
    mappings (list): A list of mapping rules from the config file.
    log_file (file): The log file to write details about the process.
    namespaces (dict): A dictionary of namespaces, if needed.
    handle_cdata (bool): Whether to handle CDATA sections explicitly.

    Returns:
    tree (ElementTree): The modified XML tree.
    modified (bool): Whether any modifications were made to the XML file.
    """
    parser = etree.XMLParser(recover=True)  # Recover from broken XML if configured
    tree = etree.parse(file_path, parser)
    root = tree.getroot()

    modified = False  # To track if any changes were made

    # Iterate over all mappings to apply the specified modifications
    for mapping in mappings:
        xpath = mapping['xpath']
        current_value = mapping['current_value']
        new_value = mapping.get('new_value', current_value)  # Default new_value to current_value if not provided
        
        # Find the node(s) using lxml's robust XPath support with optional namespaces
        nodes = root.xpath(xpath, namespaces=namespaces)

        if nodes:
            for node in nodes:
                # Handle CDATA sections
                if handle_cdata and isinstance(node, etree.CDATA):
                    log_file.write(f"Modifying CDATA section in {xpath}: {current_value} -> {new_value}\n")
                    node.text = etree.CDATA(new_value)
                    modified = True
                # Handle elements
                elif isinstance(node, etree._Element):
                    if node.text == current_value:
                        log_file.write(f"Modifying element {xpath}: {current_value} -> {new_value}\n")
                        node.text = new_value
                        modified = True
                    elif node.text == new_value:
                        log_file.write(f"No change needed for {xpath}: current value already matches new value '{new_value}'\n")
                    else:
                        log_file.write(f"Current value of element {xpath} ('{node.text}') does not match expected '{current_value}', skipping modification.\n")
                # Handle direct text results from XPath (e.g., when querying text nodes directly)
                elif isinstance(node, str):
                    if node == current_value:
                        log_file.write(f"Modifying text node {xpath}: {current_value} -> {new_value}\n")
                        parent_node = root.xpath(f"{xpath}/..")[0]  # Get the parent node to modify the text
                        parent_node.text = new_value
                        modified = True
                    elif node == new_value:
                        log_file.write(f"No change needed for text node {xpath}: current value already matches new value '{new_value}'\n")
                    else:
                        log_file.write(f"Current value of text node {xpath} ('{node}') does not match expected '{current_value}', skipping modification.\n")
        else:
            log_file.write(f"Node or attribute for {xpath} not found in the XML structure.\n")

    return tree, modified

def process_xml_files(config):
    """
    Process all XML files in the input directory and save modified files.
    
    Parameters:
    config (dict): The configuration dictionary loaded from config.json.
    """
    input_dir = config['input_directory']
    output_dir = config['output_directory']
    mappings = config['mappings']
    namespaces = config.get('namespaces', None)  # Load namespaces if provided
    handle_cdata = config.get('handle_cdata', False)  # Handle CDATA sections if enabled

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all XML files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.xml'):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)
            log_file_path = os.path.join(output_dir, filename.replace('.xml', '.log'))

            # Open the log file for this XML file
            with open(log_file_path, 'w') as log_file:
                log_file.write(f"Processing file: {filename}\n")
                
                # Parse and modify the XML file using lxml
                tree, modified = parse_and_modify_xml(input_file_path, mappings, log_file, namespaces, handle_cdata)

                # Validate XML if schema validation is enabled
                if config.get('schema_validation', {}).get('enabled', False):
                    schema_path = config['schema_validation']['schema_path']
                    schema_valid = validate_xml_with_schema(tree, schema_path, log_file)
                    if not schema_valid:
                        log_file.write(f"Skipping saving of {filename} due to schema validation failure\n")
                        continue

                if modified:
                    # Write the modified XML to the output directory with pretty-print and optional encoding
                    tree.write(output_file_path, pretty_print=config.get('pretty_print', False), 
                               xml_declaration=True, encoding=config.get('output_format', {}).get('encoding', 'UTF-8'))
                    log_file.write(f"Modified XML saved to {output_file_path}\n")
                else:
                    log_file.write(f"No changes made to {filename}\n")

if __name__ == "__main__":
    """
    Main entry point for the script. Loads the configuration and processes the XML files.
    """
    # Load the configuration from config.json
    config = load_config('config.json')

    # Process XML files based on the loaded configuration
    process_xml_files(config)
