import json
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain_groq import ChatGroq
# import dotenv
# dotenv.load_dotenv()    

from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )
LLM = None

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


import time

def prompt_function(state: State):
    return {"messages": state["messages"]}

def Set_LLM(api,key):
    LLM = None
    print("setting llm to ", api)
    if api == "GROQ":
        os.environ['GROQ_API_KEY'] = key
        LLM = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0,
            max_tokens=None,
            reasoning_format="parsed",
            timeout=None,
            max_retries=2,
            # other params...
        )
    if api == "GOOGLE":
            os.environ['GOOGLE_API_KEY'] = key
            LLM = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                    # other params...
                )

    return LLM

def Agent_Function(state: State, prompttemplate="",Agent_id=""):
    print("------------------------------------------------------------")
    print(Agent_id)
    LLM = Set_LLM(LLM_STORE[Agent_id]["api"],LLM_STORE[Agent_id]["key"])
  
    if prompttemplate:
        print("Prompt template:", prompttemplate)
    t0 = time.time()
    if LLM:
        output = LLM.invoke(str(state["messages"]) + prompttemplate)
    else:
        return { "messages": ["Please Provide LLM"] }
    t1 = time.time()
    print(f"LLM response time: {t1-t0:.2f} seconds")
    return { "messages": [output.content] }


nodes_main_list = []
LLM_STORE = {}
def CreateWorkflow(json_op):
        global LLM ,LLM_STORE
        graph_builder = StateGraph(State)
        # data = json.loads(json_op)
        data  = json_op
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
            if first_node is None and node_id=='Prompt_Node':
                first_node = node_id
            if node_type=="prompt":
                nodes_main_list.append(node_id)
                prompt = metadata[node_id]['prompt']
                # prompt_function = prompt_function(prompt)
                graph_builder.add_node(node_id, prompt_function)
            if node_type=="agent":
                nodes_main_list.append(node_id)
                LLM_STORE[node_id] = {"api":None,"key":None}
                template = metadata[node_id]['promptTemplate']
                graph_builder.add_node(node_id, lambda state, template=template , node=node_id: Agent_Function(state, prompttemplate=template, Agent_id=node))

            
            if node_type == "VD":
                pass
                # graph_builder.add_node(node_id, lambda state: LLM_Function(state, prompttemplate=metadata[node_id]['promptTemplate']))

            if node_type == "memory":
                pass
                # graph_builder.add_node(node_id, lambda state: LLM_Function(state, prompttemplate=metadata[node_id]['promptTemplate']))

            # if node_type == "LLM":
                
            #     Set_LLM(api,key)
                # graph_builder.add_node(node_id, lambda state: LLM_Function(state, prompttemplate=metadata[node_id]['promptTemplate']))

            if node_id=='Prompt_Node' :
                # print(node_id,"---------------------------->")
                graph_builder.add_edge(START, first_node)
            if node_id == 'Output_Node':
                graph_builder.add_edge(last_node, END)
            if last_node is None:
                 last_node = node_id

        for edge in edges:
            source = edge['source']
            target = edge['target']
            # print(edge)
            if edge['source'][:3] == 'LLM' and (edge['target'][:5] == 'Agent' or edge['target'][:5] == 'agent'):
                node_id = target
            
                api = metadata[source]['api']
                key = metadata[source]['key']
                LLM_STORE[node_id] = {"api":api,"key":key}

           
            if (source in nodes_main_list) and (target  in nodes_main_list):
            
             
                graph_builder.add_edge(source, target)
        # print("Graph is build send to compile")
        app1 = graph_builder.compile()
        # print("Graph is compile send to invoke")
        user_input= metadata['Prompt_Node']['prompt']
        # print(user_input)
        # return app1,user_input
        # print(LLM_STORE)
        return app1.invoke({"messages": [user_input]})


# app1, user_input = CreateWorkflow(json_op)
# sol = app1.invoke({"messages": [user_input]})
# print(sol["messages"][-1].content)

# # After compiling the graph (after app1 = graph_builder.compile()), add this code to display the graph using matplotlib:
# import matplotlib.pyplot as plt
# import io

# try:
#     # Get PNG bytes from the graph (assuming draw_mermaid_png returns bytes)
#     png_bytes = app1.get_graph().draw_mermaid_png()
#     image_stream = io.BytesIO(png_bytes)
#     img = plt.imread(image_stream, format='png')
#     plt.imshow(img)
#     plt.axis('off')
#     plt.show()
# except Exception as e:
#     print(e)
