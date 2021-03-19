# -*- coding: utf-8 -*-
"""NER.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pYXSpIxXXpWpt_-01F2sjRRykClbEc5I
"""

import spacy
import pandas as pd
from sample_isda import read_json
from spacy.matcher import Matcher
import pprint

def get_currency(text, patterns):
  doc = nlp(text)
  matcher = Matcher(nlp.vocab, validate=True)
  matcher.add("Entity", patterns)

  # Extract matched text
  matches = matcher(doc)
  entity_list = []

  for match_id, start, end in matches:
      # Get the matched span
      matched_span = doc[start:end]
      currency = matched_span.text.split()[0]
      amount = matched_span.text.split()[1]
      entity_list.append([currency, amount])

  return entity_list

def check_completion(dictionary):
  for entity in dictionary:
    if dictionary[entity] == None:
      return False
  return True

def get_results(text):

  queue = []
  results = {     "text" : text,
                  "delivery_currency": None,
                  "delivery_amount": None,
                  "delivery_rounding": "nearest",
                  "return_currency": None,
                  "return_amount": None,
                  "return_rounding": "nearest" }
  conj_flag = False
  rounding_flag = False
  completion_flag = 2

  entities = get_currency(text, patterns)
  # print(entities)

  for word in text.split():

      if word.lower() == "delivery" or word.lower() == "return":
          queue.append(word.lower())
          if conj_flag:
              queue.append("delivery + return")

      if rounding_flag:
          rounding_flag = False

          if queue[-1] == "delivery + return":
              results['delivery_rounding'] = word.lower()
              results['return_rounding'] = word.lower()

              if len(entities) == 1:
                  results['delivery_currency'] = entities[0][0]
                  results['delivery_amount'] = entities[0][1]
                  results['return_currency'] = entities[0][0]
                  results['return_amount'] = entities[0][1]
                  completion_flag -= 2

          if queue[-1] == "delivery":
              results['delivery_rounding'] = word.lower()

              results['delivery_currency'] = entities[1][0]
              results['delivery_amount'] = entities[1][1]
              results['return_currency'] = entities[0][0]
              results['return_amount'] = entities[0][1]
              completion_flag -= 1
              
          if queue[-1] == "return":
              results['return_rounding'] = word.lower()

              results['delivery_currency'] = entities[0][0]
              results['delivery_amount'] = entities[0][1]
              results['return_currency'] = entities[1][0]
              results['return_amount'] = entities[1][1]
              completion_flag -= 1          
          queue.pop()

      if word.lower() == "rounded":
          rounding_flag = True
      elif word.lower() == "and" and len(queue) > 0:
          conj_flag = True
      elif completion_flag == 0:
          break
      else: continue

  return results

global patterns
patterns = [
    [{"POS" : "PROPN", "OP" : "*"}, {"IS_ALPHA" : True, "IS_UPPER": True, "LENGTH" : 3}, {"IS_DIGIT": True},{}], 
    [{"IS_ALPHA" : True, "IS_UPPER": True, "LENGTH" : 3}, {"LIKE_NUM" : True}]
  ]

nlp = spacy.load("en_core_web_sm")

if __name__ == '__main__':

  corpus = read_json("./data/input.json")
  print("Total documents to process: ", len(corpus))
  results = []
  for text in corpus:
    text = text["text"]
    result = get_results(text)
    results.append(result)

  result_df = pd.DataFrame(results)
  result_df.to_csv("./results/results.csv", index = False)

  print("Finished Processing.")

