"""
Look inside `enhanced_plots.py` for more info.
"""
from enhanced_plots import DataUnit, FigureWithBindings, Batch
import numpy as np


data_files = 3*['test_data.csv']
names = ['name_{}'.format(i) for i in range(3)]
data_list = [ DataUnit(np.genfromtxt(i), j) for i,j in zip(data_files, names) ]


def get_norm(image, positive_only = True):
    #odecte median celeho obrazku
    #positive_only - zajisti ze vsechny hodnoty >= 1 - kvuli logplotu

    imgej = image - np.median(image)
    if positive_only:
        imgej[imgej < 1] = 1
    return imgej

def prepare_img(image):
    return np.log2(get_norm(image))


def gather_categories(tuple_list):
    cats = set([ i[0] for i in tuple_list ])
    cats_dict = dict.fromkeys(cats, [])
    for i in tuple_list:
        cat = i[0]
        xy = [i[1], i[2]]
        cats_dict[cat].append(xy)

    return cats_dict

batch = Batch(data_list,
        'example_save.out',
        append=True,
        preprocess_fun=prepare_img,
        postprocess_fun=gather_categories)

batch.gimme_more()

