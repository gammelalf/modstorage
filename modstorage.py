#!/usr/bin/python3

import argparse

import modlib


def _check_dependencies(deps):
    for mod in deps:
        if mod not in modlib.STORED_MODS:
            raise modlib.ModNotInStorage(mod)


def none(args):
    pass


def add(args):
    _check_dependencies(args.dependencies)
    mod = modlib.get_mod(args.mod)
    url = ''
    # if args.url:
    #     url = args.url
    modlib.add_version(mod, args.version, args.jar, url)
    if len(args.dependencies):
        modlib.add_dependencies(mod, args.version, *args.dependencies)


def get(args):
    _check_dependencies(args.dependencies)
    mod = modlib.get_mod(args.mod)
    if mod['curse_page']:
        import curselib
        jar = curselib.download_mod(mod['curse_page']+'/files', args.version)
        modlib.add_version(mod, args.version, jar)
        if len(args.dependencies):
            modlib.add_dependencies(mod, args.version, *args.dependencies)
    else:
        raise NotImplementedError('Get only with curseforge url implemented')


def new(args):
    if args.mod in modlib.STORED_MODS:
        raise modlib.ModAlreadyInStorage
    if args.curse_page:
        modlib.new_mod(args.mod, args.curse_page)
    else:
        modlib.new_mod(args.mod)


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


def main():
    main_parser = argparse.ArgumentParser()
    main_parser.set_defaults(func=none)
    subparsers = main_parser.add_subparsers()

    new_parser = subparsers.add_parser('new', description='Add a new mod to \
                                                           the storage')
    new_parser.add_argument('mod')
    new_parser.add_argument('curse_page', nargs='?')
    new_parser.set_defaults(func=new)

    add_parser = subparsers.add_parser('add', description='Add a version to \
                                                           a mod')
    add_parser.add_argument('mod')
    add_parser.add_argument('version')
    add_parser.add_argument('jar')
    add_parser.add_argument('dependencies', nargs='*')
    add_parser.set_defaults(func=add)

    get_parser = subparsers.add_parser('get', description='Download from \
                                                           curseforge and add \
                                                           a version to a mod')
    get_parser.add_argument('mod')
    get_parser.add_argument('version')
    get_parser.add_argument('dependencies', nargs='*')
    get_parser.set_defaults(func=get)

    pack_parser = subparsers.add_parser('pack', description='Work on packs')
    pack_parser.add_argument('pack')
    pack_parser.add_argument('-l', '--list', action='store_true')
    pack_parser.add_argument('-a', '--add', metavar='mod')
    pack_parser.add_argument('-f', '--fix', action='store_true')
    pack_parser.add_argument('-n', '--new', metavar='version')
    pack_parser.set_defaults(func=pack)

    args = main_parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
