import json
import os
import sys


class ModAlreadyInStorage(Exception):
    pass


class ModNotInStorage(Exception):
    pass


class ModAlreadyInPack(Exception):
    pass


class ModNotInPack(Exception):
    pass


with open(os.path.join(sys.path[0], './config.json')) as f:
    CONFIG = json.load(f)

# STORED_MODS(list<str>): names of mods stored in storage
with open('{}/stored_mods.json'.format(CONFIG['path'])) as f:
    STORED_MODS = json.load(f)

# LOADED_MODS(dict<str, dict>): mods already loaded
LOADED_MODS = {}


def path(name, file=''):
    '''
    Generate the path to a mod

    :param name: mod's name
    :param file: file inside mod's directory (optional)
    '''
    if file:
        return os.path.join(CONFIG['path'],
                            name.lower().replace(' ', '_'),
                            file)
    else:
        return os.path.join(CONFIG['path'],
                            name.lower().replace(' ', '_'))


def adv_path(mod, mc_v, key):
    '''
    Generate the path to a mod's file

    :param mod: dict representing the mod
    :param mc_v: minecraft version
    :param key: file to access ('link'/ 'jar')
    '''
    return path(mod['name'], mod['versions'][mc_v][key])


# -- MOD FUNCTIONS -- #

def new_mod(name, curse_page=''):
    '''
    Create a new mod
    Also save the mod to the filesystem

    :param name: the mod's name
    :param curse_page: url to the mod's curseforge page
    :returns: dict representing the mod
    :raises ModAlreadyInStorage:
    '''
    if name in STORED_MODS:
        raise ModAlreadyInStorage(name)

    STORED_MODS.append(name)
    with open('{}/stored_mods.json'.format(CONFIG['path']), 'w') as f:
        json.dump(STORED_MODS, f)

    LOADED_MODS[name] = {}
    LOADED_MODS[name]['versions'] = {}
    LOADED_MODS[name]['name'] = name
    LOADED_MODS[name]['curse_page'] = curse_page
    os.mkdir(path(name))
    write_mod(name)

    return LOADED_MODS[name]


def mod_add_version(mod, mc_v, file, url=''):
    '''
    Add a java-file to a mod for a specific version
    Add the version to the mod's dict

    :param mod: dict representing the mod
    :param mc_v: minecraft version
    :param file: path to the java-file
    :param url:
    '''
    if not os.path.isfile(file):
        raise IOError('File {} not found'.format(file))

    mod['versions'][mc_v] = {}
    mod['versions'][mc_v]['jar'] = os.path.basename(file)
    os.rename(file, adv_path(mod, mc_v, 'jar'))
    mod['versions'][mc_v]['link'] = mod['name']+' v'+mc_v+'.jar'
    os.symlink(os.path.abspath(adv_path(mod, mc_v, 'jar')),
               adv_path(mod, mc_v, 'link'))
    mod['versions'][mc_v]['url'] = url
    mod['versions'][mc_v]['deps'] = []
    write_mod(mod)


def mod_update_version(mod, mc_v, file, url=''):
    '''
    Add a java-file to a mod replaceing an existing one

    :param mod: dict representing the mod
    :param mc_v: minecraft version
    :param file: path to the java-file
    :param url:
    '''
    mod['versions'][mc_v]['jar'] = os.path.basename(file)
    os.rename(file, adv_path(mod, mc_v, 'jar'))
    os.symlink(os.path.abspath(adv_path(mod, mc_v, 'jar')),
               adv_path(mod, mc_v, 'link'))
    mod['versions'][mc_v]['url'] = url
    write_mod(mod)


def mod_add_dependencies(mod, mc_v, dep, *deps):
    '''
    Add a dependency for a mod's version

    :param mod: dict representing the mod
    :param mc_v: minecraft version
    :param dep: dependency to add (optional multiple)
    '''
    if dep not in STORED_MODS:
        raise ModNotInStorage(dep)

    mod['versions'][mc_v]['deps'].append(dep)
    write_mod(mod)

    for d in deps:
        mod_add_dependencies(mod, mc_v, d)


def write_mod(name):
    if isinstance(name, dict):
        name = name['name']
    with open(path(name, 'mod.json'), 'w') as f:
        json.dump(LOADED_MODS[name], f)


def read_mod(name):
    with open(path(name, 'mod.json')) as f:
        LOADED_MODS[name] = json.load(f)
    return LOADED_MODS[name]


def get_mod(name):
    '''
    Get a mod from the storage

    Mods already read in a session are stored in LOADED_MODS.
    This function trys to retrieve the mod from there.
    If this fails it try read it from filesystem.

    :param name: mod's name
    '''
    try:
        return LOADED_MODS[name]
    except KeyError:
        if name in STORED_MODS:
            return read_mod(name)
        else:
            raise ModNotInStorage(name)


# -- PACK FUNCTIONS -- #

def new_pack(path, version):
    '''
    Create a pack

    :param path: path where pack is created
    :param version: version pack is created for
    :returns: dict representing the pack
    '''
    if not os.path.isdir(path):
        raise NotADirectoryError('Can\'t create pack')
    if os.path.isfile(os.path.join(path, 'pack.json')):
        raise IOError('pack.json already exists')
    pack = {}
    pack['path'] = os.path.abspath(path)
    pack['version'] = version
    pack['mods'] = []
    write_pack(pack)
    return pack


def pack_add_mod(pack, mod, rewrite=True):
    '''
    Add a mod to a pack

    :param pack: dict representing the pack
    :param mod: str or dict representing the mod
    :param rewrite: whether write_pack() is called (default: True)
    :raises ModAlreadyInPack:
    :raises ValueError: mod's and pack's version don't match
    '''
    if isinstance(mod, str):
        mod = get_mod(mod)
    if not pack['version'] in mod['versions'].keys():
        raise ValueError('The mod\'s and the pack\'s versions don\'t match')
    if mod['name'] in pack['mods']:
        raise ModAlreadyInPack(mod['name'])

    pack['mods'].append(mod['name'])
    os.symlink(adv_path(mod, pack['version'], 'link'),
               os.path.join(pack['path'], mod['name']+'.jar'))
    if rewrite:
        write_pack(pack)


def pack_remove_mod(pack, name):
    '''
    Remove a mod from a pack

    :param pack: dict representing the pack
    :param name: mod's name (dict will also work)
    :raises ModNotInPack:
    '''
    if isinstance(name, dict):
        name = name['name']
    if name not in pack['mods']:
        raise ModNotInPack(name)

    pack['mods'].remove(name)
    os.remove(os.path.join(pack['path'], name+'.jar'))
    write_pack(pack)


def write_pack(pack):
    '''
    Write the dict representing a pack to a file
    The file is <path>/pack.json where path is stored in the dict

    :param pack: dict representing the pack
    '''
    with open(os.path.join(pack['path'], 'pack.json'), 'w') as f:
        json.dump(pack, f)


def read_pack(path):
    '''
    Read a pack from a file

    :param path: path to the file directly or the directory containing it
    '''
    if os.path.isdir(path):
        path = os.path.join(path, 'pack.json')
    with open(path) as f:
        return json.load(f)


def pack_get_missing(pack):
    '''
    Get a pack's missing dependencies

    :param pack: dict representing the pack
    :returns: list of missing mods' names
    '''
    missing = []
    for mod in pack['mods']:
        mod = get_mod(mod)
        for dep_name in mod['versions'][pack['version']]['deps']:
            if dep_name in pack['mods']:
                continue
            if dep_name in missing:
                continue
            missing.append(dep_name)
    return missing


def pack_fix_missing(pack):
    '''
    Add the missing dependencies to a pack

    :param pack: dict representing the pack
    '''
    missing = pack_get_missing(pack)
    if len(missing) == 0:
        return
    while len(missing) != 0:
        for mod in missing:
            pack_add_mod(pack, get_mod(mod), False)
        missing = pack_get_missing(pack)
    write_pack(pack)


# -- BUNDLE FUNCTIONS -- #

'''
A bundle is a list/ collection of mods.
It can be added as a whole to a pack.
'''


def pack_add_bundle(pack, bundle):
    '''
    Add a bundle's mods to a pack

    :param pack:
    :param bundle:
    '''
    for mod in bundle:
        if mod not in pack['mods']:
            pack_add_mod(pack, mod, False)
    write_pack(pack)
