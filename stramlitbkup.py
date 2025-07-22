import streamlit as st
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
import os
from uuid import uuid4
#from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Kafka configuration (update with your actual config)

def url_to_dict(url, ctx):
    return dict(url=url.url,
                prompt=url.prompt,
                sub_area=url.sub_area,
                url_flag=url.url_flag,
                rag_flag=url.rag_flag,
                text_input=url.text_input,
                chat_history_flag=url.chat_history_flag,
                session_id = url.session_id)
     

def delivery_report(err, msg):
    if err is not None:
        st.error(f"Message delivery failed: {err}")
    else:
        st.success(f"Message delivered to {msg.topic()} [{msg.partition()}]")    

class Url(object):

    def __init__(self, url=None, prompt=None, sub_area=None, url_flag=None, rag_flag=None, text_input=None, chat_history_flag=None, session_id=None):
        self.url = url
        self.prompt = prompt
        self.sub_area = sub_area
        self.url_flag = url_flag
        self.rag_flag = rag_flag
        self.text_input = text_input
        self.chat_history_flag = chat_history_flag
        self.session_id = session_id


if __name__ == "__main__":

   #ctx = get_script_run_ctx()
   #session_id = ctx.id 
   session_id = add_script_run_ctx().streamlit_script_run_ctx.session_id

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
        },
        {
            "name": "chat_history_flag",
            "type": "boolean"
        },
        {
            "name": "session_id",
            "type": "string"
        }
     ]
      }
      """   
        
   commonconf = {
            'bootstrap.servers': 'xxx-yyy.us-east1.gcp.confluent.cloud:9092',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': 'someuser',
            'sasl.password': 'xxx/yyy'
        #    'schema.registry.url': 'https://xxx-yyy.us-east-2.aws.confluent.cloud'
        #    'schema.registry.basic.auth.credentials.source': 'USER_INFO',
        #    'schema.registry.basic.auth.user.info': 'someapikey:someapisecret'
           }

   producerconf = {}

   consumerconf = {
            'group.id': 'raghandler',
            'session.timeout.ms': 90000,
            'request.timeout.ms': 60000,
            'auto.offset.reset': 'latest',
            }

   totopic = "ragurldemo"
   fromtopic = "ragoutput"
    #totopic = promptresults
   schema_registry_conf = {
        "url": "https://xxx-yyy.us-east-2.aws.confluent.cloud",
        "basic.auth.user.info": "someapikey:someapisecret"
    }
   schema_registry_client = SchemaRegistryClient(schema_registry_conf)
   chaturl_avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=url_schema_str,
        to_dict=url_to_dict
    )
   string_serializer = StringSerializer('utf_8')

   producerconf.update(commonconf)
   producer_conf = producerconf
   producer = Producer(producer_conf)
   consumerconf.update(commonconf)
   consumer_conf = consumerconf
   c = Consumer(consumer_conf)
    # Subscribe to topics
   c.subscribe(topics=[fromtopic])
   st.title("Simple Chatbot")
  # Input fields
   url = st.text_input("Enter value for URL")
   useurl = st.checkbox("use url")
   userag = st.checkbox("use rag")
   chathistory = st.checkbox("chat history")
   if useurl:
      url_flag = True
   else:
      url_flag = False  
   
   if userag:
      rag_flag = True
   else:
      rag_flag = False   

   if chathistory:
      chat_history_flag = True
   else:
      chat_history_flag = False   

   text_input = "" 

   if not useurl and userag:
      text_input = st.text_input("Enter Your Input") 

   prompt = st.text_input("Enter value for Prompt")
   sub_area = st.text_input("Enter value for Suject Area")


   if st.button("Send to Kafka"):
     st.success("Producing records to topic {}. ^C to exit.".format(totopic))  
     
     try:   
      #st.success("Preparing to Produce {}".format(rag_flag))
      url = Url(url=url,
                prompt=prompt,
                sub_area=sub_area,
                url_flag=url_flag,
                rag_flag=rag_flag,
                text_input=text_input,
                chat_history_flag=chat_history_flag,
                session_id=session_id
                )
      #st.success("Preparing to Produce again..")
      producer.produce(topic=totopic,
                       key=string_serializer(str(uuid4())),
                       value=chaturl_avro_serializer(url, SerializationContext(totopic, MessageField.VALUE)),
                       on_delivery=delivery_report)  
      producer.flush()
     except Exception as e:
      st.error(f"Failed to send message: {e}")
      
     try:
        msg = ""
        while msg == "":
            st.text("Polling Message...")
            msg = c.poll(timeout=60.0)
            if msg is None:
                msg == ""
            if msg.error():
                st.error(f"Failed to send message: {e}")
                raise KafkaException(msg.error())
            else:
                st.text("Your Response as below..")
                st.text(msg.value())
                msg == ""
                #print(msg.value())
                #c.store_offsets(msg)

     except Exception as e:
        st.error(f"Failed to consume message: {e}")

     finally:
        # Close down consumer to commit final offsets.
        c.close()
    
      


