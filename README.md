# Compendium-to-Card
Converting DnDAppFiles (XML) Compendiums to RPG Card (json)

## About

This project was made for convert [DnD 5 Ed. Not official Compendium] (https://github.com/ceryliae/DnDAppFiles) to [Crobi's RPG Cards generator] (https://github.com/crobi/rpg-cards).

## Setup

Install python dependencies with `pip install -r requirements.txt`

## Usage

Display the online help:

 `python3 ./compendium_to_card.py --help`

Basic conversion example.  This will convert all supported compendium categories.

 `python3 ./compendium_to_card.py ../DnDAppFiles/Items/Magic\ Items.xml rpg_cards.json` 

You can also specify one or more `-c` options to hand pick which categories you want
to convert.  See the online help for available category names.

 `python3 ./compendium_to_card.py Full\ Compendium.xml rpg_cards.json -c item -c spell` 

Yes, python3 is required because python2 provides some problems with unicode symbols :)

## Interactive Usage

You can now play around with the converted compendium objects in the python
REPL. This can be useful for various reasons, from targetting specific items to
print from just fooling around.

 ```python
 import json
 import compendium_to_card at ctc

 c = ctc.Compendium('sample.xml')
 darts = json.dumps([x.to_dict() for x in c.search_names('dart')])
 ```

## General

You're welcome to any comments and commits.
