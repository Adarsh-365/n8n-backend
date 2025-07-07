from    django.http import HttpResponse
from    django.shortcuts import render
from django.http import JsonResponse 
import json
from django.views.decorators.csrf import csrf_exempt
from .json_langgraph import llm_response
from ._model import CreateWorkflow

def home(request):
    return render(request,'index.html')

@csrf_exempt
def index(request):
    # Add CORS headers
 
    if request.method == "POST":
        print("Received POST request")
        data = json.loads(request.body)
        print("Received data:", data)
        # user_input = data['prompt']
        # response = llm_response(user_input)
        op = CreateWorkflow(json_op = data)
        # print(response)
        response1 = op["messages"][-1].content
        # print(response)
        return JsonResponse({"Output":response1})
       

    """
    A simple view that returns a welcome message.
    """
    response = JsonResponse({
        "Output": "Welcome to the backend of N8N Clone!"
    })

    return response
