#!/usr/bin/python3

import argparse

# import modlib

from mod import Mod
from base import valid_version

def minecraft_version(string):
    """
    Small wrapper for base.valid_version() to be given used as an argument type
    """
    valid_version(string)
    return string

def _check_dependencies(deps):
    for mod in deps:
        if mod not in modlib.STORED_MODS:
            raise modlib.ModNotInStorage(mod)


def storage(args):
    if args.list:
        for mod in modlib.STORED_MODS:
            print(mod)


def pack(args):
    if args.new:
        pack = modlib.new_pack(args.pack, args.new)
    else:
        pack = modlib.read_pack(args.pack)
    if args.add:
        modlib.pack_add_mod(pack, modlib.get_mod(args.add))
    if args.list:
        for mod in pack["mods"]:
            print(mod)
    if args.fix:
        modlib.pack_fix_missing(pack)


def mod(args):
    if args.new:
        Mod.new_mod(args.mod)
    mod = Mod(args.mod)
    if args.add:
        if args.v:
            mod.set_file(args.add, args.v)
        else:
            args.parser.error("option -v is required")
    if args.d:
        if args.v and mod.get("dependencies") is mod.get("dependencies", args.v):
            mod.set("dependencies", [], args.v)
        # TODO _check_dependencies(args.d)
        mod.get("dependencies", args.v).extend(args.d)
    mod.write()


def main():
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument("-l", "--list", action="store_true",
                             help="list all mods in the storage")
    main_parser.set_defaults(func=storage)
    subparsers = main_parser.add_subparsers()

    mod_parser = subparsers.add_parser("mod")
    mod_parser.add_argument("mod",
                            help="mod to work on")
    mod_parser.add_argument("-n", "--new", action="store_true",
                            help="create a new mod")
    mod_parser.add_argument("-a", "--add",  metavar="file",
                            help="add a version from a file")
    mod_parser.add_argument("-v", metavar="version", default=None,
                            type=minecraft_version,
                            help="minecraft version")
    mod_parser.add_argument("-d", metavar="mod", nargs="+",
                            help="add dependencies")
    mod_parser.set_defaults(func=mod, parser=mod_parser)

    pack_parser = subparsers.add_parser("pack")
    pack_parser.add_argument("pack")
    pack_parser.add_argument("-l", "--list", action="store_true",
                             help="list all mods in the pack")
    pack_parser.add_argument("-a", "--add", metavar="mod",
                             help="add a mod to the pack")
    pack_parser.add_argument("-f", "--fix", action="store_true",
                             help="fix the pack's missing dependencies")
    pack_parser.add_argument("-n", "--new", metavar="version",
                             help="create a new pack")
    pack_parser.set_defaults(func=pack, parser=pack_parser)

    args = main_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
