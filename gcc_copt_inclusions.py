#!/usr/bin/env python3
# https://gcc.gnu.org/onlinedocs/gccint/Option-file-format.html#Option-file-format


import argparse
import sys
import logging
import re
from enum import Enum

languages = []

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
        self.raw_props = props.strip("\n ")
        self.props = parse_properties_string(props)
        self.aliases = []
        self.enabled_by = []
        self.enables = []
        self.help = ""
        self.langs = self.props.get("LangEnabledBy", "").split(',')[0].split(' ') or []

    def __str__(self):
        return "-%s {%r}" % (self.name, self.props)

    def __repr__(self):
        return str(self)

    def is_valid_for_lang(self, lang):
        return "Common" in self.props.keys() or lang in self.langs

    def is_warning(self):
        return not self.is_alias() and "Warning" in self.props.keys()

    def is_alias(self):
        return "Alias" in self.props.keys()

    def get_alias_target(self):
        if self.is_alias():
            return self.props['Alias'].split(',')[0]
        return None

    def is_enabled_by(self):
        keys = self.props.keys()
        return "EnabledBy" in keys or "LangEnabledBy" in keys

    def is_by_default(self):
        # TODO: less hackish
        return "Var(" in self.raw_props and "Init(1)" in self.raw_props and "Range" not in self.raw_props

    def get_enabled_by(self):
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
                res.append(opt.strip(' '))
        if res:
            return res
        return None

    def pretty_print(self):
        print("Option:", self.name, "[DEFAULT ON]" if self.is_by_default() else "")
        if self.is_alias():
            print("\tAlias:", self.props["Alias"])
        if self.is_enabled_by():
            e = self.props.get('EnabledBy', None)
            if e:
                print("\tEnabledBy", e)
            e = self.props.get('LangEnabledBy', None)
            if e:
                print("\tLangEnabledBy", e)
        if self.enables:
            print("\tEnables:", ", ".join(self.enables))
        print("\tHelp:", self.help)#.rstrip())
        print("\t"+self.raw_props)

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
parser.add_argument('--warn-not-enabled', action='store_true', help="List warnings not enabled by -Wall and -Wextra")
parser.add_argument('--lang', help="Restrict to this language")
parser.add_argument('-v', '--verbose', action='store_true', help='verbose operations')

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

state = State.INIT
current_option = None

Ignored_options = ['TargetSave', 'Variable', 'TargetVariable', 'HeaderInclude', 'SourceInclude']

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
            options[current_option].help += l
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
            # Skip already defined options
            # TODO: check which definition is the best ?
            if current_option not in options:
                opt = GCCOption(current_option, l)
                logging.debug("%r", opt)
                options[current_option] = opt
                state = State.OPTION_HELP
            else:
                state = State.IGNORE
        else:
            raise RuntimeError("Invalid STATE "+str(state))

# Consolidate options
for name, opt in options.items():
    # Aliases are added to the real option, then deleted
    alias_target = opt.get_alias_target()
    if alias_target:
        try:
            options[alias_target].aliases.append(name)
        except KeyError:
            print(f"Error: could not find Alias target '{alias_target}', check for typo")
            sys.exit(1)
        continue
    enabled_by = opt.get_enabled_by()
    if enabled_by:
        for en in enabled_by:
            if "&&" not in en and "||" not in en:
                options[en].enables.append(name)

def get_enabled_by_recursive(opt, res=[]):
    if opt.is_enabled_by():
        en_by = opt.get_enabled_by()
        for o in en_by:
            res.append(o)
            if "&&" not in o and "||" not in o:
                get_enabled_by_recursive(options[o], res)
        return res
    return res

if args.warn_not_enabled:
    for name, opt in options.items():
        if opt.is_warning() and not opt.is_by_default() and name not in ("Wextra", "Wall"):
            if opt.is_enabled_by():
                en_by = get_enabled_by_recursive(opt)
                if "Wextra" in en_by or "Wall" in en_by:
                    continue
            opt.pretty_print()
else:
    for arg in args.arg:
        p = re.compile(arg)
        for found_opt in filter(lambda x: p.match(x), options.keys()):
            options[found_opt].pretty_print()
