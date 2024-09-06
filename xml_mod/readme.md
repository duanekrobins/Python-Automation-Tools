# XML File Modification Script

## Overview

This script allows users to parse and modify XML files in a specified directory based on rules defined in a `config.json` file. It uses the `lxml` library for enhanced XML parsing, XPath querying, schema validation, error recovery, CDATA handling, and pretty-printing of the modified XML files.

For each XML file processed, a log file is generated containing the details of the changes made or skipped. The modified XML files are saved to an output directory specified in the configuration.

## Features

- Dynamic XPath-based modifications of XML nodes and attributes using `lxml`.
- Error recovery for malformed XML files.
- Optional schema validation using XML Schema Definition (XSD).
- Support for modifying CDATA sections.
- Namespace handling for complex XML structures.
- Pretty-printing for human-readable XML output.
- Logs generated for each processed XML file.

## Prerequisites

### Required Software

- **Python 3.x**: Ensure Python 3 is installed. Download it [here](https://www.python.org/downloads/).
- **lxml Library**: Install the `lxml` library using pip:

  ```bash
  pip install lxml
### Required Files

- **config.json**: A configuration file defining input/output directories, XML modifications, and additional options.
- **Input XML Files**: XML files to be processed by the script.
- **Optional XML Schema (XSD)**: If schema validation is required.

## Script Usage

### Step 1: Prepare the Configuration (`config.json`)

Create a `config.json` file that defines the following settings:

- `input_directory`: Path to the directory containing the XML files to modify.
- `output_directory`: Path where the modified XML files and logs will be saved.
- `pretty_print`: Set to `true` for pretty-printing the XML output.
- `handle_cdata`: Set to `true` to handle and modify CDATA sections.
- `error_recovery`: Set to `true` to allow the script to recover from malformed XML.
- `schema_validation`: Provide the path to the XSD file if validation is needed.
- `namespaces`: Define namespaces used in the XML structure for XPath queries.
- `mappings`: Define the XPath queries to target nodes or attributes for modification.

### Example `config.json` File:
```json
{
  "input_directory": "C:/path/to/input/xml/files",
  "output_directory": "C:/path/to/output/xml/files",
  "pretty_print": true,
  "handle_cdata": true,
  "error_recovery": true,
  "schema_validation": {
    "enabled": true,
    "schema_path": "C:/path/to/schema.xsd"
  },
  "namespaces": {
    "ns": "http://example.com/ns"
  },
  "mappings": [
    {
      "xpath": "./AMS_DOCUMENT/@DOC_CAT",
      "current_value": "JV",
      "new_value": "JV_NEW"
    },
    {
      "xpath": "./AMS_DOCUMENT/JV_DOC_HDR/DOC_TYP",
      "current_value": "JV",
      "new_value": "JV_NEW_TYPE"
    },
    {
      "xpath": "./AMS_DOCUMENT/JV_DOC_HDR/DOC_NM[CDATA]",
      "current_value": "<![CDATA[Some Data]]>",
      "new_value": "<![CDATA[New Data]]>"
    }
  ]
}
```
### Step 2: Running the Script

Once the `config.json` file is set up and the input XML files are ready, run the script with:

```bash
python xml_modifier.py
```
### Script Workflow

1. **Load Configuration**: Reads the `config.json` file to load settings, mappings, and paths.
2. **Process XML Files**: Iterates over all XML files in the `input_directory` and applies the XPath-based mappings to modify nodes or attributes.
3. **Error Recovery**: If `error_recovery` is enabled, the script will attempt to recover from malformed XML files.
4. **Schema Validation**: If enabled, the script will validate each XML file against the XSD schema.
5. **Log Generation**: A `.log` file is generated for each processed file, recording details of the changes.
6. **Output**: The modified XML files are saved to the `output_directory` with pretty-printing and encoding, if configured.

### Step 3: Reviewing Output and Logs

#### Output XML Files:
The modified XML files will be saved in the `output_directory`. If `pretty_print` is enabled, the output XML will be formatted for readability.

#### Log Files:
A `.log` file will be generated for each XML file processed. These log files include:

- Modified nodes or attributes.
- Skipped modifications if the current value doesn’t match the expected value.
- Any errors encountered, such as validation issues or missing nodes.

#### Example Log Entry:

```bash
Processing file: 150JVA05_V18.xml
Modifying node ./AMS_DOCUMENT/@DOC_CAT: JV -> JV_NEW
Modifying node ./AMS_DOCUMENT/JV_DOC_HDR/DOC_TYP: JV -> JV_NEW_TYPE
Modifying CDATA section in ./AMS_DOCUMENT/JV_DOC_HDR/DOC_NM[CDATA]: <![CDATA[Some Data]]> -> <![CDATA[New Data]]>
Modified XML saved to C:/path/to/output/xml/files/150JVA05_V18.xml
```
### Advanced Usage and Options

1. **Schema Validation**:  
   To ensure the modified XML files conform to a specific XML Schema (XSD), enable schema validation in the `config.json` file:
   
   ```json
   "schema_validation": {
     "enabled": true,
     "schema_path": "C:/path/to/schema.xsd"
   }
   ```
2. **CDATA Handling**:  
   Modify content within CDATA sections by setting `handle_cdata` to `true`. Use an XPath that targets nodes with CDATA content:

   ```json
   {
     "xpath": "./AMS_DOCUMENT/JV_DOC_HDR/DOC_NM[CDATA]",
     "current_value": "<![CDATA[Some Data]]>",
     "new_value": "<![CDATA[New Data]]>"
   }
   ```
3. **Namespace Handling**:  
   If your XML files use namespaces, define them in `config.json`:

   ```json
   "namespaces": {
     "ns": "http://example.com/ns"
   }
   ```
  Reference namespaces in XPath queries:
```json
{
  "xpath": "//ns:AMS_DOCUMENT/ns:JV_DOC_HDR/ns:DOC_TYP",
  "current_value": "JV",
  "new_value": "JV_NEW_TYPE"
}
```
4. **Error Recovery**:
Enable error recovery in config.json to handle malformed XML files:
```json
"error_recovery": true
```
### FAQs

- **What happens if I run the script multiple times on the same files?**  
  The script will re-apply modifications. If the current value already matches the new value, no changes will be made.

- **Can I validate my XML files against a DTD?**  
  The script currently supports validation against XSD (XML Schema Definition). DTD validation can be added if needed.

- **What if some XML files are malformed?**  
  If `error_recovery` is enabled, the script will attempt to parse and recover as much of the malformed XML as possible.

- **Can I process large XML files?**  
  Yes, `lxml` is efficient and can handle large XML files, but ensure sufficient memory if dealing with extremely large datasets.

- **How do I handle repeated nodes?**  
  XPath can target all matching nodes. For repeated nodes, the script will modify each matching node. No need to specify indices unless targeting a specific instance.

