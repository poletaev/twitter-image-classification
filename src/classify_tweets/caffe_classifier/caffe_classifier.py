"""
Caffe Classifier

This extension is based on web_demo Flask application provided with Caffe
https://github.com/BVLC/caffe

"""

import cPickle
import logging
import os
import requests
import tempfile
import time

import caffe
import numpy as np
import pandas as pd
from PIL import Image


class FailToClassify(Exception):
    pass


class ImagenetClassifier(object):

    ORIENTATIONS = {   # used in _apply_orientation
        2: (Image.FLIP_LEFT_RIGHT,),
        3: (Image.ROTATE_180,),
        4: (Image.FLIP_TOP_BOTTOM,),
        5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
        6: (Image.ROTATE_270,),
        7: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_270),
        8: (Image.ROTATE_90,)
    }

    def __init__(self, prototxt=None, caffemodel=None, mean_file=None,
                 class_labels=None, bet_file=None, gpu=False, tmp_dir=None):
        self._image_dim = 256
        self._raw_scale = 255.
        self._prototxt = prototxt
        self._caffemodel = caffemodel
        self._mean_file = mean_file
        self._class_labels = class_labels
        self._bet_file = bet_file
        self._gpu = gpu
        self._tmp_dir = tmp_dir
        for path in [self._prototxt, self._caffemodel, self._mean_file,
                     self._class_labels, self._bet_file]:
            if not os.path.exists(path):
                raise Exception("File {} is missing.".format(path))
        if self._gpu:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()

        self.net = caffe.Classifier(
            self._prototxt,
            self._caffemodel,
            image_dims=(self._image_dim, self._image_dim),
            raw_scale=self._raw_scale,
            mean=np.load(self._mean_file).mean(1).mean(1), channel_swap=(2, 1, 0)
        )
        with open(self._class_labels) as f:
            labels_df = pd.DataFrame([
                {
                    'synset_id': l.strip().split(' ')[0],
                    'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
                }
                for l in f.readlines()
            ])
        self.labels = labels_df.sort('synset_id')['name'].values
        self.bet = cPickle.load(open(self._bet_file))
        # A bias to prefer children nodes in single-chain paths
        # I am setting the value to 0.1 as a quick, simple model.
        self.bet['infogain'] -= np.array(self.bet['preferences']) * 0.1

    def _apply_orientation(self, im, orientation):
        if orientation in self.ORIENTATIONS:
            for method in self.ORIENTATIONS[orientation]:
                im = im.transpose(method)
        return im

    def _open_oriented_im(self, image_path):
        if not os.path.exists(image_path):
            try:
                url = image_path
                tmp_file = tempfile.NamedTemporaryFile(delete=False,
                                                       dir=self._tmp_dir)
                image_path = tmp_file.name
                r = requests.get(url, stream=True)
                for chunk in r.iter_content(10000):
                    tmp_file.write(chunk)
                tmp_file.close()
            except requests.exceptions.RequestException as e:
                logging.exception("Requests error", e)
                raise FailToClassify(e.message)
            except Exception as e:
                logging.exception("Error", e)
                raise FailToClassify(e.message)

        im = Image.open(image_path)
        if hasattr(im, '_getexif'):
            exif = im._getexif()
            if exif is not None and 274 in exif:
                orientation = exif[274]
                im = self._apply_orientation(im, orientation)
        img = np.asarray(im).astype(np.float32) / 255.
        if img.ndim == 2:
            img = img[:, :, np.newaxis]
            img = np.tile(img, (1, 1, 3))
        elif img.shape[2] == 4:
            img = img[:, :, :3]
        return img

    def _classify_image(self, image_path):
        """
        :param image_path: file path to classified image 
        :return: tuple of boolean result, 
                          list with top N predictions
                          elapsed time 
        """
        logging.info("Classify {} image.".format(image_path))
        try:
            image = self._open_oriented_im(image_path)
            scores = self.net.predict([image], oversample=True).flatten()
            return scores

        except Exception as err:
            logging.exception('Classification error: %s', err)
            raise FailToClassify(err.message)

    def top_n_classes(self, image_path, top_n=10):
        starttime = time.time()

        if top_n > len(self.labels):
            logging.warning("Requested top N predictions ({}) is bigger "
                            "than total number of classes ({})."
                            .format(top_n, len(self.labels)))

        scores = self._classify_image(image_path)
        indices = (-scores).argsort()[:top_n]
        predictions = self.labels[indices]
        return predictions.tolist(), time.time() - starttime

    def top_n_scores_and_classes(self, image_path, top_n=10):
        starttime = time.time()

        if top_n > len(self.labels):
            logging.warning("Requested top N predictions ({}) is bigger "
                            "than total number of classes ({})."
                            .format(top_n, len(self.labels)))

        scores = self._classify_image(image_path)
        indices = (-scores).argsort()[:top_n]
        predictions = self.labels[indices]

        meta = {}
        for i, p in zip(indices, predictions):
            meta.setdefault(p, '%.5f' % scores[i])
        return meta, time.time() - starttime

    def _hedging_classify_image(self, image_path):
        """
        :param image_path: file path to classified image
        :return: expected information gain
        """
        scores = self._classify_image(image_path)
        # Compute expected information gain
        expected_infogain = np.dot(
            self.bet['probmat'], scores[self.bet['idmapping']])
        expected_infogain *= self.bet['infogain']
        return expected_infogain

    def hedging_top_n_classes(self, image_path, top_n=10):
        starttime = time.time()
        if top_n > len(self.labels):
            logging.warning("Requested top N predictions ({}) is bigger "
                            "than total number of classes ({})."
                            .format(top_n, len(self.labels)))

        # Compute expected information gain
        expected_infogain = self._hedging_classify_image(image_path)

        # sort the scores
        infogain_sort = expected_infogain.argsort()[::-1]
        bet_result = [self.bet['words'][v] for v in infogain_sort[:top_n]]
        return bet_result, time.time() - starttime

    def hedging_top_n_scores_and_classes(self, image_path, top_n=10):
        starttime = time.time()
        if top_n > len(self.labels):
            logging.warning("Requested top N predictions ({}) is bigger "
                            "than total number of classes ({})."
                            .format(top_n, len(self.labels)))

        # Compute expected information gain
        expected_infogain = self._hedging_classify_image(image_path)

        # sort the scores
        infogain_sort = expected_infogain.argsort()[::-1]

        bet_result = {}
        for v in infogain_sort[:top_n]:
            bet_result.setdefault(self.bet['words'][v],
                                  '%.5f' % expected_infogain[v])
        return bet_result, time.time() - starttime
