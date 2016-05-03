#!/usr/bin/env python3 

import xmltodict
import json
import sys
import os

input_filename = ""
output_filename = ""

if len(sys.argv) == 2 or len(sys.argv) == 3:
    if type(sys.argv[1]) is str:
        input_filename = os.path.normpath(sys.argv[1])
    if len(sys.argv) == 3 and type(sys.argv[2]) is str:
        output_filename = os.path.normpath(sys.argv[2])
else:
    print("You should use {} <input filename> [output filename]".format(sys.argv[0]))
    print("If [output_filename] is not set - output will be in STDOUT")
    sys.exit(1)

temp = open(input_filename).read()

data = xmltodict.parse(temp)

# converting OrderedDict to regular python dict
items = []
ordered_dict = data["compendium"]["item"]
for each in ordered_dict:
    reg_dict = dict(each)
    items.append(reg_dict)

output = "["
# parsing our dict for each item in
for item in items:
    temp_dict = {}
    temp_dict["title"] = item["name"]
    temp_dict["tags"] = []
    temp_text = list(filter(None, item["text"]))
    temp_dict["contents"] = [ ]
    for key in item.keys(): # Each element in Item's properties
        if key == 'type': # If type exist in item
            param = item[key]
            if param == "HA":
                param = "Heavy Armor"
            elif param == "MA":
                param = "Medium Armor"
            elif param == "LA":
                param = "Light Armor"
            elif param == "S":
                param = "Shield"
            elif param == "M":
                param = "Melee weapon"
            elif param == "R":
                param = "Ranged weapon"
            elif param == "A":
                param = "Ammunition"
            elif param == "RD":
                param = "Rod"
            elif param == "ST":
                param = "Staff"
            elif param == "WD":
                param = "Wand"
            elif param == "RG":
                param = "Ring"
            elif param == "P":
                param = "Potion"
            elif param == "SC":
                param = "Scroll"
            elif param == "W":
                param = "Wondrous item"
            elif param == "G":
                param = "Adventuring gear"
            elif param == "$":
                param = "Money"
            temp_dict["contents"].append("property | Type | {}".format(param))
            temp_dict["tags"].append(param.lower())

        elif key == "ac": # if Armor Class
            temp_dict["contents"].append("property | AC | {}".format(item[key]))

        elif key == "stealth":
            temp_dict["contents"].append("property | Stealth | Disadvantage")

        elif key == "modifier":
            element_list = []
            if type(item[key]) is list: # If several modifiers in item
                for element in item[key]:
                    element_dict = dict(element)
                    element_list.append(element_dict)
            else: # If only one modifier
                element_list.append(dict(item[key]))
            
            for item_mod in element_list:
                category = str(item_mod["@category"])
                text = str(item_mod["#text"])
                temp_dict["contents"].append("property | {} | {}".format(category.capitalize(), text.capitalize()))

        elif key == "property":
            prop_list = item[key].split(",")
            prop_text = ""
            for prop in prop_list:
                if prop == "V":
                    prop_text += "Versatile, "
                elif prop == "L":
                    prop_text += "Light, "
                elif prop == "T":
                    prop_text += "Thrown, "
                elif prop == "A":
                    prop_text += "Ammunition, "
                elif prop == "F":
                    prop_text += "Finesse, "
                elif prop == "H":
                    prop_text += "Heavy, "
                elif prop == "LD":
                    prop_text += "Loading, "
                elif prop == "R":
                    prop_text += "Reach, "
                elif prop == "S":
                    prop_text += "Special, "
                elif prop == "2H":
                    prop_text += "Two-handed, "
            temp_dict["contents"].append("property | Property | {}".format(prop_text.strip()[:-1])) # remove last comma and space
        elif key == "dmg1":
            temp_dict["contents"].append("property | Damage 1H: | {}".format(item[key]))
        elif key == "dmg2":
            temp_dict["contents"].append("property | Damage 2H: | {}".format(item[key]))
        elif key == "dmgType":
            dmgtype = item[key]
            if dmgtype == "S":
                dmgtype = "Slashing"
            elif dmgtype == "B":
                dmgtype = "Bludgeoning"
            elif dmgtype == "P":
                dmgtype = "Piercing"
            temp_dict["contents"].append("property | DmgType | {}".format(dmgtype))

        elif key != 'text' and key != 'name':
            temp_dict["contents"].append("property | {} | {}".format(key.capitalize(), item[key]))
    for key in temp_text: # description 
        if 'Source:' in key:
            source = key.replace('Source:', '').strip()
            source = source.split(',')[0]
            temp_dict['tags'].append(source.lower())
        temp_dict["contents"].append("text | {}".format(key))

    if len(output) > 1:
        output = output + ",\n"
    output = output + json.dumps(temp_dict)
output = output + "]"
if output_filename:
    print("Writing to ",output_filename)
    file = open(output_filename, "w")
    file.write(output)
else:
    print(output)
