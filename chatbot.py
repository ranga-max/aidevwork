#!/usr/bin/env python
# =============================================================================
#
# Consume messages from Confluent Cloud
# Using Confluent Python Client for Apache Kafka
# Reads Avro data, integration with Confluent Cloud Schema Registry
# Call
# python icebreaker.py -f client.properties -t shoe_promotions
# avro consumer sample : https://github.com/confluentinc/examples/blob/7.5.0-post/clients/cloud/python/consumer_ccsr.py
# =============================================================================
# Confluent
import confluent_kafka
from confluent_kafka import DeserializingConsumer
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer
#from confluent_kafka.serialization import StringDeserializer
#from confluent_kafka.serialization import StringSerializer
#import ccloud_lib
# AI
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
#from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain_community.vectorstores import Pinecone as PineconeVectorstore
from langchain.chains import RetrievalQA
from langchain_pinecone import PineconeVectorStore
from langchain.chains import LLMChain
#from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from tools.linkedin import scrape_linkedin_profile
#from tools.linkedin_lookup_agent import lookup as linkedin_lookup_agent
# General
import json,sys,logging,time
import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from pinecone import Pinecone, ServerlessSpec
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from langchain_core.documents import Document
from dotenv import load_dotenv

pc = PineconeGRPC(api_key="local-key", host="http://localhost:5081", ssl=False)
index_name = "ragiest"
#pc.delete_index(name="ragiest")
print(pc.list_indexes().names())

#if index_name not in pc.list_indexes().names():
if not pc.has_index(index_name):      
    index_model = pc.create_index(
                  name=index_name,
                  dimension=1536,
                  spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
parse_index_host = pc.describe_index(name=index_name).host   
print(parse_index_host)
#OPENAIKEY = os.environ["OPENAI_API_KEY"]
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
azendpoint = "https://models.inference.ai.azure.com"
#model_name = "openai/gpt-4o"
model_name = "meta/Llama-4-Scout-17B-16E-Instruct"
embedding_model_name = "text-embedding-3-small"
#PROXYCURL_API_KEY = os.environ["PROXYCURL_API_KEY"]
#SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=token, base_url=azendpoint)
#index = pc.Index(name=index_name, grpc_config=GRPCClientConfig(secure=False))

class Url(object):

    def __init__(self, url=None, prompt=None, sub_area=None, url_flag=None, rag_flag=None, text_input=None):
        self.url = url
        self.prompt = prompt
        self.sub_area = sub_area
        self.url_flag = url_flag
        self.rag_flag = rag_flag
        self.text_input = text_input

def generate_id_from_timestamp():
  """Generates a numeric ID based on the current timestamp."""
  return int(time.time())

def dict_to_url(obj, ctx):
    if obj is None:
        return None

    return Url(url=obj['url'],
               prompt=obj['prompt'], 
               sub_area=obj['sub_area'],
               url_flag=obj['url_flag'],
               rag_flag=obj['rag_flag'],
               text_input=obj['text_input']
               )

def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))    

if __name__ == "__main__":
    # Read arguments and configurations and initialize

    # ---- Pinecone Setup ---- #
    #PINECONE_API_KEY = '*****'
    #os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    #index = Pinecone(api_key=PINECONE_API_KEY).Index("demo1")
    load_dotenv()
    url_schema_str = """
    {
     "name": "Url",
     "type": "record",
     "fields": [
        {
            "name": "url",
            "type": "string"
        },
        {
            "name": "prompt",
            "type": "string"
        },
        {
            "name": "sub_area",
            "type": "string"
        },
        {
            "name": "url_flag",
            "type": "boolean"
        },
        {
            "name": "rag_flag",
            "type": "boolean"
        },
        {
            "name": "text_input",
            "type": "string"
        }
     ]
      }
      """

    #commonconf = {
    #        'bootstrap.servers': 'ccurl:9092', 
    #        'security.protocol': 'SASL_SSL',
    #        'sasl.mechanism': 'PLAIN',
    #        'sasl.username': 'ccapikey',
    #        'sasl.password': 'ccapipwd'
        #    'schema.registry.url': 'srurl'
        #    'schema.registry.basic.auth.credentials.source': 'USER_INFO',
        #    'schema.registry.basic.auth.user.info': 'srapikey:srapisecret'
    #       }

    commonconf = {
            'bootstrap.servers': os.getenv("CC_URL"),
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': os.getenv("CC_API_KEY"),
            'sasl.password': os.getenv("CC_API_SECRET")
           }

    consumerconf = {
            'group.id': 'testgroup',
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'latest',
            'enable.auto.offset.store': False
            }
    producerconf = {}


    #producerconf = {}
    fromtopic = "ragurldemo"
    outtopic = "ragoutput"
    #totopic = promptresults
    #schema_registry_conf = {
    #    "url": "srurl",
    #    "basic.auth.user.info": "srapikey"
    #}
    sr_url = os.getenv("SR_URL")
    sr_api_key = os.getenv("SR_API_KEY")
    sr_api_secret = os.getenv("SR_API_SECRET")
    sr_user_info_str = str(sr_api_key) + ':' + str(sr_api_secret)
    schema_registry_conf = {
        "url": sr_url,
        "basic.auth.user.info": sr_user_info_str
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    chaturl_avro_deserializer = AvroDeserializer(
        schema_registry_client=schema_registry_client,
        schema_str=url_schema_str,
        from_dict=dict_to_url
    )


    #string_serializer = StringSerializer('utf_8')
    #promptoutput_avro_serializer = AvroSerializer(
    #    schema_registry_client = schema_registry_client,
    #    schema_str =  promptres_schema_str,
    #    to_dict = promptres_to_dict)
   
    # consumer
    # for full list of configurations, see:
    #   https://docs.confluent.io/platform/current/clients/confluent-kafka-python/#deserializingconsumer
    consumerconf.update(commonconf)
    consumer_conf = consumerconf
    consumer_conf["value.deserializer"] = chaturl_avro_deserializer
    consumer = DeserializingConsumer(consumer_conf)
    producerconf.update(commonconf)
    producer_conf = producerconf
    producer = Producer(producer_conf)
    serializer = StringSerializer('utf_8')
    
    message_count = 0
    waiting_count = 0
    # Subscribe to topic
    consumer.subscribe([fromtopic])

    # producer
    #producer_conf = ""
    #producer_conf = producerconf.update(commonconf)
    #producer_conf["value.serializer"] = promptoutput_avro_serializer
    #producer = SerializingProducer(producer_conf)

    delivered_records = 0

    # Process messages
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            elif msg.error():
                print("error: {}".format(msg.error()))
            else:
                url_object = msg.value()
                if url_object is not None:
                    prompt = url_object.prompt
                    if prompt is not None:
                        print(
                            "Consumed record with value {}, Total processed rows {}".format(
                                prompt, message_count
                            )
                        )
                        message_count = message_count + 1
                        message = (
                            "Search for information: "
                            + str(prompt)
                            + " with genAI ice-breaker!"
                        )
                        # Here start with genAI
                        #print("Hello LangChain!")
                        try:
                            url = url_object.url
                            url_flag = url_object.url_flag
                            rag_flag = url_object.rag_flag
                            text_input = url_object.text_input
                            if url_flag and url != "":
                             response = requests.get(url)
                             html_content = response.content
                             html_data = BeautifulSoup(html_content, 'html.parser')
                             text_content = html_data.get_text()
                            else:
                             text_content = text_input   
                            if rag_flag:
                             text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=5000,chunk_overlap=100, length_function=len,
                                is_separator_regex=False,
                              )
                             pages = text_splitter.split_text(text_content)
                            if rag_flag:
                             splitted_documents = text_splitter.create_documents(pages)
                             #print(splited_documents)
                             #index = pc.Index(index_name)
                             index = pc.Index(name=index_name, grpc_config=GRPCClientConfig(secure=False))
                             vectorstore = PineconeVectorStore(embedding=embeddings, index=index)
                             vector_id = generate_id_from_timestamp()
                             vectorstore.add_documents(documents=splitted_documents)
                            # Define tasks for chatgpt
                            llm = ChatOpenAI(temperature=1, model_name="openai/gpt-4o", api_key=token, base_url=endpoint )
                            if not rag_flag:
                             summary_template = """
                                if given the information {text_information} about a topic from I want you to create:
                                1. a short summary of the topic specific to {prompt}
                                if not given try to get the information from your sources
                             """
                             # prepare prompt (chat)
                             summary_prompt_template = PromptTemplate(
                             input_variables=["text_information", "prompt"],
                             template=summary_template,
                             )
                             # create chatgpt instance
                             #llm = ChatOpenAI(temperature=1, model_name="openai/gpt-4o", api_key=token, base_url=endpoint )
                             # LLM chain
                             chain = LLMChain(llm=llm, prompt=summary_prompt_template)
                             non_rag_result = chain.run(text_information=text_content, prompt=prompt)
                            # execute and print result
                            if rag_flag:
                             retriever = vectorstore.as_retriever(search_type="similarity")
                             # Set up RetrievalQA chain
                             qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=False)
                             # Query the model
                             #prompt = summary_prompt_template
                             rag_result = qa({"query": prompt})
                            #print("QA Response:", result)
                            #result = chain.run(url_information=text_content, prompt=prompt)
                            try:
                             if rag_flag:   
                                result = str(rag_result['result'])
                             else:
                                result = str(non_rag_result)
                             #producer.produce(topic=outtopic, value=serializer(str(result['result'])), callback=delivery_callback)
                             producer.produce(topic=outtopic, value=serializer(result), callback=delivery_callback)
                             producer.flush()
                            except Exception as e:
                             print(f"Failed to send message: {e}")
                        except Exception as e:
                            print("An error occured:", e)
        except KeyboardInterrupt:
            break
        except SerializerError as e:
            # Report malformed record, discard results, continue polling
            print("Message deserialization failed {}".format(e))
            pass

    # Leave group and commit final offsets
    consumer.close()
