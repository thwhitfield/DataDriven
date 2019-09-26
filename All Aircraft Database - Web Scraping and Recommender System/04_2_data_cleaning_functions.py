# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 14:37:33 2019

@author: thwhi
"""

import re
import numpy as np

def fix_name(name):
    return(str(name).strip())

def fix_length(length):
    """Returns the length in ft"""
    if length == None:
        return(0)
    myList = [length]
    return(fix_lengths(myList)[0])
    
def fix_lengths(lengths):
    """Returns list of lengths in ft"""
    new_lengths = lengths.copy()
    rem_parenth = re.compile(r'\(.*\)')
    ft_in_regex = re.compile(r'(\d+\.?\d*)[ ]*[ft|feet] (\d+\.?\d*)[  ]*in')    
    just_ft_regex = re.compile(r'(\d+\.?\d*)[ ]*[ft|feet]')
    just_m_regex = re.compile(r'(\d+\.?\d*)[ ]*m')
    for i in range(len(new_lengths)):
        if new_lengths[i] == '':
            new_lengths[i] = np.nan
            continue
        if type(new_lengths[i]) != str:
            continue
        new_lengths[i] = new_lengths[i].replace(",", "")
        new_lengths[i] = rem_parenth.sub('', new_lengths[i])
        ft_in_length = ft_in_regex.search(new_lengths[i])
        just_ft_length = just_ft_regex.search(new_lengths[i])
        just_m_length = just_m_regex.search(new_lengths[i])
        if ft_in_length:
            new_lengths[i] = float(ft_in_length.group(1)) + float(ft_in_length.group(2))/12
        elif just_ft_length:
            new_lengths[i] = float(just_ft_length.group(1))
        elif just_m_length:
            new_lengths[i] = float(just_m_length.group(1))*3.28084
    
    for length in new_lengths:
        try:
            length = float(length)
        except:
            length = np.nan
    
    return new_lengths

def fix_copied_weights():
    my_values=pyperclip.paste()
    my_values = my_values.split('\r\n')
    new_weights = fix_weights(my_values)
    new_weights = list(map(str, new_weights))
    export_weights = ('\r\n').join(new_weights)
    pyperclip.copy(export_weights)

def fix_weight(weight):
    """Returns weight in lbs"""
    if weight == None:
        return(0)
    myList = [weight]
    return(fix_weights(myList)[0])

#weights should be a list of text weights
def fix_weights(weights):
    """ Returns list of weights in lbs"""
    new_weights = weights.copy()
    rem_parenth = re.compile(r'\(.*\)')
    lb_regex = re.compile(r'(\d+\.?\d*) lb')    
    kg_regex = re.compile(r'(\d+\.?\d*) kg')   
    for i in range(len(new_weights)):
        if type(new_weights[i]) != str:
            continue
        new_weights[i] = new_weights[i].replace(",", "")
        new_weights[i] = rem_parenth.sub('', new_weights[i])
        lb_weight = lb_regex.search(new_weights[i])
        kg_weight = kg_regex.search(new_weights[i])
        if lb_weight:
            new_weights[i] = int(float(lb_weight.group(1)))
        elif kg_weight:
            new_weights[i] = int(float(kg_weight.group(1))*2.20462)

    return new_weights
    
#fix_copied_weights()
    
#def fix_copied_lengths():
#    my_values = pyperclip.paste()
#    my_values = my_values.split('\r\n')
#    new_lengths = fix_lengths(my_values)
#    new_lengths = list(map(str, new_lengths))
#    export_lengths = ('\r\n').join(new_lengths)
#    pyperclip.copy(export_lengths)
    
#def count_values_in_columns():
#    my_table = pyperclip.paste()
#    my_values = my_table.split('\r\n')
#    for i in range(len(my_values)):
#        my_lists.append(my_values[i].split('\t'))