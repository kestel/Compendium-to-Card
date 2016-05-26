#!/usr/bin/env python3
'''
compendium_to_card - convert D&D compendium XML files into JSON for rpgcard

Reference:

Keys & Sub-keys in compendium:

item
====
{'modifier', 'property', 'weight', 'stealth', 'text', 'range', 'name', 'strength',
 'type', 'ac', 'roll', 'dmg2', 'dmg1', 'dmgType'}

race
====
{'size', 'name', 'ability', 'trait', 'speed', 'proficiency'}

background
==========
{'name', 'trait', 'proficiency'}

feat
====
{'text', 'prerequisite', 'name', 'modifier'}

class
=====
{'hd', 'name', 'spellAbility', 'autolevel', 'proficiency', 'SpellAbility'}

spell
=====
{'school', 'time', 'duration', 'classes', 'text', 'name', 'components', 'ritual',
 'roll', 'level', 'range'}

monster
=======
{'languages', 'vulnerable', 'immune', 'description', 'cha', 'skill', 'wis', 'save',
 'spells', 'action', 'cr', 'name', 'dex', 'type', 'senses', 'int', 'passive', 'str',
 'hp', 'reaction', 'alignment', 'resist', 'speed', 'legendary', 'conditionImmune',
 'size', 'con', 'trait', 'ac'}

'''
# pylint: disable=superfluous-parens

import argparse
import json
import re
import sys
from string import capwords
import xmltodict


CATEGORY_MAP = {}
#     'item': Item,
#     'race': Race,
#     'background': Background,
#     'feat': Feat,
#     'class': Class,
#     'spell': Spell,
#     'monster': Monster,
# }


class SimpleDescriptor(object):
    '''
    TODO

    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, key_name, default=None):
        self.key_name = key_name
        self.default = default

    def __get__(self, instance, dummy_cls):
        value = instance.data.get(self.key_name, self.default)

        return value

    def __set__(self, dummy_instance, dummy_value):
        print('Updating compendium values is not allowed')

    def __delete__(self, dummy_instance):
        print('Deleting compendium values is not allowed')


class LookupDescriptor(object):
    '''
    TODO

    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, key_name, lookup_dict):
        self.key_name = key_name
        self.lookup = lookup_dict

    def __get__(self, instance, dummy_cls):
        code = instance.data.get(self.key_name)
        if code is not None:
            try:
                value = self.lookup[code]
            except KeyError:
                print(sys.stderr, "Unrecognized %s code: '%s'" % (self.key_name, code))
                value = value

            return value

    def __set__(self, dummy_instance, dummy_value):
        print('Updating compendium values is not allowed')

    def __delete__(self, dummy_instance):
        print('Deleting compendium values is not allowed')


class LookupListDescriptor(object):
    '''
    TODO

    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, key_name, lookup_dict):
        self.key_name = key_name
        self.lookup = lookup_dict

    def __get__(self, instance, dummy_cls):
        result = []
        codes = instance.data.get(self.key_name)
        if codes is not None:
            codes = codes.split(',')
            for code in codes:
                try:
                    result.append(self.lookup[code])
                except KeyError:
                    print(sys.stderr, "Unrecognized %s code: '%s'" % (self.key_name, code))
                    result.append(code)

        return result

    def __set__(self, dummy_instance, dummy_value):
        print('Updating compendium values is not allowed')

    def __delete__(self, dummy_instance):
        print('Deleting compendium values is not allowed')


class CompendiumMeta(type):
    def __init__(cls, name, bases, cdict):
        super(CompendiumMeta, cls).__init__(name, bases, cdict)
        if object not in bases:
            # We only want to add the CompendiumCategory subclasses, not
            # CompendiumCategory itself
            CATEGORY_MAP[name.lower()] = dict(cls=cls)


class CompendiumCategory(object, metaclass=CompendiumMeta):
    '''
    TODO

    '''
    name = SimpleDescriptor('name')
    text = None

    def __init__(self, item_dict):
        self.data = item_dict

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.name)

    @property
    def source(self):
        '''
        TODO

        '''
        # pylint: disable=not-an-iterable
        source = None
        if self.text is not None:
            for line in self.text:
                if line is not None:
                    if 'Source:' in line:
                        source = line.replace('Source:', '').strip()

        return source

    @property
    def sourcebook(self):
        '''
        TODO

        '''
        book = None
        if self.source is not None:
            book = self.source.split(',')[0]

        return book

    def to_dict(self):
        '''
        TODO

        '''
        print('Not yet implemented', file=sys.stderr)


class Race(CompendiumCategory):
    pass


class Monster(CompendiumCategory):
    pass


class Spell(CompendiumCategory):
    pass


class Class(CompendiumCategory):
    pass


class Background(CompendiumCategory):
    pass


class Feat(CompendiumCategory):
    pass


class Item(CompendiumCategory):
    '''
        Item Keys & Sub-keys in compendium:
        {
            'modifier',
            'property',
            'weight',
            'stealth',
            'text',
            'range',
            'name',
            'strength',
            'type',
            'ac',
            'roll',
            'dmg2',
            'dmg1',
            'dmgType'
        }

    '''
    item_codes = dict(
        HA='Heavy Armor',
        MA='Medium Armor',
        LA='Light Armor',
        S='Shield',
        M='Melee weapon',
        R='Ranged weapon',
        A='Ammunition',
        RD='Rod',
        ST='Staff',
        WD='Wand',
        RG='Ring',
        P='Potion',
        SC='Scroll',
        W='Wondrous item',
        G='Adventuring gear',
    )
    # Handle special code names that break dict() constructors
    item_codes['$'] = 'Money'

    property_codes = dict(
        V="Versatile",
        L="Light",
        T="Thrown",
        A="Ammunition",
        F="Finesse",
        H="Heavy",
        LD="Loading",
        R="Reach",
        S="Special",
    )
    # Handle special code names that break dict() constructors
    property_codes['2H'] = "Two-handed"

    damage_codes = dict(
        S="Slashing",
        B="Bludgeoning",
        P="Piercing",
    )

    weight = SimpleDescriptor('weight')
    text = SimpleDescriptor('text')
    range = SimpleDescriptor('range')
    strength = SimpleDescriptor('strength')
    ac = SimpleDescriptor('ac')     # pylint: disable=invalid-name
    roll = SimpleDescriptor('roll')
    dmg1 = SimpleDescriptor('dmg1')
    dmg2 = SimpleDescriptor('dmg2')
    dmgType = LookupDescriptor('dmgType', damage_codes)
    type = LookupDescriptor('type', item_codes)
    properties = LookupListDescriptor('property', property_codes)

    @property
    def modifier(self):
        '''
        Here we always ensure that an item's modifier returns a list

        '''
        _modifier = self.data.get('modifier', [])
        if isinstance(_modifier, dict):
            _modifier = [_modifier]

        return _modifier

    @property
    def stealth(self):
        '''
        Indicates whether an item triggers disadvantage on stealth rolls

        '''
        value = self.data.get('stealth', 'NO')

        return value.lower() == 'yes'

    @property
    def dmg(self):
        '''
        TODO

        '''
        damage = [dmg for dmg in [self.dmg1, self.dmg2] if dmg is not None]

        return ", ".join(damage)

    def to_dict(self):
        rpgdict = dict()
        contents = [
            "Type | {}".format(self.type),
        ]
        tags = []

        if self.type is not None:
            tags.append(self.type.lower())

        if self.sourcebook is not None:
            tags.append(self.sourcebook.lower())

        if self.properties:
            tags.extend([x.lower() for x in self.properties])
            contents.append('Property | {}'.format(', '.join(self.properties)))

        for mod in self.modifier:
            contents.append(capwords("{m[@category]} | {m[#text]}".format(m=mod)))

        if self.ac is not None:
            contents.append('AC | {}'.format(self.ac))

        if self.dmg1 is not None:
            contents.append('Damage 1H | {}'.format(self.dmg1))

        if self.dmg2 is not None:
            contents.append('Damage 2H | {}'.format(self.dmg2))

        if self.dmgType is not None:
            contents.append('DmgType | {}'.format(self.dmgType))

        if self.range is not None:
            contents.append('Range | {}'.format(self.range))

        if self.stealth:
            contents.append('Stealth | Disadvantage')

        if self.strength is not None:
            contents.append('Strength | {}'.format(self.strength))

        contents = ["property | {}".format(x) for x in contents]
        contents.append('text | {}'.format(self.text))

        rpgdict.update(
            title=self.name,
            contents=contents,
            tags=tags,
        )
        return rpgdict


class CategoryDescriptor(object):
    '''
    TODO

    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, dummy_cls):
        category = instance.contents.get(self.name, [])
        category_class = CATEGORY_MAP[self.name].get('cls', CompendiumCategory)
        if isinstance(category, list):
            for comp_def in category:
                yield category_class(comp_def)
        else:
            yield category_class(category)

    def __set__(self, dummy_instance, dummy_value):
        print('Updating compendium categories is not allowed')

    def __delete__(self, dummy_instance):
        print('Deleting compendium categories is not allowed')


class Compendium(object):
    '''
    TODO

    '''
    compatible_versions = ('5',)

    def __init__(self, xml_file):
        self._xml_file = xml_file
        self._contents = None

    def parse_xml_compendium(self):
        '''
        TODO

        '''
        with open(self._xml_file) as infile:
            return xmltodict.parse(infile.read())['compendium']

    @property
    def contents(self):
        '''
        TODO

        '''
        if self._contents is None:
            self._contents = self.parse_xml_compendium()
        return self._contents

    @property
    def version(self):
        '''
        TODO

        '''
        return self.contents.get('@version')

    def carddump(self, categories=None):
        '''
        TODO

        '''
        if categories is None:
            categories = list()

        dump = []
        for obj_list in self._dump(categories):
            for obj in obj_list:
                obj_dict = obj.to_dict()
                if obj_dict is not None:
                    dump.append(obj_dict)

        #     obj.to_dict() for obj_list in self._dump(categories)
        #     for obj in obj_list if obj is not None
        # ]

        return dump

    def _dump(self, categories):
        '''
        TODO

        '''
        if not categories:
            # default to all known categories
            categories = CATEGORY_MAP.keys()

        for category in categories:
            attr_name = CATEGORY_MAP[category]['property']
            if hasattr(self, attr_name):
                attr = getattr(self, attr_name)
                yield [x for x in attr]

    def search_names(self, name):
        '''
        TODO

        '''
        if name == name.lower():
            regex = re.compile('.*%s.*' % name, re.I)
        else:
            regex = re.compile('.*%s.*' % name)
        for item in self.items:
            result = regex.search(item.name)
            if result is not None:
                yield item

    # Create properties for compendium categories and update the map so we
    # can cross reference a category to a Compendium property
    items = CategoryDescriptor('item')
    CATEGORY_MAP['item']['property'] = 'items'
    races = CategoryDescriptor('race')
    CATEGORY_MAP['race']['property'] = 'races'
    backgrounds = CategoryDescriptor('background')
    CATEGORY_MAP['background']['property'] = 'backgrounds'
    feats = CategoryDescriptor('feat')
    CATEGORY_MAP['feat']['property'] = 'feats'
    classes = CategoryDescriptor('class')
    CATEGORY_MAP['class']['property'] = 'classes'
    spells = CategoryDescriptor('spell')
    CATEGORY_MAP['spell']['property'] = 'spells'
    monsters = CategoryDescriptor('monster')
    CATEGORY_MAP['monster']['property'] = 'monsters'


def parse_args():
    '''
    TODO

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
        choices=CATEGORY_MAP.keys(),
        help=(
            "Chose the compendium categories you want to convert, default is "
            "everything. Repeat this option for multiple selections."
        )
    )

    return parser.parse_args()


def main():
    '''
    TODO

    '''
    args = parse_args()

    compendium = Compendium(args.input_file)

    if compendium.version not in compendium.compatible_versions:
        print(
            "%s is not compatible with version %s compendiums!" %
            (__file__, compendium.version)
        )
        return 1

    rpgcard_data = json.dumps(
        compendium.carddump(args.categories),
        indent=4,
    )

    if args.output_file is None:
        print(rpgcard_data)
    else:
        with open(args.output_file, 'w') as outfile:
            outfile.write(rpgcard_data)

    return 0


if __name__ == '__main__':
    sys.exit(main())
