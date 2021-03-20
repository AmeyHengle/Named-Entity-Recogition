import json
from collections import defaultdict
import spacy
import pandas as pd
from spacy.matcher import Matcher

DATAPOINTS = ["delivery_currency", "delivery_amount", "delivery_rounding",
              "return_currency", "return_amount", "return_rounding"]

global patterns
patterns = [
    [{"POS" : "PROPN", "OP" : "*"}, {"IS_ALPHA" : True, "IS_UPPER": True, "LENGTH" : 3}, {"IS_DIGIT": True},{}], 
    [{"IS_ALPHA" : True, "IS_UPPER": True, "LENGTH" : 3}, {"LIKE_NUM" : True}]
  ]

nlp = spacy.load("en_core_web_sm")

def read_json(path):
    """The function is used to read the isda data provided as part of the test

    Returns:
        list: list of dictionary values which contains the text and the datapoints as keys.
    """
    with open(path) as f_p:
        list_isda_data = json.load(f_p)

    return list_isda_data


def get_currency(text, patterns):
    
    """The function extracts the entities (currency and amount) in the given text using spacy's matcher.

    Args:
        text (str): This is the input text for information mining. 
        patterns (list): A list of patterns for extracting the entities currency (eg : EUR) and amount (eg : 10,000) from the input text.

    Returns:
        entity_list (list): The function returns a list of tuples (currency, amount) detected from the input text  """
    
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

    

def get_results(text):

    """The function contains the entire logic for the information extraction from given financial texts. 

    Args:
        text (str): This is the input text for information mining. 

    Returns:
        results (dict): The function returns a dictionary object, where a key corresponds to a datapoint and the value corresponds to the 
        extracted information  """


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


def extract(input_data):
    """The function is used to build the extraction logic for ISDA datapoint
    extraction from the list of text inputs. Write your code logic in this function.

    Args:
        input_data (list): The input is a list of text or string from which the datapoints need to be extracted

    Returns:
        list: the function returns a list of dictionary values which contains the predictions for the input
              text. Note: The predictions should not be in a misplaced order.
              Example Output:
              [
                  {
                        "delivery_currency": "USD",
                        "delivery_amount": "10,000",
                        "delivery_rounding": "nearest",
                        "return_currency": "USD",
                        "return_amount": "10,000",
                        "return_rounding": "nearest"
                  },
                  ...
              ]
    """

    print("Total documents to process: ", len(input_data))
    
    predicted_output = []
    
    for text in input_data:
        result = get_results(text)
        predicted_output.append(result)

    return predicted_output


def evaluate(input_data, predicted_output):
    """The function computes the accuracy for each of the datapoints
    that are part of the information extraction problem.

    Args:
        input_data (list): The input is a list of dictionary values from the isda json file
        predicted_output (list): This is a list which the information extraction algorithm should extract from the text

    Returns:
        dict: The function returns a dictionary which contains the number of exact between the input and the output
    """

    result = defaultdict(lambda: 0)
    for i, input_instance in enumerate(input_data):
        for key in DATAPOINTS:
            if input_instance[key] == predicted_output[i][key]:
                result[key] += 1

    # compute the accuracy for each datapoint
    for key in DATAPOINTS:
        print(key, 1.0 * result[key] / len(input_data))

    return result


if __name__ == "__main__":
    path = "./data/isda_data.json"
    json_data = read_json(path)
    text_data = [data['text'] for data in json_data]

    # write your extract logic in the extract function
    predicted_output = extract(text_data)
    result = evaluate(json_data, predicted_output)
