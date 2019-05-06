## jgi_eukarya_scraping
"""
Scrape individual archaea EC numbers from JGI.
`scrape_archaea_from_jgi` is the only function meant to be called directly.

Usage:
  scrape_archaea_from_jgi.py SAVE_DIR
  scrape_archaea_from_jgi.py SAVE_DIR [--database=<db>]
  scrape_archaea_from_jgi.py SAVE_DIR [--homepage=<hp>]
  scrape_archaea_from_jgi.py SAVE_DIR [--write_concatenated_json=<wj>]


Arguments:
  SAVE_DIR  directory to write jsons to (no \ required after name)

Options:
  --database=<db>    Database to use, either 'jgi' or 'all' [default: jgi]
  --homepage=<hp>    url of jgi homepage [default: https://img.jgi.doe.gov/cgi-bin/m/main.cgi]
  --write_concatenated_json=<wj>     write single concatenated json after all individual jsons are written [default: True]
"""

from selenium import webdriver
import time
import os
import re
import json
from docopt import docopt
from ast import literal_eval
from bs4 import BeautifulSoup

def activate_driver():
    """
    Activate chrome driver used to automate webpage navigation (see: https://sites.google.com/a/chromium.org/chromedriver/)
    The chrome driver .exec file must be in the home directory

    :returns: driver [object]
    """
    homedir = os.path.expanduser('~')
    return webdriver.Chrome(homedir+'/chromedriver')

def get_archaea_url_from_jgi_img_homepage(driver,homepage_url,database='jgi'):
    """
    load homepage_url -> retrieve archaea_url

    :param driver: the chrome driver object
    :param homepage_url: url of the jgi homepage. should be 'https://img.jgi.doe.gov/cgi-bin/m/main.cgi' as of 6/15/2017
    :param database: choose to use only the jgi database, or all database [default=jgi]
    :returns: url of the eukarya database page
    """

    driver.get(homepage_url)
    time.sleep(5)
    htmlSource = driver.page_source

    ## All ampersands (&) must be followed by 'amp;'
    if database == 'jgi':
        regex = r'href=\"main\.cgi(\?section=TaxonList&amp;page=taxonListAlpha&amp;domain=Archaea&amp;seq_center=jgi)\"'
    elif database == 'all':
        regex = r'href=\"main\.cgi(\?section=TaxonList&amp;page=taxonListAlpha&amp;domain=Archaea)\"'
    else:
        raise ValueError("Database must be 'jgi' or 'all'")

    match = re.search(regex, htmlSource)
    archaea_suffix = match.group(1)
    archaea_url = homepage_url+archaea_suffix

    return archaea_url

def get_archaea_json_from_archaea_url(driver,archaea_url):
    """
    load archaea_url- > retrieve archaea_json_url -> load archaea_json_url -> retrieve archaea_json

    :param driver: the chrome driver object
    :param archaea_url: url of archaea database
    :returns: json containing urls of each individual archaea
    """

    driver.get(archaea_url)
    time.sleep(5)
    htmlSource = driver.page_source
    # driver.quit()

    regex = r'var myDataSource = new YAHOO\.util\.DataSource\(\"(.*)\"\);'
    match = re.search(regex, htmlSource)
    archaea_json_suffix = match.group(1)
    archaea_url_prefix = archaea_url.split('main.cgi')[0]
    archaea_json_url = archaea_url_prefix+archaea_json_suffix

    driver.get(archaea_json_url)
    time.sleep(5)
    # jsonSource = driver.page_source

    ## convert the jsonSource into a dict of dicts here
    archaea_json = json.loads(driver.find_element_by_tag_name('body').text)

    return archaea_json


def get_archaea_urls_from_archaea_json(driver,homepage_url,archaea_json):
    """
    parse archaea_json -> retrieve archaea_urls

    :param driver: the chrome driver object
    :param homepage_url: url of the jgi homepage. should be 'https://img.jgi.doe.gov/cgi-bin/m/main.cgi' as of 6/15/2017
    :param archaea_json: json text of archaea
    :returns: list of all archaea urls
    """

    all_GenomeNameSampleNameDisp =  [d['GenomeNameSampleNameDisp'] for d in archaea_json['records']]

    archaea_urls = list()

    for htmlandjunk in all_GenomeNameSampleNameDisp:
        regex = r"<a href='main\.cgi(.*)'>"
        match = re.search(regex, htmlandjunk)
        html_suffix = match.group(1)
        full_url = homepage_url+html_suffix
        archaea_urls.append(full_url)

    return archaea_urls

def get_archaea_htmlSource_and_metadata(driver, archaea_url):
    """
    load archaea_url -> retrieve archaea_htmlSource & metadata

    :param driver: the chrome driver object
    :param archaea_url: url for an single archaeon
    :returns: html source of single archaeon, all metadata for that archaeon
    """

    driver.get(archaea_url)
    time.sleep(5)
    archaea_htmlSource = driver.page_source

    metadata_table_dict = get_archaea_metadata_while_on_archaea_page(archaea_htmlSource)

    return archaea_htmlSource, metadata_table_dict


def get_enzyme_url_from_archaea_url(archaea_url, archaea_htmlSource):

    """
    archaea_htmlSource -> parse out enzyme_url

    :param driver: the chrome driver object
    :param archaea_url: url for an single archaeon
    :returns: url of a single archaeon's enzyme page
    """


    regex = r'<a href=\"(main\.cgi\?section=TaxonDetail&amp;page=enzymes&amp;taxon_oid=\d*)\"'
    match = re.search(regex, archaea_htmlSource)

    print("Getting enzyme_url from Archaeon url: %s"%(archaea_url))

    enzyme_url_suffix = match.group(1)
    enzyme_url_prefix = archaea_url.split('main.cgi')[0]
    enzyme_url = enzyme_url_prefix+enzyme_url_suffix

    return enzyme_url


def get_archaea_metadata_while_on_archaea_page(htmlSource):
    """
    htmlSource -> dictionary of archaeon metadata

    :param htmlSource: the archaea_url driver's .page_source
    :returns: all metadata from a archaeon's html
    """

    # return dict of metagenome table data
    bs = BeautifulSoup(htmlSource,"html.parser")
    metadata_table = bs.findAll('table')[0]

    metadata_table_dict = dict()
    for row in metadata_table.findAll('tr'):

        if (len(row.findAll('th')) == 1) and (len(row.findAll('td')) == 1):

            row_key = row.findAll('th')[0].text.rstrip()
            row_value = row.findAll('td')[0].text.rstrip() if row.findAll('td')[0] else None
            metadata_table_dict[row_key] = row_value

    metadata_table_dict.pop('Project Geographical Map', None)

    ## metadata_table_dict['Taxon Object ID'] should be the way we identify a metagenome

    return metadata_table_dict

def get_enzyme_json_from_enzyme_url(driver,enzyme_url):
    """
    load enzyme_url -> retrieve enzyme_json_url -> load enzyme_json_url -> retrieve enzyme_json

    :param driver: the chrome driver object
    :param enzyme_url: url for an single enzyme type from an single eukaryote
    :returns: json of single archaeon's enzyme data
    """

    driver.get(enzyme_url)
    time.sleep(5)
    htmlSource = driver.page_source
    # driver.quit()

    regex = r'var myDataSource = new YAHOO\.util\.DataSource\(\"(.*)\"\);'
    match = re.search(regex, htmlSource)
    enzyme_json_suffix = match.group(1)
    enzyme_url_prefix = enzyme_url.split('main.cgi')[0]
    enzyme_json_url = enzyme_url_prefix+enzyme_json_suffix

    driver.get(enzyme_json_url)
    time.sleep(5)
    # jsonSource = driver.page_source

    ## convert the jsonSource into a dict of dicts here
    enzyme_json = json.loads(driver.find_element_by_tag_name('body').text)

    return enzyme_json

def parse_enzyme_info_from_enzyme_json(enzyme_json):
    """
    load enzyme_json -> return ec dict

    :param enzyme_json: json of a single archaeaon's enzyme data
    :returns: dict of a single eukaryote (key=ec,value=[enzymeName,genecount])
    """

    enzyme_dict = dict() # Dictionary of ec:[enzymeName,genecount] for all ecs in a single metagenome

    for i, singleEnzymeDict in enumerate(enzyme_json['records']):
        ec = singleEnzymeDict['EnzymeID']
        enzymeName = singleEnzymeDict['EnzymeName']
        genecount = singleEnzymeDict['GeneCount']

        enzyme_dict[ec] = [enzymeName,genecount]

    return enzyme_dict

def write_concatenated_json(save_dir,jgi_archaea):
    """
    write single json of all eukaryote data

    :param save_dir: dir where each single_eukaryote_dict.json is saved to
    :param jgi_eukarya: dict of single_eukaryote_dicts. Used to write single json.
    """

    print("Writing concatenated json to file...")

    concatenated_fname = save_dir+'_concatenated.json'

    with open(concatenated_fname, 'w') as outfile:

        json.dump(jgi_archaea,outfile)

    print("Done.")

def scrape_archaea_from_jgi(save_dir,homepage_url='https://img.jgi.doe.gov/cgi-bin/m/main.cgi',database='jgi',write_concatenated_json=True):

    driver = activate_driver()

    jgi_archaea = list()

    print("Scraping all archaea genomes ...")

    archaea_url = get_archaea_url_from_jgi_img_homepage(driver,homepage_url,database=database)

    archaea_json = get_archaea_json_from_archaea_url(driver,archaea_url)

    archaea_urls = get_archaea_urls_from_archaea_json(driver,homepage_url,archaea_json) ### gets SINGLE archaea urls as opposed to all, i think

    for archaea_url in archaea_urls:

        print("Scraping archaea: %s ..."%archaea_url)

        archaea_htmlSource, metadata_table_dict = get_archaea_htmlSource_and_metadata(driver, archaea_url)

        single_archaea_dict = {'metadata':metadata_table_dict}

        taxon_id = metadata_table_dict['Taxon ID']

        enzyme_url = get_enzyme_url_from_archaea_url(archaea_url, archaea_htmlSource)

        enzyme_json = get_enzyme_json_from_enzyme_url(driver,enzyme_url)

        enzyme_dict = parse_enzyme_info_from_enzyme_json(enzyme_json)

        single_archaea_dict['genome'] = enzyme_dict

        jgi_archaea.append(single_archaea_dict)

        with open(save_dir+'/'+taxon_id+'.json', 'w') as outfile:

            json.dump(single_archaea_dict,outfile)

        print("Done scraping archaeon.")
        print("-"*80)

    print("Done scraping archaea.")
    print("="*90)

    if write_concatenated_json:

        write_concatenated_json(save_dir,jgi_archaea)

## Can i write it so that it scrapes many at a time?

if __name__ == '__main__':
    arguments = docopt(__doc__, version='scrape_archaea_from_jgi 1.0')

    if not os.path.exists(arguments['SAVE_DIR']):
        os.makedirs(arguments['SAVE_DIR'])

    scrape_archaea_from_jgi(arguments['SAVE_DIR'],
        homepage_url=arguments['--homepage'],
        database=arguments['--database'],
        write_concatenated_json=literal_eval(arguments['--write_concatenated_json']))
