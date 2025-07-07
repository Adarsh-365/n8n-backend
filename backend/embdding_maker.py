import google.generativeai as genai
import os

# Assuming your API key is stored in an environment variable
api_key = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

text = "This is an example sentence."
embeddings = genai.embed_content(
    model="models/embedding-001",
    content=text
)

print(embeddings)