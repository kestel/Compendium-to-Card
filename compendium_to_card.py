#!/usr/bin/env python3
'''
    It's a thing

'''

import argparse
from collections import defaultdict
import json
from string import capwords
import xml.etree.ElementTree as ET

import sys


ITEM_TYPES = {
    'HA':   'Heavy Armor',
    'MA':   'Medium Armor',
    'LA':   'Light Armor',
    'S':    'Shield',
    'M':    'Melee weapon',
    'R':    'Ranged weapon',
    'A':    'Ammunition',
    'RD':   'Rod',
    'ST':   'Staff',
    'WD':   'Wand',
    'RG':   'Ring',
    'P':    'Potion',
    'SC':   'Scroll',
    'W':    'Wondrous item',
    'G':    'Adventuring gear',
    '$':    'Money',
}

ITEM_PROPERTIES = {
    'V':    'Versatile',
    'L':    'Light',
    'T':    'Thrown',
    'A':    'Ammunition',
    'F':    'Finesse',
    'H':    'Heavy',
    'LD':   'Loading',
    'R':    'Reach',
    'S':    'Special',
    '2H':   'Two-handed',
}

ITEM_DAMAGE_TYPES = {
    'S':    "Slashing",
    'B':    "Bludgeoning",
    'P':    "Piercing",
}

# This maps an item's sub-element tag name to a function that receives the
# xml.etree.ElementTree element for processing. The functions are not expected
# fully process each element into it's final form, that is handled by further
# generators in the processing pipeline.
ITEM_ELEMENTS = {
    'modifier':
        lambda e:
        [e.get('category'), e.text],
    'property':
        lambda e:
        [ITEM_PROPERTIES.get(p, p) for p in e.text.split(',')],
    'weight':
        lambda e:
        e.text,
    'stealth':
        lambda e:
        True,
    'text':
        lambda e:
        None if e.text is None else e.text.strip(),
    'range':
        lambda e:
        e.text,
    'name':
        lambda e:
        e.text,
    'strength':
        lambda e:
        e.text,
    'type':
        lambda e:
        ITEM_TYPES.get(e.text, e.text),
    'ac':
        lambda e:
        e.text,
    'roll':
        lambda e:
        e.text,
    'dmg2':
        lambda e:
        e.text,
    'dmg1':
        lambda e:
        e.text,
    'dmgType':
        lambda e:
        ITEM_DAMAGE_TYPES.get(e.text, e.text),
}

# Create namespaces for gathering related category data under one roof
Item = type(
    'Item',
    (object,),
    {
        'types': ITEM_TYPES,
        'properties': ITEM_PROPERTIES,
        'damage_types': ITEM_DAMAGE_TYPES,
        'elements': ITEM_ELEMENTS,
    }
)


def property_tag(field):
    '''
    Process property field tags

    :param list field: should be the property field of a compendium object
    :rtype list:

    '''
    tags = list()
    for prop in field:
        if hasattr(prop, '__iter__') and not isinstance(prop, str):
            tags.extend(prop)
        else:
            tags.append(prop)

    return tags


# The keys in TAG_MAP are exposed as command line options for users to choose
# which ones they want to include in their rpg card JSON data. Once in the JSON,
# the tags can be used in filters within the rpgcard webui.
# Here, tags map to a 2-tuple of
#   (<XML field name>, <function applied to field to create tag data>).
# Usually the key name == field name, but not always.
# The tag functions MUST return an iterable.
TAG_MAP = {
    'source':
        ('text', lambda f: [sourcebook(source(f))]),
    'type':
        ('type', lambda f: [x for x in f]),
    'property':
        ('property', property_tag),
}


def source(text_list):
    '''
    Returns the line containing the word 'Source:' from a sequence of strings,
    or None if not found.

    :param iterable text_list:

    '''
    sourceline = None
    for line in text_list:
        if line is not None:
            if 'Source:' in line:
                sourceline = line.replace('Source:', '').strip()

    return sourceline


def sourcebook(source_text):
    '''
    Returns the first portion of a string that was found by source(), which
    is typically the name of a book (minus the page reference).

    :param str source_text:

    '''
    book = 'Unknown'
    if source_text is not None:
        book = source_text.split(',')[0]
        book = ''.join([x[0] for x in book.split()])

    return book


def gen_category(root, category):
    '''
    Yields iterators of category from a XML root object.

    :param xml.etree.ElementTree.ElementTree root:
    :param str category:

    '''
    for iterator in root.getiterator(category):
        yield iterator


def gen_item(items):
    '''
    Yield dicts from a sequence of 'item' categories produced by gen_category()

    '''
    for item in items:
        # Normalize all tag values as keys to prevent special tag-by-tag
        # handling rules
        item_dict = defaultdict(list)
        for element in Item.elements:
            sublist = list(item.getiterator(element))
            for sub in sublist:
                # Apply the defined transforms to each tag
                func = Item.elements[sub.tag]
                item_dict[sub.tag].append(func(sub))

        yield item_dict


def gen_spell(spells):
    '''
    Yield dicts from a sequence of 'spell' categories produced by gen_category()

    WIP

    '''
    pass


# TBD: spell, feat, class, background, monster
SUPPORTED_CATEGORIES = {
    'item': gen_item,
    # 'spell': gen_spell,
    # 'feat': gen_feat,
    # 'class': gen_class,
    # 'background': gen_background,
    # 'monster': gen_monster,
}


def gen_tags(tags, dicts):
    '''
    Yields dicts from a sequence of dicts with an extra field inserted that
    includes the desired tag data.

    :param list tags: the desired tag data to insert
    :param iterable dicts:

    '''
    for dct in dicts:
        processed = list()
        for tag in tags:
            tag_field = TAG_MAP[tag][0]
            tag_func = TAG_MAP[tag][1]
            try:
                value = tag_func(dct[tag_field])
            except Exception as exc:
                sys.stderr.write(
                    'Error when tagging {}: {}\n'.format(dct['name'], exc)
                )
            else:
                if value:
                    processed.extend(value)

        if processed:
            dct.update(tags=processed)

        yield dct


def gen_flatten(dicts):
    '''
    Yields dicts from a sequence of dicts, with certain fields being modified
    to hold scalars instead of lists.

    :param iterable dicts:

    '''
    for dct in dicts:
        for key, value in dct.items():
            if key not in ('text', 'modifier', 'tags'):
                if value:
                    dct[key] = value.pop()
        yield dct


def gen_rpgcard_fix(dicts):
    '''
    Converts tagged values to lowercase, because rpgcard does not behave
    correctly when attempting to match tagged data with filters.

    :param iterable dicts:

    '''
    for dct in dicts:
        dct.update(tags=[t.lower() for t in dct['tags']])
        yield dct


def gen_format(dicts):
    '''
    Yields a formatted dict from a sequence of dicts as the last step before
    the data is ready to be written to the output.
    This currently is only geared towards the 'item' category. Something else
    will have to be done to handle other categories, or just let this generator
    get really huge.

    :param iterable dicts:

    '''
    for dct in dicts:
        contents = [
            "Type | {}".format(dct['type']),
        ]

        if 'modifier' in dct:
            contents.extend([capwords('{l[0]} | {l[1]}'.format(l=m)) for m in dct['modifier']])

        if 'property' in dct:
            contents.append('Property | {}'.format(', '.join(dct['property'])))

        if 'ac' in dct:
            contents.append('AC | {}'.format(dct['ac']))

        if 'dmg1' in dct:
            contents.append('Damage 1H | {}'.format(dct['dmg1']))

        if 'dmg2' in dct:
            contents.append('Damage 2H | {}'.format(dct['dmg2']))

        if 'dmgtype' in dct:
            contents.append('DmgType | {}'.format(dct['dmgType']))

        if 'range' in dct:
            contents.append('Range | {}'.format(dct['range']))

        if dct.get('stealth', False):
            contents.append('Stealth | Disadvantage')

        if 'strength' in dct:
            contents.append('Strength | {}'.format(dct['strength']))

        contents = ["property | {}".format(x) for x in contents]

        contents.extend(
            ['text | {}'.format(x) for x in dct['text'] if x is not None]
        )

        yield dict(
            title=dct['name'],
            tags=dct.get('tags', []),
            contents=contents
        )


def dct2json(dicts):
    '''
    Consumes a sequence of dicts, marshalls to JSON, and returns the entire
    sequence as a single document.

    :param iterable dicts:
    '''
    return json.dumps([d for d in dicts], indent=4)


def parse_args():
    '''
    Command line argument parser for compendium_to_card

    '''
    parser = argparse.ArgumentParser(
        description=(
            "Convert Roll20 compendium XML documents into JSON objects "
            "compatible with rpg-card.\n"
            "See:\n"
            "\thttps://github.com/ceryliae/DnDAppFiles\n"
            "\thttps://github.com/crobi/rpg-cards"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input_file", type=str,
        help="Roll20 Compendium XML file to read"
    )
    parser.add_argument(
        "output_file", type=str, default=None, nargs='?',
        help="rpg-card JSON file to write; or STDOUT if omitted"
    )
    parser.add_argument(
        '-c', dest='categories', action='append', default=[],
        choices=SUPPORTED_CATEGORIES.keys(), metavar='<category>',
        help=(
            "Chose the compendium categories you want to convert; default is "
            "all supported categories. Repeat this option to choose multiple "
            "categories."
        )
    )
    parser.add_argument(
        '-t', dest='tags', action='append', default=[],
        choices=TAG_MAP.keys(), metavar='<tag name>',
        help=(
            "Chose the fields that you'd like to add as tags in the output "
            "data. This allows you to filter on these fields within rpgcard. "
            "Repeat this option to choose multiple tags."
        )
    )

    return parser.parse_args()


def tracer(things):
    '''
    a debugging tool for generator expressions

    '''
    for thing in things:
        print('[TRACE] {}'.format(thing))
        yield thing


def dispatch(root, categories):
    '''
    Yields category iterators found in root for each category in categories.

    :param xml.etree.ElementTree.ElementTree root:
    :param list categories:

    '''
    for category in categories:
        generator = SUPPORTED_CATEGORIES[category](gen_category(root, category))
        while True:
            yield next(generator)


def main():
    '''
    Redirected main entry point

    '''

    args = parse_args()

    if not args.categories:
        # Apply default categories
        args.categories = list(SUPPORTED_CATEGORIES)

    root = ET.parse(args.input_file)

    pipeline = (
        gen_format(
            gen_rpgcard_fix(
                gen_flatten(
                    gen_tags(
                        args.tags, (x for x in dispatch(root, args.categories))
                    )
                )
            )
        )
    )

    if args.output_file is not None:
        with open(args.output_file, 'w') as output:
            output.write(dct2json(pipeline))
    else:
        print(dct2json(pipeline))


if __name__ == '__main__':
    main()
