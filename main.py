__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq_llm import Groq_llm
from transcriptProcessor import TranscriptProcessor

#Method to get the summary of the transcript provided
def get_transcript_summary(video_id):
    transcriptArray = YouTubeTranscriptApi.get_transcript(video_id)
    if transcriptArray == None:
        st.error("There is no transcript for this URL.") 
        return
    
    tp = TranscriptProcessor(transcriptArray)
    st.session_state.TranscriptProcessor = tp
    return tp.getSummary()

# Function to add a message to the chat history
def add_message(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

#initiallzes state variables
def createSessionVariables():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "display_chat" not in st.session_state:
        st.session_state.display_chat = False
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "TranscriptProcessor" not in st.session_state:
        st.session_state.TranscriptProcessor = None
    if "video_link" not in st.session_state:
        st.session_state.video_link = ""

def main():    
    createSessionVariables()
    col1, col2 = st.columns(2)
    textbox = st.empty()

    text_input = col1.text_input("Enter YouTube URL:")
    button_container = col2.container()
    button_container.write("")
    button_container.write("")
    

    if button_container.button("Submit"):
        st.session_state.chat_history = []
        st.session_state.video_link = text_input[(text_input.index("v=") + 2) : text_input.index("&")]        
        st.session_state['summary'] = get_transcript_summary(st.session_state.video_link)
        st.session_state.display_chat = True

    textbox.markdown(st.session_state.summary)
    if st.session_state.display_chat:
        user_input = st.chat_input("Ask any question here")
        # Check if user has entered some text
        if user_input:
            add_message("user", user_input)
            # Process the user input (e.g., send to a language model)
            answer = st.session_state.TranscriptProcessor.getAnswer(user_input)
            #If LLM can't answer, links are not generated
            linkHeader = ""
            if len(answer[1]) != 0:
                linkHeader = "<br/><br/> **Links** <br/> \n"
            links = "\n".join([f"* https://www.youtube.com/watch?v={st.session_state.video_link}&t={str(int(answer[1][i]))}" for i in range(0, len(answer[1]))])
            add_message("assistant", answer[0] + linkHeader + links)

            
        # Display the response from the language model
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html = True)
        

if __name__ == "__main__":
    main()