from fastapi import FastAPI
import redis
import os
from llm_client import call_llm
import time
app = FastAPI()


host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=host,
    port=port,
    decode_responses=True
)

@app.get("/")
def first_get():
    return {  "message": "Hello from Docker!"}

@app.get("/redis-health")
def redis_health():
    state= redis_client.ping()
    return {"redis_connected": state}


@app.get("/cache-test")
def cache_test():
    redis_client.set("message","hello from fastapi")
    output =  redis_client.get("message")
    return {"cached_message" : output}





@app.get("/cache-demo")
def cache_demo():
    #redis_client.set("question", "some answer", ex=500)
    output = redis_client.get("question")
    if output: 
        final = {"source":"cache","answer":output}
    else:
        redis_client.set("question","docker is doing some shit",ex=60)
        output_generated = redis_client.get("question")
        final = {"source":"generated","answer":output_generated}
    return final


@app.get("/ask")
def ask(question : str):
    start = time.perf_counter()
    dynamic_key = f"{question}:redis_key"
    checking = redis_client.get(dynamic_key)
    if checking is not None:
        output = {"source" : "cache","answer" : checking}   
        end = time.perf_counter()
        elapsed_time_ms = round((end - start) * 1000, 2)
        output_with_time = {"source" : "cache","answer" : checking, "elapsed_time": elapsed_time_ms}
    else: 
        answer = call_llm(question)
        redis_client.set(dynamic_key , answer ,ex=60)
        output = {"source" : "generated","answer" : answer }
        end = time.perf_counter()
        elapsed_time_ms = round((end - start) * 1000, 2)
        output_with_time = {"source" : "generated","answer" : answer, "elapsed_time": elapsed_time_ms}
    return output_with_time



@app.get("/debug-test")
def debug_test():
    result = 10 / 4
    return {"result": result}