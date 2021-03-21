
# Task : Extracting Financial data from Text


## Problem Statement:
From any given financial text we need to extract the following:
- Currency
- Amount
- Rounding (up / down/ nearest) If not mentioned, take it as 'nearest' by default.
for 'Delivery Amount' and 'Return Amount'.

## Proposed System:

This is a name-entity-recognition problem. For solving this problem statement, I have made use of the popular spacy library for pattern detection, and a queue data structure for sequence maintenance. I approach the problem in two steps. First, I detect the entities (currency, amount and rounding) in the order that they appear in a sentence. Then, I map these obtained entities to their respective subject (‘Delivery’ or ‘Return’) using a queue data structure.

My hypothesis is that, as the English language follows a Subject-Verb-Object structure, the order in which the entities occur can be leveraged to establish their relationship with the subjects (‘Delivery’ or ‘Return’). 


## Usage:

Run sample_isda.py file for testing results.
Store all the custom use-cases (texts) in the input.json file.
Run the run.py file.
Check the results stored in the results folder.

## Requirements:
spacy



