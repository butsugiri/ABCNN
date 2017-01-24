# -*- coding: utf-8 -*-
import os
import sys
import json
import numpy as np
import pickle
from collections import defaultdict
from itertools import groupby


class DataProcessor(object):

    def __init__(self, data_path, test):
        self.train_data_path = os.path.join(data_path, "train.json")
        self.dev_data_path = os.path.join(data_path, "dev.json")
        self.test_data_path = os.path.join(data_path, "test.json")
        # conventional lexical features pkl used in [Yang+ 2015]
        self.id2features = pickle.load(open("../work/features.pkl", "rb"))
        self.test = test # if true, use tiny datasets for quick test

        # Vocabulary for sentence pairs
        self.vocab = defaultdict(lambda: len(self.vocab))
        self.vocab["<pad>"]
        # 予測先のconnective tokens
        # self.connective = defaultdict(lambda: len(self.connective))

    def prepare_dataset(self):
        # load train/dev/test data
        sys.stderr.write("loading dataset...")
        self.train_data, self.n_train = self.load_dataset("train")
        self.dev_data, self.n_dev = self.load_dataset("dev")
        if self.test:
            sys.stderr.write("...preparing tiny dataset for quick test...")
            self.train_data = self.train_data[:100]
            self.dev_data = self.dev_data[:100]
            # self.test_data = self.test_data[:10]
        sys.stderr.write("done.\n")

    def load_dataset(self, _type):
        if _type == "train":
            path = self.train_data_path
        elif _type == "dev":
            path = self.dev_data_path
        elif _type == "test":
            path = self.test_data_path

        dataset = []
        question_ids = []
        with open(path, "r") as input_data:
            for line in input_data:
                data = json.loads(line)
                y = np.array(data["label"], dtype=np.int32)
                x1s = np.array([self.vocab[token] for token in data["question"]], dtype=np.int32)
                x2s = np.array([self.vocab[token] for token in data["answer"]][:40], dtype=np.int32)  # truncate maximum 40 words
                wordcnt = np.array([self.id2features[(data['question_id'], data['sentence_id'])]['wordcnt']], dtype=np.float32)
                wgt_wordcnt = np.array([self.id2features[(data['question_id'], data['sentence_id'])]['wgt_wordcnt']], dtype=np.float32)
                question_ids.append(data['question_id'])
                # this should be in dict for readability
                # but it requires implementating L.Classifier by myself
                dataset.append((x1s, x2s, wordcnt, wgt_wordcnt, y))

        # Number of Question-Answer Pair for each question.
        # This is needed for validation, when calculating MRR and MAP
        qa_pairs = [len(list(section)) for _, section in groupby(question_ids)]
        return dataset, qa_pairs