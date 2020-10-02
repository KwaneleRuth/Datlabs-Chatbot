#!/usr/bin/python
#title			:actions.py
#description	:Custom Actions
#author			:Kwanele Ndhlovu
#date			:20191121
#version		:0.1
#notes			:Custom actions
#python_version	:3.6.8
#==============================================================================
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Action
import time
import datetime
import csv
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker

"""
=======================================
GENERAL AND UTILITY ACTIONS
"""
class ActionChitchat(Action):
    """Returns the chitchat utterance dependent on the intent"""

    def name(self) -> Text:
        return "action_chitchat"

    def run(self, dispatcher:CollectingDispatcher, 
            tracker: Tracker, domain:Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message["intent"].get("name")
        dispatcher.utter_message(template=f"utter_{intent}")
        return []

class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    def __init__(self) -> None:
        self.intent_mappings = {}
        with open('intent_description_mapping.csv',
                  newline='',
                  encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.intent_mappings[row[0]] = row[1]

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
            ) -> List['Event']:

        intent_ranking = tracker.latest_message.get('intent_ranking', [])
        if len(intent_ranking) > 1:
            diff_intent_confidence = (intent_ranking[0].get("confidence") -
                                      intent_ranking[1].get("confidence"))
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]
        first_intent_names = [intent.get('name', '')
                              for intent in intent_ranking
                              if intent.get('name', '') != 'out_of_scope']
        message_title = "Sorry, I'm not sure I've understood " \
                        "you correctly 🤔 Do you mean..."
        mapped_intents = [(name, self.intent_mappings.get(name, name))
                          for name in first_intent_names]
        entities = tracker.latest_message.get("entities", [])
        entities_json, entities_text = get_formatted_entities(entities)
        buttons = []
        for intent in mapped_intents:
            buttons.append({'title': intent[1] + entities_text,
                            'payload': '/{}{}'.format(intent[0],
                                                      entities_json)})
        buttons.append({'title': 'Something else',
                        'payload': '/escape_loop_intent'})
        dispatcher.utter_message(message_title, buttons=buttons)

        return []


def get_formatted_entities(entities: List[Dict[str, Any]]) -> (Text, Text):
    key_value_entities = {}
    for e in entities:
        key_value_entities[e.get("entity")] = e.get("value")
    entities_json = ""
    entities_text = ""
    if len(entities) > 0:
        entities_json = json.dumps(key_value_entities)
        entities_text = ["'{}': '{}'".format(k, key_value_entities[k])
                         for k in key_value_entities]
        entities_text = ", ".join(entities_text)
        entities_text = " ({})".format(entities_text)

    return entities_json, entities_text
"""
END OF GENERAL AND UTILITY ACTIONS
===========================================
START OF GENESIS HARDCODED COURSE ACTIONS
"""
class ActionFaqModel(Action):
    def name(self):
        return "action_faq_model"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain:Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent_name = tracker.latest_message["intent"]["name"]
        cur_template = "utter_" + intent_name
        dispatcher.utter_message(template=cur_template)
        return []
