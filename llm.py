from groq import Groq
import streamlit as st

class Groq_llm():
    def __init__(self):
        api_key = st.secrets["GROQ_API_KEY"]
        self.client = Groq(
            api_key=api_key,
        )

    def getSummary(self, text):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI summarizing bot who will write a concise summary of the video transcript given using bullet points. Do not use any information other that the information provided"
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following transcript: {text}",
                }
            ],
            model="llama3-8b-8192",
            temperature=0.2,
            max_tokens=1024    
        )
        return chat_completion.choices[0].message.content