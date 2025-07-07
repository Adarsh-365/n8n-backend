import time
from langchain_google_genai import ChatGoogleGenerativeAI
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyCGDMPEYAcVOb6jSE_auD_XWYPTwMjzrGI"
os.environ["HTTP_PROXY"] = "http://proxy-dmz.intel.com:912"
os.environ["HTTPS_PROXY"] = "http://proxy-dmz.intel.com:912"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

t0 = time.time()
response = llm.invoke([{"role": "user", "content": "what is 1+1"}])
t1 = time.time()
print(f"LLM response time: {t1-t0:.2f} seconds")
print(response)