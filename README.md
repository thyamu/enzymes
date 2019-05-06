### README for genome scraping scripts

need to have chromedriver installed and located in script directory

a set of scripts for pulling genomes from JGI or from "all" (which would still be using JGI as homepage)

pulls archaea, bacteria, eukarya, and metagenomes separately

outputs a .json file containing genome/metagenome metadata and the associated enzyme list (E.C. list)

example call:
  python scrape_eukarya_from_jgi.py save_directory


scripts are part of the ecg package written by Harrison B. Smith for ELIFE
eukarya and metagenome scripts adapted for python3 and archaea and bacteria scripts created by Dylan C. Gagler on 5/6/2019
