
# Assume openai>=1.0.0
from openai import OpenAI

# Create an OpenAI client with your KRUTRIM API KEY and endpoint

openai = OpenAI(
    api_key="murehQRXdX_dVOw4lknJ",  # Refer to Create a secret key section
    base_url="https://cloud.olakrutrim.com/v1",
)



def prompt_response(x):
    chat_completion = openai.chat.completions.create(
        model="Krutrim-spectre-v2",
        messages=[
            {"role": "system", "content": f"please generate the crisp and upto the point text for {x}. It should be in 3-4 lines to generate the audio of 15-20 seconds max "},
        ],
        frequency_penalty=0,  # Optional, Defaults to 0. Range: -2 to 2
        logit_bias={2435: -100, 640: -100},
        logprobs=True,  # Optional, Defaults to false
        top_logprobs=2,  # Optional. Range: 0 to 50
        max_tokens=256,  # Optional
        n=1,  # Optional, Defaults to 1
        presence_penalty=0,  # Optional, Defaults to 0. Range: -2 to 2
        response_format={"type": "text"},  # Optional, Defaults to text
        stop=[],
        # Optional, Defaults to null. Can take up to 4 sequences where the API will stop generating further tokens.
        stream=False,  # Optional, Defaults to false
        temperature=0,  # Optional, Defaults to 1. Range: 0 to 2
        top_p=1  # Optional, Defaults to 1. We generally recommend altering this or temperature but not both.
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


def process_input(user_input):
    # Convert to lowercase
    input_lower = user_input.lower()
    print(input_lower)
    # Vehicle command detection
    commands = {
        ('high beam', 'on'): '0x02',
        ('high beam', 'off'): '0x03',
        ('right', 'indicator', 'on'): '0x04',
        ('right indicator', 'off'): '0x05',
        ('left indicator', 'on'): '0x06',
        ('left indicator', 'off'): '0x07',
        ('turn on', 'normal mode'): '0x0A',
        ('on', 'sport mode'): '0x0B',
        ('turn on', 'hyper mode'): '0x0C',
        ('turn on', 'eco mode'): '0x0D',
        ('unlock', 'scooter'): '0x0E',
        ('turn on', 'reverse mode'): '0x0F',
        ('turn on', 'park mode'): '0x10',
        ('turn on', 'custom mode'): '0x11',
        ('safety lights', 'on'): '0x12',
        ('safety lights', 'off'): '0x12',
        ('unlock', 'trunk'): '0x13',
        ('turn off', 'regen'): '0x14',
        ('set regen', 'low'): '0x15',
        ('set regen', 'default'): '0x16',
        ('set regen', 'high'): '0x17',
        ('increase volume',): '0x18',
        ('volume up',): '0x18',
        ('next track',): '0x19',
        ('lock', 'scooter'): '0x01',
        ('diagnose','scooter'): '0x20'

    }

    # Check for command matches
    for keywords, hex_code in commands.items():
        if all(keyword in input_lower for keyword in keywords):
            print("This is the keyword:",keywords)
            print("This is the hexcode:",hex_code)
            return hex_code
    return "None"

if __name__ == "__main__":
    command = "How is the weather today"
    output = process_input(command)
    print(output)


# while True:
#     user_request = input("You want to exit (Y/N)")
#     if user_request == "N":
#         prompt_response()
#     if user_request == "Y":
#         break