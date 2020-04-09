#!/usr/bin/python3

import argparse, os
from zipfile import ZipFile

from modlib.mod import Mod
from modlib.pack import Pack
from modlib.base import valid_version


def storage(args):
    raise NotImplementedError
    if args.list:
        for mod in modlib.STORED_MODS:
            print(mod)


def pack(args):
    pack = Pack(args.pack, *args.new)
    if args.add:
        pack.add(args.add)
    if args.remove:
        pack.remove(args.remove)
    if args.clean:
        pack.autoremove()
    if args.list:
        for mod in pack.mods:
            print(mod)


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

    if args.read:
        if args.v:
            with Zipfile() as jar:
                with jar.open("mcmod.info") as info:
                    for key, value in json.load(info)[0].items():
                        mod.set(key, value, args.v)
        else:
            args.parser.error("option -v is required")
    mod.write()


def main():
    # Define some type functions for argparse
    def minecraft_version(string):
        valid_version(string)
        return string

    def directory(string):
        if os.path.exists(string) and os.path.isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    # Main parser
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument("-l", "--list", action="store_true",
                             help="list all mods in the storage")
    main_parser.set_defaults(func=storage)
    subparsers = main_parser.add_subparsers()

    # Mod parser
    mod_parser = subparsers.add_parser("mod")
    mod_parser.add_argument("mod")
    mod_parser.add_argument("-n", "--new", action="store_true",
                            help="create a new mod")
    mod_parser.add_argument("-a", "--add",  metavar="file",
                            help="add a version from a file")
    mod_parser.add_argument("-r", "--read", action="store_true",
                            help="Experimental! Read the mcmod.info")
    mod_parser.add_argument("-v", metavar="version", default=None,
                            type=minecraft_version,
                            help="minecraft version")
    mod_parser.add_argument("-d", metavar="mod", nargs="+",
                            help="add dependencies")
    mod_parser.set_defaults(func=mod, parser=mod_parser)

    # Pack parser
    pack_parser = subparsers.add_parser("pack")
    pack_parser.add_argument("pack")
    pack_parser.add_argument("-l", "--list", action="store_true",
                             help="list all mods in the pack")
    pack_parser.add_argument("-a", "--add", metavar="mod", type=Mod,
                             help="add a mod to the pack")
    pack_parser.add_argument("-r", "--remove", metavar="mod", type=Mod,
                             help="remove a mod from the pack")
    pack_parser.add_argument("-c", "--clean", action="store_true",
                             help="remove obsolete mods")
    pack_parser.add_argument("-n", "--new", metavar=("directory", "version"),
                             nargs=2, default=[],
                             help="create a new pack")
    pack_parser.set_defaults(func=pack, parser=pack_parser)

    # Parse and process
    args = main_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
