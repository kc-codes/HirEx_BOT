import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai  # Assuming the library is installed

# Load environment variables
# load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with HirEx!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model (using TextGenerationSession if applicable)
try:
    from google.generativeai import TextGenerationSession  # Import for potential context manager
    with TextGenerationSession(api_key=GOOGLE_API_KEY) as session:
        model = session  # Assign session to model if using context manager
except ImportError:  # Fallback for potential absence of TextGenerationSession
    gen_ai.configure(api_key=GOOGLE_API_KEY)
    model = gen_ai.GenerativeModel('gemini-pro')  # Use GenerativeModel if no context manager

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])


# Display the chatbot's title on the page
st.title(" 🤖  HirEx - ChatBot")

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)


# Input field for user's message
user_prompt = st.chat_input("Ask HirEx...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Function to check if a prompt is within the chatbot's scope
    def is_on_topic(prompt):
        # Customize keywords for interview and resume topics
        keywords = ["interview", "interview tips", "resume", "resume advice", "job search", "hire", "career", "job", "work", "employment", "professional", "skills"]
        return any(keyword in prompt.lower() for keyword in keywords)

    # Check if the prompt is within scope
    if is_on_topic(user_prompt):
        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(user_prompt)
    else:
        # Reply with out-of-scope message
        try:
            # Attempt using TextGenerationSession if applicable
            gemini_response = session.generate_text(
                prompt="I'm sorry, that's outside my scope of expertise. I'm focused on helping with interview and resume topics. Would you like to try rephrasing your question?"
            )
        except:
            # Fallback for potential absence of TextGenerationSession
            gemini_response = "I'm sorry, that's outside my scope of expertise. I'm focused on helping with interview and resume topics. Would you like to try rephrasing your question?"

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        if isinstance(gemini_response, str):
            st.markdown(gemini_response)
        else:
            st.markdown(gemini_response.text)

# Clear chat window button
if st.sidebar.button("Clear Chat Window", use_container_width=True, type="primary"):
    st.session_state["chat_session"].history = []  # Clear history within chat session

