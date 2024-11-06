import chromadb
import ollama  # Assuming ollama is imported correctly
"""
from langchain_ollama import ollama
from langchain_core.prompts import ChatPromptTemplate

model = ollama(model="llama3.1")
client = chromadb.Client()
"""
client = chromadb.Client()
# Sample message history
message_history = [
    {
        'id': 1,
        'prompt': 'What is my name',
        'response': 'Your Name is Patton, known online as Justsimple.'
    },
    {
        'id': 2,
        'prompt': 'What is the square root of 9876',
        'response': '99.3780659904'
    },
    {
        'id': 3,
        'prompt': 'What kind of dog do I have',
        'response': 'Your dog Max is a Labradoodle breed. A labradoodle is a crossbreed dog created by crossing a Labrador Retriever and a Standard or Miniature Poodle'
    }
]

# Conversation storage
convo = []

# Streaming response function
def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})
    response = ''
    stream = ollama.chat(model='llama3.1', messages=convo, stream=True)
    print('\nASSISTANT: ')

    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)
    
    print('\n')
    convo.append({'role': 'assistant', 'content': response})

# Vector database creation function
def create_vector_db(conversations):
    vector_db_name = 'conversations'

    try:
        client.delete_collection(name=vector_db_name)
    except ValueError:
        pass  # Ignore if collection doesn't exist

    vector_db = client.create_collection(name=vector_db_name)

    # Process conversations to store embeddings
    for c in conversations:
        serialized_convo = f"prompt: {c['prompt']} response: {c['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']

        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )

# Retrieve embeddings based on user prompt
def retrieve_embeddings(prompt):
    response = ollama.embeddings(model='nomic-embed-text', prompt=prompt)
    prompt_embedding = response['embedding']

    vector_db = client.get_collection(name='conversations')
    results = vector_db.query(query_embeddings=[prompt_embedding], n_results=1)
    best_embedding = results['documents'][0][0]  # Adjust path as per result structure

    return best_embedding

# Build vector database
create_vector_db(conversations=message_history)

# Chat handling with retrieval
def handle_conversation():
    print("Welcome to the llama3.1 RAG AI Chatbot! Type 'exit' to quit.")
    while True:
        prompt = input("User: \n")
        if prompt.lower() == "exit":
            break
        # Retrieve context from embedding
        context = retrieve_embeddings(prompt=prompt)
        # Format prompt with context
        formatted_prompt = f'USER PROMPT: {prompt} \nCONTEXT FROM EMBEDDINGS: {context}'
        stream_response(prompt=formatted_prompt)

if __name__ == "__main__":
    handle_conversation()