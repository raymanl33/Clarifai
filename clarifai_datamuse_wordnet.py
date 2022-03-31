import re
from pprint import pprint
from datamuse import Datamuse
from nltk.corpus import wordnet as wn
from json import dumps, loads

## Clarifai API Call ============================================
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

keys = '' # <------------ API keys goes here
metadata = (('authorization', f'Key {keys}'),)


post_model_outputs_response = stub.PostModelOutputs(
    service_pb2.PostModelOutputsRequest(
        model_id='aaa03c23b3724a16a56b629203edc62c', # <---------- model used: General 
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        url="" # <------ paste image URL link here 
                    )
                )
            )
        ],
        model=resources_pb2.Model(
            output_info=resources_pb2.OutputInfo(
                output_config=resources_pb2.OutputConfig(
                    max_concepts=200 # <---- sets how many words Clarifai will genererate related the image provided
                )
            )
        )
    ),
    metadata=metadata
)

if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
    raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

output = post_model_outputs_response.outputs[0]
# Clarifai call ends ================================================


# Categories uesed to answer 4 high-level questions. Exlucding the category qurstion  =======================================
wordnet_category = {'Place': ['building', 'room', 'place_parts', 'structure', 'facility', 'region', 'geological_formation'],
                    'Look' : ['body_part', 'nature_object','container', 'fastner', 'animal_skin', 'geological_formation', 
                    'natural_object', 'meat', 'vegetable', 'facility',
                    'home appliance', 'furniture'],             
                    'Association': ['person', 'region', 'facility', 'clothing', 'natural_object', 'region', 'feeling'
                    'tool', 'symbol', 'beverage', 'worker' ], 
                    'Function': ['tool']}


place = []
look = []
association = []
function = []
# =========================================================

def main():
    data = load_data("files/new.json")
    r = True
    # list of words generated from Clarifai are passed into the function test() ===========
    for concept in output.data.concepts:
        if concept.value > 0.7:
            test(data, concept.name)
    # =========================================



def test(category, word=''):
    temp = {"first": [], "second": [], 'not_found': True}
    try:
        """Categorizing word from unique 8 digit value"""
        word = int(word)
        syn = wn.synset_from_pos_and_offset(wn.NOUN, word)
        offset_check(syn, category, temp, syn._name.split('.')[0])
        # display(temp)
    except ValueError:
        """ Categorizing word from the word form """
        word.replace(' ', '_')
        syns = wn.synsets(word)
        for syn in syns:
            offset_check(syn, category, temp, word)

def display(temp: dict) -> None:
    if not temp['not_found']:
        print(f"{'Main Category':-^110}")
        print(f"{'Word':<30}{'Synset':<30}{'Sub Category':<30}{'Main Category':<30}")
        display_helper(temp['first'][0])


def display_helper(arr: list) -> None:
    word = arr[0]
    syn = arr[1]
    sub_category = arr[2]
    main_category = arr[3]
    print(f"{word:<30}{syn:<30}{sub_category:<30}{main_category:<30}")


def offset_check(syn: wn.synset, category: list, temp, word: str = ''):
    parent = [x._name for x in list(syn.closure(lambda x: x.hypernyms()))]
    for key in category:
        syns = category[key]
        for s in parent:
            if s in syns:
                # Words generated from Clarifai are sorted into 4 high-level questions ==========
                # Place = Where is it found? 
                # Look = What does it look like (parts)?
                # Assiciation = What does it associate with?
                # Function = What does it do (function)?
                split_string = s.split('.',1)  
                substring = split_string[0]
                for key, value in wordnet_category.items():
                    if substring in value:
                        if key == 'Place':
                            place.append(word)
                        elif key == 'Look':
                            look.append(word)
                        elif key == 'Association':
                            association.append(word)
                        elif key == 'Function':
                            function.append(word)
                # =================================================
        


def load_data(filename: str = "files/category.json") -> dict: # <--- look for category.json inside the files folder 
    with open(filename, 'r') as f:
        data = loads(f.read())
    return data


if __name__ == '__main__':
    main()
    print("=" * 50)
    print(f'Where is it found: {set(place)}')
    print(f'What does it look like: {set(look)}')
    print(f'Association: {set(association)}')
    print(f'Function: {set(function)}') 