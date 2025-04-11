from datetime import datetime
import streamlit as st
import asyncio
import uuid
from agentss.faqs_agent import faqs_agent_openai
from agentss.faqs_agent import faqs_agent_gemini
from agentss.vision_agent import vision_tool
from agents import Runner
from dotenv import load_dotenv
import os

load_dotenv()  

openai_key = st.secrets['OPENAI_API_KEY']
# openai_key = os.getenv('OPENAI_API_KEY')

if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# st.secrets['OPENAI_API_KEY'] = openai_key



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

if "model_type" not in st.session_state:
    st.session_state.model_type = None

if "chinput" not in st.session_state:
    st.session_state.chinput = False

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

def user_inpt():
    user_input = st.chat_input("Ask Billy...", accept_file=True, file_type=["png", "jpg"])
    if user_input:
        if len(user_input["files"]) == 0:
            handle_user_message(user_input)
        else:
            handle_user_image(user_input)
        st.rerun()

# Sidebar for user preferences
with st.sidebar:
    # st.title("Travel Preferences")

    st.subheader("Chatbot Preference")
    preferred_model = st.multiselect(
        "Select Model Type (only choose 1)",
        ["OpenAI", "Gemini"],
    )


    if st.button("Save Preferred Model"):
        st.session_state.chinput = True
        if len(preferred_model) != 1:
            st.warning("Please select exactly one model.")
        else:
            selected = preferred_model[0]
            st.session_state.model_type = selected
            # st.write(f"Using model: {st.session_state.model_type}")
            st.success("Preferred model saved!")

    st.divider()
    
    if st.button("Start New Conversation"):
        st.session_state.chat_history = [{
                "role": "assistant",
                "content": "Hello I'm Billy! You can ask me about FAQs, make promise to pay (PTP), and process transaction reciepts. What can I help with? 😊",
                "timestamp": datetime.now().strftime("%I:%M %p")
            }]
        st.session_state.model_type = None
        st.success("New conversation started! Pick a model again.")


st.title("💸 Billy")
st.caption("Billease Customer Assistant")
st.info('Made using gpt-4o-mini & gemini-2.0-flash model', icon="🤖")
    

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

if st.session_state.chinput == True:  
    user_inpt()


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
                # First message
                input_list = user_input
            if st.session_state.model_type == "OpenAI":
                result = asyncio.run(Runner.run(
                starting_agent=faqs_agent_openai,
                input=input_list
                ))
            
            elif st.session_state.model_type == "Gemini":
                result = asyncio.run(Runner.run(
                starting_agent=faqs_agent_gemini,
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
