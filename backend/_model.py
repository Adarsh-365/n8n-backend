import json
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain_groq import ChatGroq

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

# # Set proxy for internet access (adjust if your proxy is different)

# json_op = """{"flow": {"nodes": [{"id": "Prompt_Node", "type": "prompt", "position": {"x": 0, "y": 0}, 
# "data": {"label": "Prompt"}, "measured": {"width": 74, "height": 46}, "selected": false},
#  {"id": "Agent_Node", "type": "agent", "position": {"x": 200, "y": 0}, 
#  "data": {"label": "Agent"}, "measured": {"width": 97, "height": 46}}, 
#  {"id": "Output_Node", "type": "output", "position": {"x": 400, "y": 0}, 
#  "data": {"label": "Output"}, "measured": {"width": 150, "height": 61}, 
#  "selected": false}], "edges": []},"metadata": {"Prompt_Node": {"prompt": "what is 1+1"}, "Agent_Node": {"option": "option1"}}}"""

# Received data: {'flow': {'nodes': [{'id': 'Prompt', 'type': 'prompt', 'position': {'x': 0, 'y': 0},
#                                      'data': {'label': 'Prompt'}, 'measured': {'width': 74, 'height': 46}},
#                                        {'id': 'Processing', 'type': 'processing', 'position': {'x': 200, 'y': 0},
#                                          'data': {'label': 'Processing'}, 'measured': {'width': 97, 'height': 46}},
#                                            {'id': 'Output', 'type': 'output', 'position': {'x': 400, 'y': 0}, 'data':
#                                              {'label': 'Output'}, 'measured': {'width': 150, 'height': 61}}], 
#                                              'edges': [{'source': 'Prompt', 'target': 'Processing', 'id': 
#                                                         'xy-edge__Prompt-Processing'}, {'source': 'Processing',
# 'target': 'Output', 'id': 'xy-edge__Processing-Output'}]}, 'prompt': '', 'option': 'option1'}



# json_op = """{
#   "flow": {
#     "nodes": [
#       {
#         "id": "Prompt_Node",
#         "type": "prompt",
#         "position": {"x": 0, "y": 0},
#         "data": {"label": "Prompt"},
#         "measured": {"width": 74, "height": 46},
#         "selected": false
#       },
#       {
#         "id": "Agent_Node",
#         "type": "agent",
#         "position": {"x": 200, "y": 0},
#         "data": {"label": "Agent"},
#         "measured": {"width": 97, "height": 46}
#       },
#       {
#         "id": "Output_Node",
#         "type": "output",
#         "position": {"x": 400, "y": 0},
#         "data": {"label": "Output"},
#         "measured": {"width": 150, "height": 61},
#         "selected": false
#       }
#     ],
#     "edges": [
#       {
#         "source": "Prompt_Node",
#         "target": "Agent_Node",
#         "id": "xy-edge__Prompt-Node-Agent-Node"
#       }
     
    
#     ]
#   },
#   "metadata": {
#     "Prompt_Node": {"prompt": "what is 1+1"},
#     "Agent_Node": {"option": "option1"}
#   }
# }
# """

import time

def prompt_function(state: State):
    return {"messages": state["messages"]}

def LLM_Function(state: State, prompttemplate=""):
    print("Calling LLM...")
    if prompttemplate:
        print("Prompt template:", prompttemplate)
    t0 = time.time()
    output = llm.invoke(str(state["messages"]) + prompttemplate)
    t1 = time.time()
    print(f"LLM response time: {t1-t0:.2f} seconds")
    return { "messages": [output.content] }

def CreateWorkflow(json_op):
        graph_builder = StateGraph(State)
        data = json_op
        flow = data['flow']

        # print(flow)
        metadata = data["metadata"]
        # print(metadata)

        nodes = flow['nodes']
        edges = flow['edges']

        first_node = None
        last_node = None
        for node in nodes:
            node_id = node['id']
            node_type = node['type']
            
            # print(node_id, node_type)
            if first_node is None:
                first_node = node_id
            if node_type=="prompt":
                prompt = metadata[node_id]['prompt']
                # prompt_function = prompt_function(prompt)
                graph_builder.add_node(node_id, prompt_function)
            if node_type=="agent":
                template = metadata[node_id]['promptTemplate']
                graph_builder.add_node(node_id, lambda state, template=template: LLM_Function(state, prompttemplate=template))

          
            if first_node is not None:
                graph_builder.add_edge(START, first_node)
            if node_id == 'Output_Node':
                graph_builder.add_edge(last_node, END)
            if last_node is None:
                 last_node = node_id

        for edge in edges:
            source = edge['source']
            target = edge['target']
            if target=='Output':
                continue

            graph_builder.add_edge(source, target)
        # print("Graph is build send to compile")
        app1 = graph_builder.compile()
        # print("Graph is compile send to invoke")
        user_input= metadata['Prompt_Node']['prompt']
        # print(user_input)
        return app1.invoke({"messages": [user_input]})


# sol = CreateWorkflow()
# print(sol["messages"][-1].content)