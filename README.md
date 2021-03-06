### scripts for pulling genome metadata and enzyme lists from JGI

**REQUIRED**: need to have chromedriver installed and located in script directory

**DESCRIPTION**: a set of scripts for pulling genomes from JGI or from "all" (which would still be using JGI as homepage). Archaea, bacteria, eukarya, and metagenomes are pulled separately

**OUTPUT**: a .json file containing genome/metagenome metadata and the associated enzyme list (E.C. list)

example call:
  python scrape_eukarya_from_jgi.py save_directory

**note**: scripts are part of the ecg package written by Harrison B. Smith for ELIFE: https://github.com/ELIFE-ASU/ecg
eukarya and metagenome scripts adapted for python3 and archaea and bacteria scripts created by Dylan C. Gagler on 5/6/2019
