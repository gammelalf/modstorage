#!/usr/bin/python3

import argparse

import modlib


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
        for mod in pack['mods']:
            print(mod)
    if args.fix:
        modlib.pack_fix_missing(pack)


def mod(args):
    if args.new:
        modlib.new_mod(args.mod)
    mod = modlib.get_mod(args.mod)
    if args.c:
        mod['curse_page'] = args.c
        modlib.write_mod(mod)
    if args.get:
        if mod['curse_page']:
            if args.v:
                import curselib
                jar = curselib.download_mod(mod['curse_page']+'/files', args.v)
                modlib.mod_add_version(mod, args.v, jar)
            else:
                args.parser.error('option -v is required')
        else:
            args.parser.error('missing curseforge page')
    elif args.add:
        if args.v:
            modlib.mod_add_version(mod, args.v, args.add)
        else:
            args.parser.error('option -v is required')
    if args.d:
        if args.v:
            _check_dependencies(args.d)
            modlib.mod_add_dependencies(mod, args.v, *args.d)
        else:
            args.parser.error('option -v is required')


def main():
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('-l', '--list', action='store_true',
                             help='list all mods in the storage')
    main_parser.set_defaults(func=storage)
    subparsers = main_parser.add_subparsers()

    mod_parser = subparsers.add_parser('mod')
    mod_parser.add_argument('mod',
                            help='mod to work on')
    mod_parser.add_argument('-n', '--new', action='store_true',
                            help='create a new mod')
    mod_parser.add_argument('-c', metavar='url',
                            help='set url to curseforge')
    group = mod_parser.add_mutually_exclusive_group()
    group.add_argument('-g', '--get', action='store_true',
                       help='download a version from curseforge')
    group.add_argument('-a', '--add', metavar='file',
                       help='add a version from a file')
    mod_parser.add_argument('-v', metavar='version',
                            help='minecraft version, required for -a, -d, -g')
    mod_parser.add_argument('-d', metavar='dependency', nargs='+',
                            help='add dependencies')
    mod_parser.set_defaults(func=mod, parser=mod_parser)

    pack_parser = subparsers.add_parser('pack')
    pack_parser.add_argument('pack')
    pack_parser.add_argument('-l', '--list', action='store_true',
                             help='list all mods in the pack')
    pack_parser.add_argument('-a', '--add', metavar='mod',
                             help='add a mod to the pack')
    pack_parser.add_argument('-f', '--fix', action='store_true',
                             help='fix the pack\'s missing dependencies')
    pack_parser.add_argument('-n', '--new', metavar='version',
                             help='create a new pack')
    pack_parser.set_defaults(func=pack, parser=pack_parser)

    args = main_parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
