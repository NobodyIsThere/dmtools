#!/usr/bin/env python

from dmtools import get_data_path
import random

START_TOKEN = -2
END_TOKEN = -1

def load_tokens(type):
    path = get_data_path() + "names/"
    path += type + "_tokens.txt"
    string_to_token = {">": END_TOKEN, "<": START_TOKEN}
    token_to_string = {END_TOKEN: ">", START_TOKEN: "<"}
    with open(path, 'rb') as f:
        for i, line in enumerate(f):
            string_to_token[line.strip()] = i
            token_to_string[i] = line.strip()
    return string_to_token, token_to_string
    
def load_names(type, string_to_token):
    path = get_data_path() + "names/"
    path += type + "_names.txt"
    data = []
    with open(path, 'rb') as f:
        for line in f:
            data += [START_TOKEN] + tokenify(line.strip(), string_to_token) + \
                [END_TOKEN]
    return data
    
def get_next_token(tokens, all_tokens, data, min_length, depth=3):
    choices = [END_TOKEN]
    for i, t in enumerate(data[:-depth]):
        for j in range(len(tokens)+1):
            if j <= depth:
                #print data[i:i+j]
                #print tokens[-j:]
                if data[i:i+j] == tokens[-j:]:
                    choices.append(data[i+j])
    choice = random.choice(choices)
    return choice

def generate_name(type, gender=None, seed="", min_length=3):
    string_to_token, token_to_string = load_tokens(type)
    all_tokens = token_to_string.keys()
    data = load_names(type, string_to_token)
    tokens = tokenify(seed, string_to_token)
    while tokens[-1] != END_TOKEN:
        tokens.append(get_next_token(tokens, all_tokens, data, min_length))
    name = stringify(tokens, token_to_string)[1:-1]
    return name.title()
    
def tokenify(string, string_to_token):
    tokens = []
    i = 0
    while i < len(string):
        for j in range(len(string), i, -1):
            current_string = string[i:j]
            if current_string in string_to_token:
                tokens.append(string_to_token[current_string])
                current_string = ""
                i = j
                break
    if len(tokens) == 0:
        return [START_TOKEN]
    return tokens
    
def stringify(tokens, token_to_string):
    string = ""
    for token in tokens:
        string += token_to_string[token]
    return string