#!/usr/bin/env python3

"""
find out the stop words in crkeng.xml's translations
"""
import argparse
import re
from collections import Counter
from pprint import pprint
from typing import List
from xml.etree import ElementTree as ET

parser = argparse.ArgumentParser(
    description="find out the stop words in crkeng.xml's translations"
)
parser.add_argument("crkeng_file")

if __name__ == "__main__":
    word_pattern = re.compile(r"[\w.\-/']+")
    args = parser.parse_args()
    root = ET.parse(str(args.crkeng_file)).getroot()
    elements = root.findall(".//t")
    translations = {e.text.lower() for e in elements if e.text is not None}

    words: List[str] = [
        word
        for translation in translations
        for word in re.findall(word_pattern, translation)
    ]
    print("result is case insensitive:")
    pprint(Counter(words).most_common(100))

"""
result on CreeDictionary/res/dictionaries/crkeng_cw_md_200314.xml 
[('s/he', 17963),
 ('is', 5010),
 ('s.o.', 4665),
 ('a', 4647),
 ('it', 4255),
 ('s.t.', 3385),
 ('he', 2605),
 ('the', 2566),
 ('of', 2090),
 ('to', 2030),
 ('in', 2022),
 ('has', 1464),
 ('for', 1394),
 ('things', 1233),
 ('with', 1228),
 ('by', 1201),
 ('or', 1136),
 ('people', 1083),
 ('on', 1064),
 ('makes', 999),
 ('e.g.', 867),
 ('as', 859),
 ('his/her', 712),
 ('one', 685),
 ('from', 672),
 ('at', 615),
 ('my', 569),
 ('up', 561),
 ('out', 532),
 ('an', 523),
 ('they', 517),
 ('and', 510),
 ('it/him', 498),
 ('him/herself', 475),
 ('off', 474),
 ('there', 435),
 ('own', 422),
 ('something', 394),
 ('him', 390),
 ('takes', 382),
 ('goes', 374),
 ('down', 360),
 ('water', 356),
 ('about', 355),
 ('into', 329),
 ('small', 320),
 ('being', 317),
 ('another', 309),
 ('it.', 306),
 ('all', 304),
 ('so', 301),
 ('him.', 301),
 ('looks', 289),
 ('over', 285),
 ('pulls', 284),
 ('puts', 280),
 ('are', 275),
 ('literally', 262),
 ('thus', 260),
 ('cree', 253),
 ('hand', 252),
 ('good', 246),
 ('little', 227),
 ('thinks', 221),
 ('together', 219),
 ('well', 215),
 ('that', 214),
 ('gives', 214),
 ("s.o.'s", 214),
 ('away', 211),
 ('way', 209),
 ('gets', 207),
 ('back', 201),
 ('holds', 200),
 ('cuts', 198),
 ('be', 194),
 ('.', 190),
 ('breaks', 189),
 ('runs', 185),
 ('through', 185),
 ('his', 182),
 ('places', 181),
 ('around', 179),
 ('place', 178),
 ('time', 174),
 ('comes', 167),
 ('animate', 166),
 ('does', 166),
 ('bad', 165),
 ('head', 165),
 ('not', 163),
 ('person', 162),
 ('throws', 158),
 ('long', 156),
 ('many', 156),
 ('such', 155),
 ('along', 154),
 ('uses', 150),
 ('speaks', 147),
 ('moves', 146)]
"""
