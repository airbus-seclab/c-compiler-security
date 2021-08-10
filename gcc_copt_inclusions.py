#!/usr/bin/env python3
# https://gcc.gnu.org/onlinedocs/gccint/Option-file-format.html#Option-file-format


import argparse
import logging
import re
from enum import Enum

class State(Enum):
    INIT = 1
    LANGUAGE = 2
    ENUM = 3
    ENUM_VALUE = 4
    OPTION = 5
    OPTION_HELP = 6
    IGNORE = 1000

def parse_properties_string(s):
    res = {}
    r = re.compile(r"([^( ]+(?:\(.*?\))?)")
    name_val_r = re.compile(r"([^( ]+)(\(.*?\))?")
    try:
        for v in r.findall(s):
            k, v = name_val_r.search(v).groups()
            if v:
                res[k] = v[1:-1]
            else:
                res[k] = None
    except TypeError as e:
        raise RuntimeError("Invalid properties string: "+s) from e
    return res

class GCCOption():
    def __init__(self, name, props):
        self.name = name
        self.props = parse_properties_string(props)
        self.aliases = []
        self.enabled_by = []
        self.enables = []
        self.help = ""

    def __str__(self):
        return "-%s {%r}" % (self.name, self.props)

    def __repr__(self):
        return str(self)

    def is_alias(self):
        return "Alias" in self.props.keys()

    def get_alias_target(self):
        if self.is_alias():
            return self.props['Alias'].split(',')[0]
        return None

    def is_enabled_by(self):
        keys = self.props.keys()
        return "EnabledBy" in keys or "LangEnabledBy" in keys

    def get_enabled_by(self, lang="C"):
        # TODO: handle && and ||
        res = []
        if "EnabledBy" in self.props.keys():
            res.append(self.props['EnabledBy'])

        if "LangEnabledBy" in self.props.keys():
            lang_args = self.props['LangEnabledBy'].split(',')
            if len(lang_args) > 2:
                lang_args = lang_args[0:2]
            if len(lang_args) > 1:
                langs, opt = lang_args
                if lang in langs:
                    res.append(opt.strip(' '))
        if res:
            return res
        return None

    def pretty_print(self):
        print("Option:", self.name)
        if self.is_alias():
            print("\tAlias:", self.props["Alias"])
        if self.is_enabled_by():
            print("\tEnabledBy", self.props.get('EnabledBy', ''))
            print("\tLangEnabledBy", self.props.get('LangEnabledBy', ''))
        if self.enables:
            print("\tEnables:", ", ".join(self.enables))
        print("\tHelp:", self.help)

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
parser.add_argument('arg', nargs='*', help='Arg to display details of')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='verbose operations')

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

state = State.INIT
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
            state = State.INIT
            current_option = None
            continue
        if state == State.INIT:
            if l in Ignored_options:
                state = State.IGNORE
            elif l == "Language":
                state = State.LANGUAGE
            elif l == "Enum":
                state = State.ENUM
            elif l == "EnumValue":
                state = State.ENUM_VALUE
            else:
                state = State.OPTION
                current_option = l
        elif state in (State.IGNORE, ):
            logging.debug("Ignoring line")
            # Ignore line
            continue
        elif state == State.OPTION_HELP:
            options[current_option].help += l+"\n"
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
            opt = GCCOption(current_option, l)
            logging.debug("%r", opt)
            options[current_option] = opt
            state = State.OPTION_HELP
        else:
            raise RuntimeError("Invalid STATE "+str(state))

# Consolidate options
to_del = []
for name, opt in options.items():
    # Aliases are added to the real option, then deleted
    alias_target = opt.get_alias_target()
    if alias_target:
        options[alias_target].aliases.append(name)
        to_del.append(name)
        continue
    enabled_by = opt.get_enabled_by()
    if enabled_by:
        for en in enabled_by:
            if "&&" not in en and "||" not in en:
                options[en].enables.append(name)

for arg in args.arg:
    options[arg].pretty_print()
