#!/usr/bin/python3

import argparse, os
from zipfile import ZipFile

from modlib import Mod, Pack
from modlib.base import config, valid_version


def storage(args):
    if args.config:
        if os.path.exists(".modlib.config"):
            raise FileExistsError(".modlib.config")
        with open(".modlib.config", "w") as f:
            f.write(config.DEFAULT)


def main():
    def minecraft_version(string):
        valid_version(string)
        return string

    # Init Parser
    parser = argparse.ArgumentParser()
    mod = parser.add_argument_group("mod-commands")
    pack = parser.add_argument_group("pack-commands")

    # Optional Arguments
    parser.add_argument("--version",
                        type=minecraft_version,
                        help="Use this version in commands")
    parser.add_argument("--mod",
                        type=Mod,
                        help="Use existing mod in commands")
    parser.add_argument("--pack",
                        type=Pack,
                        help="Use existing pack in commands")

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

    # Execute Mod Commands
    if args.new_mod:
        args.mod = Mod.new_mod(args.new_mod)
    if args.add_file:
        args.mod.set_file(args.add_file, args.version)
    if args.add_dependencies:
        if args.version and args.mod.get("dependencies") is args.mod.get("dependencies", args.version):
            args.mod.set("dependencies", [], args.version)
        args.mod.get("dependencies", args.version).extend(args.add_dependencies)
    if args.read:
        with Zipfile() as jar:
            with jar.open("mcmod.info") as info:
                for key, value in json.load(info)[0].items():
                    mod.set(key, value, args.version)
    if args.mod:
        args.mod.write()

    # Execute Pack Commands
    if args.new_pack:
        args.pack = Pack(*args.new_pack, args.version)
    if args.add:
        args.pack.add(args.mod)
    if args.remove:
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
