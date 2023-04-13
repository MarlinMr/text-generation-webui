'''

Contributed by SagsMug. Thank you SagsMug.
https://github.com/oobabooga/text-generation-webui/pull/175

'''

import asyncio
import json
import random
import string

import websockets

# Note, Gradio may pick a different fn value as the definition of the Gradio app changes.
# You can always launch the web UI and inspect the websocket stream using your browser's dev tools
# to determine what value Gradio expects here.
GRADIO_FN = 29


def random_hash():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(9))


async def run(context):
    server = "localhost"
    params = {
        'max_new_tokens': 50,
        'do_sample': True,
        'temperature': 0.5,
        'top_p': 0.9,
        'typical_p': 1,
        'repetition_penalty': 1.05,
        'encoder_repetition_penalty': 1.0,
        'top_k': 0,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'custom_stopping_strings': [],
        'ban_eos_token': False,
        'custom_stopping_strings': "Question:"
    }
    payload = json.dumps([context, params])
    session = random_hash()
    async with websockets.connect(f"ws://{server}:7860/queue/join") as websocket:
        while content := json.loads(await websocket.recv()):
            # Python3.10 syntax, replace with if elif on older
            match content["msg"]:
                case "send_hash":
                    await websocket.send(json.dumps({
                        "session_hash": session,
                        "fn_index": GRADIO_FN
                    }))
                case "estimation":
                    pass
                case "send_data":
                    await websocket.send(json.dumps({
                        "session_hash": session,
                        "fn_index": GRADIO_FN,
                        "data": [
                            payload
                        ]
                    }))
                case "process_starts":
                    pass
                case "process_generating" | "process_completed":
                    yield content["output"]["data"][0]
                    # You can search for your desired end indicator and
                    #  stop generation by closing the websocket here
                    if (content["msg"] == "process_completed"):
                        break

#prompt = "What I would like to say is the following: "
while True:

    context = "ChatGPT's Persona: ChatGPT's primary function is to interact with users through natural language processing, which means it can understand and respond to text-based queries in a way that is similar to how humans communicate with each other. It's trained on vast amounts of data and algorithms that allow it to generate responses based on patterns and associations in language. It's goal is to provide helpful and informative responses to the best of it's abilities within the scope of it's programming and knowledge. \n <START> \n You: Why is the sky blue? \n ChatGPT: The blue color of the sky is due to a phenomenon called Rayleigh scattering, named after the British physicist Lord Rayleigh, who first explained it in the 19th century. When sunlight enters the Earth's atmosphere, it encounters tiny molecules of gases and other particles. These molecules scatter the sunlight in all directions, but the shorter, blue wavelengths of light are scattered more than the longer, red wavelengths. This is because blue light has a shorter wavelength and higher frequency than red light, which makes it more easily scattered by the small atmospheric particles. As a result, when we look up at the sky, we see the blue light that has been scattered all around us. At sunrise or sunset, however, the sky often appears red or orange because the sunlight has to travel through more of the Earth's atmosphere, and the blue light has been scattered away, leaving mostly the longer, red wavelengths to reach our eyes. \n You: Interesting, can you give me the equations for Einstein's theory of relativity? \n ChatGPT: Yes, I can provide you with some of the equations used in Einstein's theory of relativity: The equation for time dilation: t' = t / sqrt(1 - v^2/c^2) Where t' is the time experienced by an observer moving at a velocity v relative to an observer at rest, t is the time measured by the observer at rest, c is the speed of light in a vacuum. The equation for length contraction: L' = L * sqrt(1 - v^2/c^2) Where L' is the length of an object as measured by an observer moving at a velocity v relative to an observer at rest, L is the length of the object measured by the observer at rest. The equation for energy-mass equivalence: E = mc^2 Where E is the energy equivalent of a mass m, c is the speed of light in a vacuum. These equations are just a few of the key equations used in Einstein's theory of relativity. They describe some of the fundamental principles of the theory, such as time dilation, length contraction, and the equivalence of energy and mass.You: People seem to tend to have a shallow amount of contextualization when having conversations with them.  Does that make sense? They seem to limit the thoughts they contextualize to reach a conclusion.  Like they compartmentalize all knowledge and see information as discrete and separate from most other pieces of information.\n ChatGPT: Yes, what you're describing is a common phenomenon in communication and human cognition. It's known as compartmentalization or mental silos - the tendency for people to organize their knowledge into discrete, disconnected compartments or categories, rather than seeing the connections and interrelationships between different pieces of information. This can lead to shallow contextualization in conversations because people may not consider how the information they're discussing is related to other knowledge they have. They may not connect the dots between different concepts or ideas, or they may not recognize the broader context in which the information exists. As a result, conversations may lack depth or nuance, and important insights or connections may be missed There are a variety of reasons why people compartmentalize their knowledge, including cognitive biases, limited attention and working memory, and the way knowledge is taught and learned in formal education. However, it's important to recognize this tendency in ourselves and others and to actively work to overcome it by seeking out connections and thinking more holistically about the information we encounter. This can lead to more meaningful and productive conversations, as well as a deeper and more nuanced understanding of the world around us. " 

    greeting = "Hello there! How can I help you today? Do you have any questions or topics you'd like to discuss?"


    prompt = input("Prompt: ")

    guide = f"Common sense question and answers \n Question: {prompt} Factual answer:"

    async def get_result():
        async for response in run(guide):
            # Print intermediate steps
            answer = response.replace(guide, "", 1)
            print(answer)

        # Print final result
        print(response)

    asyncio.run(get_result())
