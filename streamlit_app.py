from datetime import datetime
import streamlit as st
import asyncio
import uuid
from agentss.faqs_agent import faqs_agent
from agentss.vision_agent import vision_tool
from agents import Runner
from dotenv import load_dotenv
import os

load_dotenv()  

openai_key = st.secrets['OPENAI_API_KEY']

if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

st.secrets['OPENAI_API_KEY'] = openai_key



st.set_page_config(
    page_title="Billy",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)



if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
                "role": "assistant",
                "content": "Hello I'm Billy! You can ask me about FAQs, make promise to pay (PTP), and process transaction reciepts. What can I help with? 😊",
                "timestamp": datetime.now().strftime("%I:%M %p")
            }]

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

if "processing_image" not in st.session_state:
    st.session_state.processing_image = None




def handle_user_message(user_input: str):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input.text,
        "timestamp": timestamp
    })
    
    st.session_state.processing_message = user_input.text


def handle_user_image(user_input: str):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input.text,
        "image": user_input["files"][0] if user_input.get("files") else None,
        "timestamp": timestamp
    })

    st.session_state.processing_image = user_input["files"][0]


st.title("💸 Billy")
st.caption("Billease Customer Assistant")
    

for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=default" class="avatar" />
                    <div class="message">
                        <div>{message["content"]}</div>
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if "image" in message and message["image"] is not None:
                try:
                    st.image(message["image"], width=300, use_container_width=False)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


user_input = st.chat_input("Ask Billy...", accept_file=True, file_type=["png", "jpg"])
if user_input:
    if len(user_input["files"]) == 0:
        handle_user_message(user_input)
    else:
        handle_user_image(user_input)
    st.rerun()


if st.session_state.processing_message:
    user_input = st.session_state.processing_message
    st.session_state.processing_message = None

    with st.spinner("Thinking..."):
        try:
            if len(st.session_state.chat_history) > 1:
                input_list = []
                for msg in st.session_state.chat_history:
                    input_list.append({"role": msg["role"], "content": msg["content"]})
            else:
                input_list = user_input
            result = asyncio.run(Runner.run(
                starting_agent=faqs_agent, 
                input=input_list
            ))

            st.session_state.chat_history.append({
                "role": "assistant",
                "content":  result.final_output,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        st.rerun()

if st.session_state.processing_image:
    user_input = st.session_state.processing_image
    st.session_state.processing_image = None

    with st.spinner("Processing image..."):
        try:
            image_analysis = vision_tool(user_input)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content":  image_analysis,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            
        st.rerun()