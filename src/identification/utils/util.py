# -*- coding: utf-8 -*-

from typing import *
import json
from pathlib import Path
from itertools import repeat
from collections import OrderedDict

import torch

try:
    from .class_utils import vocab_cls
    from ..data_utils import documents
except ImportError:
    from src.identification.utils.class_utils import vocab_cls
    from src.identification.data_utils import documents

def ensure_dir(dirname):
    dirname = Path(dirname)
    if not dirname.is_dir():
        dirname.mkdir(parents=True, exist_ok=False)


def read_json(fname):
    fname = Path(fname)
    with fname.open('rt') as handle:
        return json.load(handle, object_hook=OrderedDict)


def write_json(content, fname):
    fname = Path(fname)
    with fname.open('wt') as handle:
        json.dump(content, handle, indent=4, sort_keys=False)


def inf_loop(data_loader):
    ''' wrapper function for endless data loader. '''
    for loader in repeat(data_loader):
        yield from loader


def iob2entity(tag):
    '''
    iob label to entity
    :param tag:
    :return:
    '''
    if len(tag) == 1 and tag != 'O':
        raise TypeError('Invalid tag!')
    elif len(tag) == 1 and tag == 'O':
        return tag
    elif len(tag) > 1:
        e = tag[2:]
        return e


def iob_index_to_str(tags: List[List[int]]):
    decoded_tags_list = []
    for doc in tags:
        decoded_tags = []
        for tag in doc:
            s = vocab_cls['iob_labels'].itos[tag]
            if s == '<unk>' or s == '<pad>':
                s = 'O'
            decoded_tags.append(s)
        decoded_tags_list.append(decoded_tags)
    return decoded_tags_list


def text_index_to_str(texts: torch.Tensor, mask: torch.Tensor):
    # union_texts: (B, num_boxes * T)
    matrix_box_len, union_texts = texts_to_union_texts(texts, mask)
    B, NT = union_texts.shape

    decoded_tags_list = []
    words_list = []

    for i in range(B):
        decoded_text = []
        for text_index in union_texts[i]:
            text_str = vocab_cls['keys'].itos[text_index]
            if text_str == '<unk>' or text_str == '<pad>':
                text_str = 'O'
            decoded_text.append(text_str)
        decoded_tags_list.append(decoded_text)
        
        tmp = 0
        word = []
        for wl in matrix_box_len[i].tolist():
            if wl == 0: 
                continue
            word.append([(tmp,tmp+wl),''.join(decoded_tags_list[i][tmp:tmp+wl])])
            tmp += wl 
        words_list.append(word)
    return words_list, decoded_tags_list


def texts_to_union_texts(texts, mask):
    '''

    :param texts: (B, N, T)
    :param mask: (B, N, T)
    :return:
    '''

    B, N, T = texts.shape
    
    matrix_box_len = (texts*mask != 0).sum(-1)

    texts = texts.reshape(B, N * T)
    mask = mask.reshape(B, N * T)

    # union tags as a whole sequence, (B, N*T)
    union_texts = torch.full_like(texts, vocab_cls['keys']['<pad>'], device=texts.device)

    max_seq_length = 0
    for i in range(B):
        valid_text = torch.masked_select(texts[i], mask[i].bool())
        valid_length = valid_text.size(0)
        union_texts[i, :valid_length] = valid_text

        if valid_length > max_seq_length:
            max_seq_length = valid_length

    # max_seq_length = documents.MAX_BOXES_NUM * documents.MAX_TRANSCRIPT_LEN
    # (B, N*T)
    union_texts = union_texts[:, :max_seq_length]

    # (B, N*T)
    return matrix_box_len, union_texts


def iob_tags_to_union_iob_tags(iob_tags, mask):
    '''

    :param iob_tags: (B, N, T)
    :param mask: (B, N, T)
    :return:
    '''

    B, N, T = iob_tags.shape

    iob_tags = iob_tags.reshape(B, N * T)
    mask = mask.reshape(B, N * T)

    # union tags as a whole sequence, (B, N*T)
    union_iob_tags = torch.full_like(iob_tags, vocab_cls['iob_labels']['<pad>'], device=iob_tags.device)

    max_seq_length = 0
    for i in range(B):
        valid_tag = torch.masked_select(iob_tags[i], mask[i].bool())
        valid_length = valid_tag.size(0)
        union_iob_tags[i, :valid_length] = valid_tag

        if valid_length > max_seq_length:
            max_seq_length = valid_length

    # max_seq_length = documents.MAX_BOXES_NUM * documents.MAX_TRANSCRIPT_LEN
    # (B, N*T)
    union_iob_tags = union_iob_tags[:, :max_seq_length]

    # (B, N*T)
    return union_iob_tags
