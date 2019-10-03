import requests
#from xml.etree import ElementTree


version_map = {'1.7.10': '2020709689:4449',
               '1.12.2': '2020709689:6756',
               '1.10.2': '2020709689:6170'}


def download_mod(url, version):
    '''
    Download mod for version from
        https://www.curseforge.com/minecraft/mc-mods/<mod>/files

    :param url:
    :param version: minecraft version
    '''
    #options = get_options(url)
    #if version not in options.keys():
    #    raise RuntimeError('Given version is not available')
    url += '?filter-game-version='+version_map[version]
    url = get_download(url)
    if url is None:
        raise RuntimeError('Given verison is not available')
    return download_url(url)


def get_download(url):
    '''
    Get download link from
        [...]/projects/<mod>/files?filter-game-version=<version>

    :param url:
    '''
    # Get page
    with requests.get(url) as r:
        html = str(r.content)

    # Find first download
    tag_start = '<a data-action="file-link" href="'
    start = html.find(tag_start)
    if start == -1:
        return None
    else:
        start += len(tag_start)
        end = html.find('"', start)

        return ('https://www.curseforge.com'+html[start:end]) \
               .replace('/files/', '/download/')+'/file'


# Simple Utilities
def download_url(url):
    '''
    Download url as file

    :param url:
    :returns: file name
    '''
    with requests.get(url, stream=True) as r:
        file_name = r.url.split('/')[-1]
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    # f.flush()
    return file_name


def isversion(string):
    '''
    Check if string has minecraft version's format

    :param string: to check
    :returns: whether correct format
    '''
    for c in string:
        if c == '.':
            continue
        if ord(c) >= ord('0') and ord(c) <= ord('9'):
            continue
        else:
            return False
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', metavar='version',
                        help='Get filter for version')
    args = parser.parse_args()

    if args.f:
        print('?filter-game-version='+version_map[args.f])


if __name__ == '__main__':
    main()
