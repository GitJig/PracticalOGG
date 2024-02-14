'''
Based on example in https://dash.plotly.com/cytoscape/styling
'''
from dash import Dash, dcc, html, Input, Output, ctx, callback,State
import dash_cytoscape as cyto
import json
import numpy as np
import base64
import io
import os

ifilename = input('Enter a file name: ')
print (ifilename)

# def parse_report_file(self, ifilename):
#     """ Checks if input report file is of type json or xml """
#     parsed_report_file = None
#     try:
#         parsed_report_file = self._parse_json_file(ifilename)
#         self.is_json_report_file = True
#     except Exception as e:
#         print("error parsing file " + self.ifilename)
#         print("ensure file is valid OCI GG JSON file")
#         exit(1)

#     return parsed_report_file

# pf = parse_report_file()
# pf.parse_report_file(ifilename)

cyto.load_extra_layouts()
app = Dash(__name__)
server = app.server

    
with open(ifilename) as jsonFile:
     data = json.load(jsonFile)

#Number of Extract/trail/replicat pairs
numtrees=len(data["data"]["items"])
Nodenum=0
ProcessType = ''
nonterminal_nodeslist = ["Deployment"]
nonterminal_processlist = ["Deployment"]
terminal_nodesiconlist = ["\ggicon.png"]
edgelist =[]
edgesourcelist =[]
edgetargetlist =[]

proccount=0

while Nodenum < numtrees: 
    
    # Populate Variables Extract, TrailName and Replicats for each pair

    Extract = data["data"]["items"][Nodenum]["producer"]
    TrailName = data["data"]["items"][Nodenum]["trail-file-id"]
    Replicats = data["data"]["items"][Nodenum]["consumers"]
    Nodenum += 1  
   # Populate non-terminal Nodes for Extract, TrailName and Replicats for each pair
    
    if Extract is None :
        Extract = "NoExtract"
        ProcessType="Extract"
        nonterminal_nodeslist.append(Extract)
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append('\MissingExtract.png')
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
    else: 
        nonterminal_nodeslist.append(Extract)
        ProcessType="Extract" 
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append("\Extract.png")
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
        
    ProcessType="Trail"
    
    nonterminal_nodeslist.append((TrailName))
    nonterminal_processlist.append(ProcessType)
    terminal_nodesiconlist.append("\Trail.png")
    edgesourcelist.append(Extract)
    edgetargetlist.append(TrailName)
    
    if Replicats is None :
        Replicats = "NoReplicat"
        # ProcessType="Replicat"
        # nonterminal_nodeslist.append(Replicats) 
        # nonterminal_processlist.append(ProcessType)
        # terminal_nodesiconlist.append('\MissingReplicat.png')        
    else:

        # Replicats can be > 1, so loop thru the number of replicats

        NumRep=0
        
        while NumRep < len(Replicats):
            ProcessType="Replicat"
            nonterminal_nodeslist.append(Replicats[NumRep])          
            nonterminal_processlist.append(ProcessType)
            terminal_nodesiconlist.append("\Replicat.png")
            edgesourcelist.append(TrailName)
            edgetargetlist.append(Replicats[NumRep])
            NumRep += 1
# zip will merge 2 diff lists i.e. processlist and nodelist

# nonterminal_nodes = [
#    {
#        'classes': 'nonterminal',
#        'data': {
#            'id': id, 
#            'label': processtype,
#            'process':processtype 
#            }
#     }
#     for id, processtype in zip(nonterminal_processlist,nonterminal_nodeslist)
#    ]
   
edges = [
    {
         'data': {
            'source': source, 
            'target': target
            }
    }
     for source, target in zip(edgesourcelist,edgetargetlist)
    ]

# Creating elements

terminal_nodes = [
    {
        'classes': 'terminal',
        'data': {
            'id': name,
            'label': name,
            'url': "static"+url
        }
    }
    for name, url in zip(nonterminal_nodeslist,terminal_nodesiconlist)
]

proccount=0

# print("terminal_nodes")
# print(terminal_nodes)
# print("nonterminal_nodes")
# print(nonterminal_nodes)
print("edges")
print(edges)
# Creating styles
stylesheetset = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(process)',
            'label': 'data(process)',
        }
    },
    {
        'selector': '.terminal',
        'style': {
            'width': 1200,
            'height': 800,
            'label': 'data(name)',
            'background-fit': 'cover',
            'content': 'data(label)',
            'background-image': 'data(url)',
            'font-size': '300px'
        }
    },
    {
        'selector': '.nonterminal',
        'style': {
            'shape': 'rectangle',
    
        }
    }
]

styles = {
    'output': {
        'overflow-y': 'scroll',
        'overflow-wrap': 'break-word',
        'height': 'calc(100% - 5px)',
        'border': 'thin black solid'
    },
    'tab': {'height': 'calc(18vh - 110px)'}
}

app.layout = html.Div([
    html.Div('Oracle GoldenGate Topology viewer v0.1'),
    html.Div(className='eight columns', children=[
        cyto.Cytoscape( 
            id='cytoscape-image-export',
            #elements=terminal_nodes + nonterminal_nodes + edges,
            elements=terminal_nodes +edges,
            layout={'name': 'breadthfirst', 'roots': ['Deployment']},
            style={
                    'width': '100%', 
                    'height': '1000px',
                    'float': 'left'
                   },
            stylesheet=stylesheetset
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs-image-export', children=[
            dcc.Tab(label='Save Chart', value='jpg') 
        ]),
        html.Div(style=styles['tab'], children=[
            html.Div(
                id='image-text',
                children='Topology diagram',
                style=styles['output']
            )
        ]),
        html.Div('Download OGG Topology Diagram:'),
        html.Button("as jpg", id="btn-get-jpg"),
    ])
])


@callback(
    Output('image-text', 'children'),
    Input('cytoscape-image-export', 'imageData'),
    )
def put_image_string(data):
    return data


@callback(
    Output("cytoscape-image-export", "generateImage"),
    [
        Input('tabs-image-export', 'value'),
        Input("btn-get-jpg", "n_clicks")
    ])
def get_image(tab, get_jpg_clicks):

    # File type to output of 'svg, 'png', 'jpg', or 'jpeg' (alias of 'jpg')
    ftype = "jpg"

    # 'store': Stores the image data in 'imageData' !only jpg/png are supported
    # 'download'`: Downloads the image as a file with all data handling
    # 'both'`: Stores image data and downloads image as file.
    action = 'store'

    if ctx.triggered:
        if ctx.triggered_id != "tabs-image-export":
            action = "both"
            ftype = ctx.triggered_id.split("-")[-1]

    return {
        'type': ftype,
        'action': action
        }
    
if __name__ == '__main__':
   app.run(debug=True,port=7079)