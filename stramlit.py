import streamlit as st
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
import os
from uuid import uuid4
import threading 
import time
# Kafka configuration (update with your actual config)

def url_to_dict(url, ctx):
    return dict(url=url.url,
                prompt=url.prompt,
                sub_area=url.sub_area,
                url_flag=url.url_flag,
                rag_flag=url.rag_flag,
                text_input=url.text_input)
     

def delivery_report(err, msg):
    if err is not None:
        st.error(f"Message delivery failed: {err}")
    else:
        st.success(f"Message delivered to {msg.topic()} [{msg.partition()}]")    

class Url(object):

    def __init__(self, url=None, prompt=None, sub_area=None, url_flag=None, rag_flag=None, text_input=None):
        self.url = url
        self.prompt = prompt
        self.sub_area = sub_area
        self.url_flag = url_flag
        self.rag_flag = rag_flag
        self.text_input = text_input



class KafkaProducer(threading.Thread):
    def __init__(self, producer, url, value_serializer, key_serializer, totopic):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.producer = producer
        self.value_serializer = value_serializer
        self.key_serializer = key_serializer
        self.totopic = totopic
        self.url = url

    def stop(self):
        self.stop_event.set()
        
    def run(self):
        
        while not self.stop_event.is_set():
            try:
               self.producer.produce(topic=totopic,
                       key=self.key_serializer(str(uuid4())),
                       value=self.value_serializer(url, SerializationContext(self.totopic, MessageField.VALUE)),
                       on_delivery=delivery_report)
               self.producer.flush()  
            except Exception as e:
               print("An error occured:", e) 
               #st.error(f"Failed to send message: {e}")    

class KafkaConsumer(threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.consumer = consumer
        self.text_output = "no response yet"

    def stop(self):
        self.stop_event.set()

    def run(self):
        # Subscribe to topic
        self.consumer.subscribe([self.topic])
        try:
           while not self.stop_event.is_set():
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                   continue

                if msg.error():
                    #st.error(f"Failed to send message: {e}")
                    raise KafkaException(msg.error())
                else:
                    self.text_output = str(msg.value())
                    #st.text(msg.value())

        except Exception as e:
           print("An error occured:", e) 
           #st.error(f"Failed to consume message: {e}")
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

if __name__ == "__main__":  
    
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
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'latest',
            'enable.auto.offset.store': False
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
   if useurl:
      url_flag = True
   else:
      url_flag = False  
   
   if userag:
      rag_flag = True
   else:
      rag_flag = False   

   text_input = "" 

   if not useurl and userag:
      text_input = st.text_input("Enter Your Input") 

   prompt = st.text_input("Enter value for Prompt")
   sub_area = st.text_input("Enter value for Suject Area")

   url = Url(url=url,
                prompt=prompt,
                sub_area=sub_area,
                url_flag=url_flag,
                rag_flag=rag_flag,
                text_input=text_input
                )
   if st.button("Send to Kafka"):
      st.success("Producing records to topic {}. ^C to exit.".format(totopic))
      kproducer = KafkaProducer(producer, url, chaturl_avro_serializer, string_serializer, totopic)
      kproducer.daemon = True  # Producer thread will terminate when main thread terminates
      kproducer.start()
    # Create and start the consumer thread
   consumer = KafkaConsumer(c)
   consumer.daemon = True  # Consumer thread will terminate when main thread terminates
   consumer.start()

   try:
        # Keep the main thread running (or do other work here)
        while True:
            time.sleep(1)
            st.text(consumer.text_output)
   except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C)
        kproducer.stop()
        consumer.stop()
        kproducer.join()
        consumer.join()
      


