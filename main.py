#!/usr/bin/python3

import argparse
import os

from modlib import *


def main():
    # Init Parser
    parser = argparse.ArgumentParser()
    hidden = parser.add_argument_group("hidden-commands")
    mod = parser.add_argument_group("mod-commands")
    pack = parser.add_argument_group("pack-commands")

    # Optional Arguments
    parser.add_argument("--version",
                        type=Version,
                        help="Use this version in commands")
    parser.add_argument("--mod",
                        type=Mod,
                        help="Use existing mod in commands")
    parser.add_argument("--pack",
                        type=Pack,
                        help="Use existing pack in commands")

    # Hidden Commands
    hidden.add_argument("--list-mods",
                        action="store_true",
                        help=argparse.SUPPRESS)
    hidden.add_argument("--list-packs",
                        action="store_true",
                        help=argparse.SUPPRESS)

    # Mod Commands
    mod.add_argument("--new-mod",
                     metavar="NAME",
                     help="Create new mod")
    mod.add_argument("--add-file",
                     metavar="FILE",
                     help="Add a jar file")
    mod.add_argument("--add-dependencies",
                     nargs="+",
                     metavar="MOD",
                     help="Add dependencies")
    mod.add_argument("--read",
                     action="store_true",
                     help="Experimental! Read the mcmod.info")

    # Pack Commands
    pack.add_argument("--new-pack",
                      nargs=2,
                      metavar=("NAME", "DIR"),
                      help="Create new pack")
    pack.add_argument("--add",
                      action="store_true",
                      help="Add a mod to a pack")
    pack.add_argument("--remove",
                      action="store_true",
                      help="Remove a mod from a pack")
    pack.add_argument("--autoremove",
                      action="store_true",
                      help="See apt")
    pack.add_argument("--list",
                      action="store_true",
                      help="List mods")

    # Parse Arguments
    args = parser.parse_args()

    def check_version():
        """Check whether a version was specified"""
        if args.version is None:
            parser.error("argument --version is required")

    def check_mod():
        """Check whether a mod was specified"""
        if args.mod is None:
            parser.error("argument --mod is required")

    # Execture Hidden Commands
    if args.list_mods:
        mods = os.listdir(storage_path())
        print("\n".join(mods))
        return
    if args.list_packs:
        packs = os.listdir(packs_path())
        print("\n".join(packs))
        return

    # Execute Mod Commands
    if args.new_mod:
        args.mod = Mod.new_mod(args.new_mod)
    if args.add_file:
        check_mod()
        check_version()
        args.mod.set_file(args.add_file, args.version)
    if args.add_dependencies:
        check_mod()
        if args.version and args.mod.get("dependencies") is args.mod.get("dependencies", args.version):
            args.mod.set("dependencies", [], args.version)
        args.mod.get("dependencies", args.version).extend(args.add_dependencies)
    if args.read:
        parser.error("argument --read is not supported at the moment")
        with Zipfile() as jar:
            with jar.open("mcmod.info") as info:
                for key, value in json.load(info)[0].items():
                    mod.set(key, value, args.version)
    if args.mod:
        args.mod.write()

    # Execute Pack Commands
    if args.new_pack:
        check_version()
        args.pack = Pack(*args.new_pack, args.version)
    if args.add:
        check_mod()
        args.pack.add(args.mod)
    if args.remove:
        check_mod()
        args.pack.remove(args.mod)
    if args.autoremove:
        args.pack.autoremove()
    if args.list:
        for mod in args.pack.mods:
            print(mod)
    if args.pack:
        args.pack.write()


if __name__ == "__main__":
    main()
