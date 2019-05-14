import requests
from xml.etree import ElementTree


def download_mod(url, version):
    '''
    Download mod for version from
        https://minecraft.curseforge.com/projects/<mod>/files

    :param url:
    :param version: minecraft version
    '''
    options = get_options(url)
    if version not in options.keys():
        raise RuntimeError('Given version is not available')
    url += '?filter-game-version='+options[version]
    url = get_download(url)
    return download_url(url)


def get_options(url):
    '''
    Read available versions from
        https://minecraft.curseforge.com/projects/<mod>/files

    :param url:
    :returns: dict containing available versions and their php representation
    '''
    # Get page
    with requests.get(url) as r:
        html = str(r.content)

    # Rough filter to decrease parser's load
    start = html.find('<select id="filter-game-version"')
    end = html.find('</select>', start)+9
    select = html[start:end]

    # Tidy up
    select = select.replace('\\r', '\r')
    select = select.replace('\\n', '\n')

    # Parse XML
    options = {}
    root = ElementTree.fromstring(select)
    for child in root.getchildren():
        if not child.text.startswith('\\xc2\\xa0'):
            continue
        text = child.text.replace('\\xc2\\xa0', '')
        if isversion(text):
            options[text] = child.attrib['value']
    return options


def get_download(url):
    '''
    Get download link from
        [...]/projects/<mod>/files?filter-game-version=<version>

    :param url:
    '''
    # Get page
    with requests.get(url) as r:
        html = str(r.content)

    # Rough filter to decrease parser's load
    start = html.find('<div class="project-file-download-button">')
    end = html.find('</div>', start)+6
    div = html[start:end]

    # Tidy up
    div = div.replace('\\r', '\r')
    div = div.replace('\\n', '\n')

    # Parse XML
    root = ElementTree.fromstring(div)
    return 'https://minecraft.curseforge.com'+root.find('a').attrib['href']


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
