from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from typing import List

client = MongoClient("mongodb+srv://user:password@mongo-cluster.xxxx.mongodb.net/?retryWrites=true&w=majority&appName=Mongo-Cluster")
db = client["testdb"]
collection = db["my_ai_application"]

new_question_modifier = """
Your primary task is to determine if the latest question requires context from the chat history to be understood.

IMPORTANT: If the latest question is standalone and can be fully understood without any context from the chat history or is not related to the chat history, you MUST return it completely unchanged. Do not modify standalone questions in any way.

Only if the latest question clearly references or depends on the chat history should you reformulate it as a complete, standalone legal question. When reformulating:

"""

def get_last_three_questions(session_id: str) -> List[str]:
    """
    Retrieves the last three questions asked by a user in a specific chat session.

    Args:
        session_id (str): The unique identifier for the chat session.

    Returns:
        List[str]: A list containing the last three questions asked by the user,
                   ordered from most recent to oldest.
    """
    query = {"sessionid": session_id}
    results = collection.find(query).sort("updatedAt", -1).limit(3)
    #print("results..", results)
    questions = [result["question"] for result in results]
    print("questions..", questions)
    return questions

def insert_chat_history(sessionid:str, prompt: str):
    document = {
    "question": prompt,
    "response": "Nan",
    "sessionid": sessionid,
    "updatedAt": datetime.now()
    }

    # Insert the document into the collection
    result = collection.insert_one(document)
    print(f"Inserted document with _id: {result.inserted_id}")


def cleanup_memory():
    # get
    lastthree = collection.find().sort("updatedAt", -1).limit(3)
    lastthreeids = [doc['_id'] for doc in lastthree]
    result = collection.delete_many({ "_id" : { "$nin": lastthreeids }})


    
