#!/usr/bin/python

import argparse
import json
import sys


def read_file(filename):
    """
    read from file
    :param filename: the filename
    :return: the content of file
    """
    if filename is None:
        lines = []
        for line in sys.stdin:
            lines.append(line)
        return "\n".join(lines)
    else:
        with open(filename) as fp:
            return fp.read()


def write_file(content, filename):
    """
    write the content to the file
    :param content: the content
    :param filename: the file name
    :return: None
    """
    if filename is None:
        print(content)
    else:
        with open(filename, "w") as fp:
            fp.write(content)


def to_string(json_element, pretty):
    if isinstance(json_element, dict) or isinstance(json_element, list):
        return json.dumps(json_element, indent=2) if pretty else json.dumps(json_element)
    else:
        return json_element


def create_element(root, path):
    cur = root
    for name in path:
        if isinstance(cur, dict):
            if name not in cur:
                cur[name] = {}
            cur = cur[name]
        elif isinstance(cur, list):
            if not name.isdigit() or int(name) >= len(cur):
                cur.append({})
                cur = cur[-1]
            else:
                cur = cur[int(name)]
        else:
            return None
    return cur


def find_element(root, path):
    """
    find the element by its path
    :param root: the root element
    :param path: path array
    :return: the element or None
    """
    cur = root
    for name in path:
        if isinstance(cur, dict):
            if name in cur:
                cur = cur[name]
            else:
                return None
        elif isinstance(cur, list):
            if not name.isdigit() or int(name) >= len(cur):
                return None
            else:
                cur = cur[int(name)]
        else:
            return None
    return cur


def get_value(args):
    _get_value(args.input, args.key, args.pretty, args.output)


def _get_value(in_filename, path, pretty, out_filename):
    root = json.loads(read_file(in_filename))
    elements = path.split(".")
    cur = find_element(root, elements[0:-1])
    last_name = elements[-1]

    if cur is not None:
        if isinstance(cur, dict):
            if last_name in cur:
                write_file(to_string(cur[last_name]), out_filename)
        elif isinstance(cur, list):
            if last_name.isdigit() and int(last_name) < len(cur):
                write_file(to_string(cur[len(last_name)]), out_filename)


def _replace_value(in_filename, path, txt_value, json_value, out_filename):
    """
    replace the value of a json path
    :param in_filename: the input file name
    :param path: the json path
    :param txt_value: the text value
    :param json_value: the json value
    :param out_filename: the output file name
    :return: None
    """
    root = json.loads(read_file(in_filename))
    elements = path.split(".")
    cur = find_element(root, elements[:-1])
    last_name = elements[-1]

    if cur is not None and last_name in cur:
        if txt_value is not None:
            cur[last_name] = txt_value
        elif json_value is not None:
            cur[last_name] = json.loads(json_value)

    write_file(json.dumps(root, indent=2), out_filename)


def replace_value(args):
    _replace_value(args.input, args.key, args.txt_value, args.json_value, args.output)


def _add_value(in_filename, path, txt_value, json_value, out_filename):
    root = json.loads(read_file(in_filename))
    elements = path.split(".")
    cur = create_element(root, elements[:-1])
    last_name = elements[-1]

    if isinstance(cur, dict):
        if txt_value is not None:
            cur[last_name] = txt_value
        elif json_value is not None:
            cur[last_name] = json.loads(json_value)
    write_file(json.dumps(root, indent=2), out_filename)


def add_value(args):
    _add_value(args.input, args.key, args.txt_value, args.json_value, args.output)


def _del_value(in_filename, path, out_filename):
    root = json.loads(read_file(in_filename))
    elements = path.split(".")
    cur = find_element(root, elements[:-1])
    last_name = elements[-1]
    print(cur)
    if cur is not None:
        if isinstance(cur, dict) and last_name in cur:
            del cur[last_name]
        if isinstance(cur, list) and last_name.isdigit() and len(cur) > len(last_name):
            del cur[int(last_name)]
    write_file(json.dumps(root, indent=2), out_filename)


def del_value(args):
    _del_value(args.input, args.key, args.output)


def parse_args():
    parser = argparse.ArgumentParser(description="json edit tool")
    subparsers = parser.add_subparsers(description="sub commands")

    get_parser = subparsers.add_parser("get", help="get element value")
    get_parser.add_argument("--input", help="the input file")
    get_parser.add_argument("--output", help="the output file")
    get_parser.add_argument("--key", help="the key", required=True)
    get_parser.add_argument("--pretty", help="output in pretty format", action="store_true")
    get_parser.set_defaults(func=get_value)

    replace_parser = subparsers.add_parser("replace", help="replace element value")
    replace_parser.add_argument("--input", help="the input file")
    replace_parser.add_argument("--output", help="the output file")
    replace_parser.add_argument("--key", help="the key", required=True)
    replace_parser.add_argument("--txt-value", help="the plain text value")
    replace_parser.add_argument("--json-value", help="the value in json format")
    replace_parser.set_defaults(func=replace_value)

    add_parser = subparsers.add_parser("add", help="add element value")
    add_parser.add_argument("--input", help="the input file")
    add_parser.add_argument("--output", help="the output file")
    add_parser.add_argument("--key", help="the key", required=True)
    add_parser.add_argument("--txt-value", help="the plain text value")
    add_parser.add_argument("--json-value", help="the value in json format")
    add_parser.set_defaults(func=add_value)

    del_parser = subparsers.add_parser("del", help="delete element")
    del_parser.add_argument("--input", help="the input file")
    del_parser.add_argument("--output", help="the output file")
    del_parser.add_argument("--key", help="the key", required=True)
    del_parser.set_defaults(func=del_value)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
