import hashlib
import random
import uuid


def random_cell_id_with_fixed_seed(text):
    """Returns a generator of cell ids that
    takes the notebook source as the initial seed"""
    m = hashlib.md5()
    m.update(text.encode("utf-8"))

    rd = random.Random()
    rd.seed(m.hexdigest())

    def cell_id():
        return uuid.UUID(int=rd.getrandbits(128)).hex[:8]

    return cell_id
