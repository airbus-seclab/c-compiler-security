#!/usr/bin/env python
# https://gcc.gnu.org/onlinedocs/gccint/Option-file-format.html#Option-file-format


import argparse
import logging
import regex
from enum import Enum

class State(Enum):
    NONE = 1
    LANGUAGE = 2
    ENUM = 3
    ENUM_VALUE = 4
    OPTION = 5
    OPTION_HELP = 6
    IGNORE = 1000

def parse_properties_string(s):
    res = {}
    r = regex.compile(r"([^( ]+(?:\(.*?\))?)")
    name_val_r = regex.compile(r"([^( ]+)(\(.*?\))?")
    try:
        for v in r.findall(s):
            k, v = name_val_r.search(v).groups()
            if v:
                res[k] = v[1:-1]
            else:
                res[k] = None
    except TypeError:
        raise RuntimeError("Invalid properties string: "+s)
    return res

class GCCEnum():
    def __init__(self, s):
        enum_info = parse_properties_string(s)
        self.__name__ = enum_info['Name']
        self.__type__ = enum_info['Type']
        self.values = {}

    def __str__(self):
        return "Enum: %s / %s {%r}" % (self.__name__, self.__type__, self.values)

    def __repr__(self):
        return str(self)

parser = argparse.ArgumentParser(description='Parse GCC option definition file (.opt)')
parser.add_argument('file', help='The file to parse')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='verbose operations')

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

state = State.NONE
current_option = None

Ignored_options = ['TargetSave', 'Variable', 'TargetVariable', 'HeaderInclude', 'SourceInclude']

languages = []
enums = {}
options = {}
with open(args.file, "r") as f:
    for l in f.readlines():
        l = l.rstrip("\n")
        logging.debug("State : %r, current_option: '%s', line: '%s'", state, current_option, l)
        # Skip comment
        if len(l) and l[0] == ";":
            continue
        # Empty line, reset State
        if l == "":
            state = State.NONE
            current_option = None
            continue
        if state == State.NONE:
            if l in Ignored_options:
                state = state.IGNORE
            elif l == "Language":
                state = State.LANGUAGE
            elif l == "Enum":
                state = State.ENUM
            elif l == "EnumValue":
                state = State.ENUM_VALUE
            else:
                state = State.OPTION
                current_option = l
        elif state == state.IGNORE or state == state.OPTION_HELP:
            # Ignore line
            continue
        elif state == State.LANGUAGE:
            logging.debug('New language: %s',l)
            languages.append(l)
        elif state == State.ENUM:
            new_enum = GCCEnum(l)
            logging.debug('New Enum: %s',new_enum)
            enums[new_enum.__name__] = new_enum
        elif state == State.ENUM_VALUE:
            enum_value_info = parse_properties_string(l)
            enum_name = enum_value_info['Enum']
            enums[enum_name].values[enum_value_info['String']] = enum_value_info['Value']
        elif state == State.OPTION:
            # An option definition record. These records have the following fields:
            #    the name of the option, with the leading “-” removed
            #    a space-separated list of option properties (see Option properties)
            #    the help text to use for --help (omitted if the second field contains the Undocumented property).
            opt_props = parse_properties_string(l)
            logging.debug(opt_props)
            options[current_option] = opt_props
            state == State.OPTION_HELP
        else:
            raise RuntimeError("Invalid STATE "+str(state))
                
print(languages)
print(enums)
#print(options)
