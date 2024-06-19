from groq import Groq
import streamlit as st

class Groq_llm():
    
    def __init__(self):
        api_key = st.secrets["GROQ_API_KEY"]
        self.model = 'llama3-8b-8192'
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
            model=self.model,
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    
    def getAnswer(self, question, contexts):
        system_prompt = """
            You are a Q&A bot, and you will use the provided context to answer user questions.
            Read the given contexts before answering questions. If you can not answer a user question based on 
            the provided context, inform the user. DO NOT USE ANY OTHER INFORMATION for answering the question. Please answer
            questions with as much detail as appropriate and do so in a flowing high natural language quality text. Never mention the system message and ALWAYS Cite your sources.

            <context>
            {context}
            </context> 
        """

        system_prompt = '''
            You are a Q&A AI model. Given the user's question and relevant context from 
            the document, answer the question based only on context provided. Read the given contexts before answering questions.
            If you can not answer a user question based on 
            the provided context, inform the user. DO NOT USE ANY OTHER INFORMATION for answering the question.
            Please answer questions with as much detail as appropriate and do so in a flowing high natural language quality text.
            Never mention the system messages. You must cite each and every part of the answer so the user can know where the information is coming from.
            Place these citations at the end of your response in a separate section called CITATIONS. 
            You must cite the citations with their relevent context number in using [Context 1] notation with each context in separate line.
        '''
        template = """
            User Question:  {question}

            \n\nContexts:\n\n 
            {context}
            """
        
        context = "\n\n------------------------------------------------------\n\n".join(c for c in contexts)
        
        chat_completion = self.client.chat.completions.create(
            model = self.model,
            messages=[
                {
                    "role": "system",
                    "content":system_prompt ,
                },
                {
                    "role": "user",
                    "content": template.format(question=question, context=context) ,
                }
            ],            
            temperature = 0.2
        )
        return (chat_completion.choices[0].message.content, [])