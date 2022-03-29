from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())




keys = ''  # <------------ API keys goes here
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
                    max_concepts=35 # <---- sets how many words Clarifai will genererate related the image provided
                )
            )
        )
    ),
    metadata=metadata
)

if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
    raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

output = post_model_outputs_response.outputs[0]


# Prints out all the words Clarifai generates 
for concept in output.data.concepts:
    if concept.value > 0.7: # <---------- outputs are filtered based on the confidence level
        print("%s %.2f" % (concept.name, concept.value))


