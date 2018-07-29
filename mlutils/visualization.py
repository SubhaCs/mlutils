# -*- coding: utf-8 -*-
"""
Visualization utilities for Keras.
Created on Sat Jul 28 20:00:00 2018
Author: Prasun Roy | CVPRU-ISICAL (http://www.isical.ac.in/~cvpr)
GitHub: https://github.com/prasunroy/mlutils

"""


# imports
from __future__ import division
from __future__ import print_function

import cv2
import numpy
import os

from keras import backend as K

from cvutils.io import imshow
from cvutils.io import imwrite


# LayersVisualizer class
class LayersVisualizer:
    
    # ~~~~~~~~ constructor ~~~~~~~~
    def __init__(self, model, exclusions=[]):
        self._model = model
        self._exclusions = exclusions
        self._bfunctions = self._backend_functions()
        self._fn_outputs = {}
        return
    
    # ~~~~~~~~ backend functions ~~~~~~~~
    def _backend_functions(self):
        functions = {}
        for index, layer in enumerate(self._model.layers):
            if any([ex_key in layer.name for ex_key in self._exclusions]):
                continue
            fn_key = 'layer_{}_{}'.format(str(index).zfill(len(str(len(self._model.layers)))), layer.name)
            functions[fn_key] = K.function([self._model.input, K.learning_phase()], [layer.output])
        return functions
    
    # ~~~~~~~~ create grid from array ~~~~~~~~
    def _to_grid(self, array, padding=0):
        if len(array.shape) == 1:
            array = array.reshape(-1, 1, 1)
        h, w, c = array.shape
        grid_sq = int(numpy.ceil(numpy.sqrt(c)))
        for rows in range(1, int(numpy.sqrt(c)) + 1):
            if c % rows == 0:
                grid_rows = rows
                grid_cols = c // rows
        grid_cols = min(grid_cols, grid_sq)
        grid_rows = int(numpy.ceil(c / grid_cols))
        grid = numpy.ones(shape=((h+padding)*grid_rows+padding,
                                 (w+padding)*grid_cols+padding), dtype='uint8') * 255
        k = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                image = cv2.normalize(array[:, :, k], None, 0, 255,
                                      cv2.NORM_MINMAX, cv2.CV_8UC1)
                grid[(h+padding)*row+padding:(h+padding)*row+padding+h,
                     (w+padding)*col+padding:(w+padding)*col+padding+w] = image
                k += 1
                if k >= c:
                    break
            if k >= c:
                break
        return grid
    
    # ~~~~~~~~ parse input ~~~~~~~~
    def parse_input(self, x, mode=0):
        self._fn_outputs = {fn_key: fn([x, mode])[0][0] for fn_key, fn in self._bfunctions.items()}
        return self._fn_outputs
    
    # ~~~~~~~~ save outputs ~~~~~~~~
    def save(self, out_dir, padding=0, layer_keys=[], overwrite=False):
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        for fn_key, output in self._fn_outputs.items():
            if len(layer_keys) > 0 and not any([layer_key in fn_key for layer_key in layer_keys]):
                continue
            filepath = os.path.join(out_dir, '{}.png'.format(fn_key))
            if not overwrite and os.path.isfile(filepath):
                print('[INFO] Skipped overwriting existing image at {}'.format(filepath))
            elif imwrite(filepath, self._to_grid(output, padding)):
                print('[INFO] Saved output image at {}'.format(filepath))
            else:
                print('[INFO] Failed to save output image at {}'.format(filepath))
        return
    
    # ~~~~~~~~ show outputs ~~~~~~~~
    def show(self, padding=0, layer_keys=[]):
        for fn_key, output in self._fn_outputs.items():
            if len(layer_keys) > 0 and not any([layer_key in fn_key for layer_key in layer_keys]):
                continue
            imshow(self._to_grid(output, padding), fn_key)
        return
