import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from llm import Groq_llm

def main():
    col1, col2 = st.columns(2)
    summary_placeholder = st.empty()

    text_input = col1.text_input("Enter YouTube URL:")
    button_container = col2.container()
    button_container.write("")
    button_container.write("")

    if button_container.button("Submit"):
        videoID = text_input[(text_input.index("v=") + 2) : text_input.index("&")]
        transcriptArray = YouTubeTranscriptApi.get_transcript(videoID)
        if transcriptArray == None:
            st.error("There is no transcript for this URL.") 
        else:
            transcript = ""
            for dict in transcriptArray:
                transcript += dict['text'] + " "
            llm = Groq_llm()
            summary = llm.getSummary(transcript)
            summary_placeholder.markdown(summary)
    


if __name__ == "__main__":
    main()