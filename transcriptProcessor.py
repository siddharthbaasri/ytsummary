#from groq_llm import Groq_llm
from cohere_llm import Cohere_llm
import chromadb

class TranscriptProcessor():
    def __init__(self, transcriptArray):
        self.transcriptArray = transcriptArray
        chroma_client = chromadb.Client()
        if "chunk_embeddings" not in [collection.name for collection in chroma_client.list_collections()]:
            self.collection = chroma_client.create_collection(name="chunk_embeddings")
        else:
            self.collection = chroma_client.get_collection(name = "chunk_embeddings")
        self.transcriptChunks = self.combineTranscriptChunks(transcriptArray)
        self.addChunksToDb()
        #self.llm = Groq_llm()
        self.llm = Cohere_llm()
    
    #Method splits the transcript into chunks and returns the summary of the text
    def getSummary(self):
        sentenceChunks = self.__getChunks()
        summaries = ""
        for chunk in sentenceChunks:
            summary = self.llm.getSummary(chunk)
            summaries = summaries + " " + summary    
        return self.llm.getSummary(summaries) 
    
    #Combines chunks into ~30 sec fragments
    def combineTranscriptChunks(self, transcriptArray):
        chunks = []
        for i in range(0, len(transcriptArray) - 5, 5):
            text = ""
            for j in range(0, 5):
                text += transcriptArray[i + j]['text']
            chunks.append({"text": text, "timestamp": transcriptArray[i]['start']})
        return chunks
    
    #Combines chunks into ~30 sec fragments with overlap, and adds these the the chroma database for embeddings
    def addChunksToDb(self):
        chunks = []
        for i in range(0, len(self.transcriptArray) - 5, 3):
            text = ""
            for j in range(0, 5):
                text += self.transcriptArray[i + j]['text'] + " "
            chunks.append({"text": text, "timestamp": self.transcriptArray[i]['start']})

        self.collection.add (
            documents = [chunks[i]['text'] for i in range(0, len(chunks))],
            ids = [str(i) for i in range(len(chunks))],
            metadatas = [{"timestamp": chunks[i]['timestamp']} for i in range(0, len(chunks))]
        )
        return chunks
    
    #Gets the chunks in order to feed to LLM
    def __getChunks(self):
        sentenceChunks = []
        chunk = ""
        for sentence in self.transcriptChunks:
            if len(chunk) + len(sentence) < 8000:
                chunk = chunk + " " + sentence['text']
            else:
                sentenceChunks.append(chunk)
                chunk = ""
        sentenceChunks.append(chunk)
        return sentenceChunks
    
    #Gets the answer for a question the user asks by looking up nearest matches in the chroma DB
    def getAnswer(self, question):
        results = self.collection.query(
            query_texts=[question], 
            n_results=10
        )
        index = 0
        for distance in results['distances'][0]:
            #Ignore results which are irrelevant
            if distance > 1:
                break
            index += 1
        contexts = results['documents'][0][:index]
        answer_data = self.llm.getAnswer(question, contexts)
        times = []
        for i in range(0, len(answer_data[1])):
            index = int(answer_data[1][i][4:])
            times.append(results['metadatas'][0][index]['timestamp'])
        times = self.__combineTimes(sorted(times))
        return (answer_data[0], times)
    
    #Combine times that are close by to each other
    def __combineTimes(self, times):
        if len(times) == 0:
            return times
        arr = [times[0]]
        lastTime = times[0]
        for i in range(1, len(times)):
            if times[i] - lastTime < 30:
                continue
            arr.append(times[i])
            lastTime = times[i]
        return arr