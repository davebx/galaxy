#!/usr/bin/env python

import argparse
import os
import yaml
import xml.etree.ElementTree as ET

def parse_section(child, tool_path):
    tools = []
    for element in child:
        if element.tag == 'tool':
            tools.append(os.path.join(tool_path, parse_tool_entry(element)))
    return tools

def parse_tool_entry(element):
    return element.attrib.get('file', None)

def find_test_table_configs(tool_xml_path):
    configs = []
    tool_root = os.path.split(tool_xml_path)[0]
    for root, dirs, files in os.walk(tool_root):
        if 'tool_data_table_conf.xml.test' in files:
            configs.append(os.path.join(root, 'tool_data_table_conf.xml.test'))
    return configs

def fix_data_paths(xml_path, tool_path):
    table_entries = []
    if not os.path.exists(xml_path):
        return []
    dom = ET.parse(xml_path)
    root = dom.getroot()
    for table in root:
        if table.tag != 'table':
            continue
        table_name = table.get('name', None)
        for child in table:
            if child.tag != 'file':
                continue
            data_path = child.get('path', None)
            data_path = data_path.replace('${__HERE__}', tool_path)
            child.set('path', data_path)
        table_entries.append(table)
    return table_entries

def main(options):
    tool_paths = []
    tables = []
    data_tables = {}
    data_table_entry = {}
    if not os.path.exists(options.configfile):
        print('Configuration file %s does not exist' % options.configfile)
        return 1
    with open(options.configfile, 'r') as fh:
        yaml_data = yaml.load(fh, Loader=yaml.SafeLoader)
    if 'galaxy' not in yaml_data:
        print("Section 'galaxy' not found in configuration file %s, exiting." % options.configfile)
        return 1
    else:
        if 'shed_tool_config_file' not in yaml_data['galaxy']:
            shed_tool_conf = os.path.join(os.getcwd(), 'config', 'shed_tool_conf.xml')
        else:
            shed_tool_conf = os.path.join(os.getcwd(), 'config', yaml_data['galaxy']['shed_tool_config_file'])
    if not os.path.exists(shed_tool_conf):
        print('Shed tool configuration file %s does not exist' % shed_tool_conf)
        return 1
    shed_xml = ET.parse(shed_tool_conf)
    root = shed_xml.getroot()
    tool_path = root.attrib.get('tool_path', None)
    if tool_path is None:
        print('No tool path defined in %s' % shed_tool_conf)
    for child in root:
        if child.tag == 'section':
            tool_paths.extend(parse_section(child, tool_path))
        elif child.tag == 'tool':
            tool_paths.append(os.path.join(tool_path, parse_tool_entry(child)))
    for path in tool_paths:
        for data_table_config in find_test_table_configs(tool_path):
            data_table_entries = fix_data_paths(data_table_config, tool_path)
            tables.extend(data_table_entries)
    test_table = ET.Element('tables')
    for table in tables:
        test_table.insert(1, table)
    if os.path.exists(options.output) and not options.force:
        print('File %s exists and --force flag not present, exiting.' % options.output)
        return 1
    tree = ET.ElementTree(test_table)
    tree.write(options.output)
    print('%d data table entries written to %s' % (len(tables), options.output))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--configfile', '-c', action='store', dest='configfile', default='config/galaxy.yml', help='Path to galaxy.yml')
    parser.add_argument('--output', '-o', action='store', dest='output', default='config/test_tool_data_table_conf.xml', help='Output file for the test tool data configuration')
    parser.add_argument('--force', '-f', action='store_true', dest='force', default=False, help='Overwrite output file if it exists')
    options = parser.parse_args()
    exit(main(options))
