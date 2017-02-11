from PIL import Image
import numpy as np
import json
from scipy.misc import imread


def get_data(filename):
    img = Image.open(filename)
    img = img.convert('P', palette=Image.ADAPTIVE, colors=50)
    img.save("temp.png") #I don't like PIL image format but I need it to posterize
    return imread("temp.png")


data = get_data("typo.jpg")

print("image loaded and posterized")

# okay now we want to make a map of this
# we loop over the row in groups of 3
try:
    p_map = json.loads(open("map.json").read())
except:
    print("making model")
    p_map = {}
    for i, row in enumerate(data):
        print(i)
        if i == len(data) - 1:
            break
        for j in range(len(row) - 2):
            seed = row[j:j + 3]
            out = data[i + 1][j + 1]
            key = str(seed[0]) + " " + str(seed[1]) + " " + str(seed[2])
            value = str(out)

            if not key in p_map:
                p_map[key] = {}

            if not value in p_map[key]:
                p_map[key][value] = 1
            else:
                p_map[key][value] += 1

    print("probability map formed")

    open("map.json", "w").write(json.dumps(p_map))

# okay now we need to start generation
# let's just pick a random row to start
import random


def get_item(options):
    choices = []
    for option in options:
        for key in range(options[option]):
            choices.append(option)
    return random.choice(choices)

def make_list(pix):
    pix = pix.replace("[", "").replace("]", "")
    if pix.startswith(" "):
        pix = pix[1:]
    pix = pix.replace("  ", " ").split(" ")
    pix = list(map(lambda x:int(x), pix))
    return pix

print("generating image")

rows_to_make = 15
gen = []
gen.append(random.choice(data).tolist())
for i in range(rows_to_make):
    print(i)
    new_row = []
    row = gen[-1]
    for j in range(len(row) - 2):
        seed = np.array(row[j:j + 3])
        key = str(seed[0])+ " " + str(seed[1]) + " " + str(seed[2])
        try:
            new_item = get_item(p_map[key])
            new_row.append(make_list(new_item))
        except KeyError:
            try:
                new_row.append(new_row[-1])
            except IndexError:
                #this happens if there is an error with the first pixel
                new_row.append(gen[-1][0])
    # okay but we are missing pixels for the first and last options
    # but we also want to shift left since if there is a key error we duplicate the most recent leading to a right shift
    new_row =  new_row + [new_row[-1]] + [new_row[0]]
    gen.append(new_row)



open("generated.json", "w").write(json.dumps(gen))

img = Image.fromarray(np.uint8(gen)).save("gen.png")
