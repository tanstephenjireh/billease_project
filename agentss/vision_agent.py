from agents import function_tool
from typing import Annotated
from openai import OpenAI
from agents import Agent 
import base64
import os

vision_instruction = """Analyze the text in the provided image. Extract all readable content
and present it that is clear, concise, and well-organized. Ensure proper formatting (e.g., headings, lists, or
code blocks) as necessary to represent the content effectively. Espsecially the key information
including amount and transaction reference number. Do not include unnecessary information.

If the image is blurry or not readable in any way, prompt the user to reupload a clearer version.

Answer in a fun tone and engaging for the customer.
"""

def encode_image(image_pth):
    """Encode uploaded file bytes to base64"""
    print("> encoding image")
    return base64.b64encode(image_pth.getvalue()).decode("utf-8")
    

def vision_tool(image_path):
    """Used to extract readable content from an image input
    """
    print("> vision tool")
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    base64_image = encode_image(image_path)
    print("> done encoding")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": vision_instruction,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error processing image: {str(e)}")


vision_agent = Agent(
    name="Vision Agent",
    handoff_description="Specialist agent for processing images",
    instructions=vision_instruction,
    model="gpt-4o-mini",
    tools=[vision_tool]  # note that we expect a list of tools
)