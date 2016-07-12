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

 `python3 Full\ Compendium.xml rpg_cards.json` 

You can also specify one or more `-c` options to hand pick which categories you want
to convert.  See the online help for category names. By default you will get all
supported categories, which is currently only 'item'.

 `python3 Full\ Compendium.xml rpg_cards.json -c item -c spell` 

You can also populate the 'Tags' field by specifiyng one or more '-t <tag name>'
options. The tags are visible in RPG Card and you can use that app's filter
ability to narrow the list of cards you want printed.

 `python3 Full\ Compendium.xml rpg_cards.json -t source -t 

Tags currently supported:

* source: include the source book's initals (i.e. Players Handbook = ph)
* property: include item's properties
* type: include item type

Note:
 Python3 is required because python2 provides some problems with unicode symbols :)

## General

You're welcome to any comments and commits.
