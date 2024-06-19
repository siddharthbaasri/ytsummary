import cohere
import streamlit as st

class Cohere_llm():

    def __init__(self):
        api_key = st.secrets["COHERE_API_KEY"]
        self.client = cohere.Client (
            api_key=api_key,
        )

    def getSummary(self, text):
        message = """
            ## Instructions
            Please summarize the salient points of the text and do so in a flowing high natural language quality text. Use bullet points where appropriate.

            ## Input Text
            {input_text}
            """
        response = self.client.chat(
            model = "command-r-plus",
            message = message.format(input_text=text),
            temperature = 0.2
        )
        return response.text
    
    def getAnswer(self, text, contexts):
        template = """
            ## Instructions
            You are a Q&A AI model. Given the user's question and relevant context from 
            the document, answer the question based only on the documents provided. Read the given documents before answering questions.
            If you can not answer a user question based on 
            the provided documents, inform the user. DO NOT USE ANY OTHER INFORMATION for answering the question.
            Please answer questions with as much detail as appropriate and do so in a flowing high natural language quality text.
            Never mention the system messages. You must cite each and every part of the answer so the user can know where the information is coming from.

            ## Question
            {question}
            """
        
        response = self.client.chat (
            model="command-r-plus",
            message=template.format(question = text),
            documents = [{"title": "", "snippet": c} for c in contexts],
            temperature=0.2
        )
        docs = None
        if (response.citations != None):
            docs = list(set([response.citations[i].document_ids[0] for i in range(0, len(response.citations))]))    
        else: 
            docs = []    
        return (response.text, docs)
    
    