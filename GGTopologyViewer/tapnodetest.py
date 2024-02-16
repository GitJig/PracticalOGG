'''
Based on example in https://dash.plotly.com/cytoscape/styling
'''
from dash import Dash, dcc, html, Input, Output, ctx, callback, State
import dash_cytoscape as cyto
import json
import numpy as np
import base64
import io
import os
ifilename = input('Enter a file name: ')
print(ifilename)
firstDeploymentName = "JDOracleGGTest"
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

with open(ifilename) as jsonFile:
    data = json.load(jsonFile)

# Number of Extract/trail/replicat pairs
numtrees = len(data["data"]["items"])
Nodenum = 0
ProcessType = ''
nonterminal_nodeslist = ["Deployment"]
nonterminal_processlist = ["Deployment"]
terminal_nodesiconlist = ["\ggicon.png"]
edgesourcelist = []
edgetargetlist = []
infolist = ["First Deployment is " + firstDeploymentName]
while Nodenum < numtrees:
    # Populate Variables Extract, TrailName and Replicats for each pair
    Extract = data["data"]["items"][Nodenum]["producer"]
    TrailName = data["data"]["items"][Nodenum]["trail-file-id"]
    TrailNum = data["data"]["items"][Nodenum]["number-of-sequences"]
    TrailSize = round(data["data"]["items"][Nodenum]["size-in-bytes"]/1024,2)
    Replicats = data["data"]["items"][Nodenum]["consumers"]  
    Nodenum += 1
    
   # Populate non-terminal Nodes for Extract, TrailName and Replicats for each pair

    if Extract is None:
        Extract = "NoExtract"
        ProcessType = "Extract"
        nonterminal_nodeslist.append(Extract)
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append('\MissingExtract.png')
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
        infolist.append("NoExtract")
        
    else:
        nonterminal_nodeslist.append(Extract)
        ProcessType = "Extract"
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append("\Extract.png")
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
        infolist.append("Extract is " + Extract)

    ProcessType = "Trail"

    nonterminal_nodeslist.append((TrailName))
    nonterminal_processlist.append(ProcessType)
    terminal_nodesiconlist.append("\Trail.png")
    edgesourcelist.append(Extract)
    edgetargetlist.append(TrailName)
    infolist.append(TrailName + " has " + str(TrailNum) + " trail files \nTotal Size is " + str(TrailSize)+"KB" )
    
    if Replicats is None:
        Replicats = "NoReplicat"

    else:

        # Replicats can be > 1, so loop thru the number of replicats

        NumRep = 0

        while NumRep < len(Replicats):
            ProcessType = "Replicat"
            nonterminal_nodeslist.append(Replicats[NumRep])
            nonterminal_processlist.append(ProcessType)
            terminal_nodesiconlist.append("\Replicat.png")
            edgesourcelist.append(TrailName)
            edgetargetlist.append(Replicats[NumRep])
            infolist.append("Replicat is " + Replicats[NumRep])
            NumRep += 1
            

# Creating elements

edges = [
    {
        'data': {
            'source': source,
            'target': target
        }
    }
    for source, target in zip(edgesourcelist, edgetargetlist)
]

print (edges)

sizelist = []
nodesize = 5
while nodesize < 400:
    sizelist.append(nodesize)
    nodesize +=10
    
terminal_nodes = [
    {
        'classes': 'terminal',
        'data': {
            'id': name,
            'label': name,
            'url': "static"+url,
            'size': nodesize
        }
    }
    for name, url,nodesize  in zip(nonterminal_nodeslist, terminal_nodesiconlist,sizelist)
]

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
            'font-size': '200px',
            'shape': 'oval',
            'font-family': "Arial"
        }
    },
    {
        'selector': '.nonterminal',
        'style': {
            'shape': 'square',

        }
    }
]

styles = {
        'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'auto'
    },
        'standardstyle': {
        'textAlign': 'center',
        'font-family': 'Arial'
    }
}
print (terminal_nodes)
app.layout = html.Div([
    html.H1(children='OCI GoldenGate Topology viewer v0.1', style=styles['standardstyle']),
    html.Div(className='nine columns', children=[
        cyto.Cytoscape(
            id='cytoscape-image-export',
            # elements=terminal_nodes + nonterminal_nodes + edges,
            elements=terminal_nodes + edges,
            layout={'name': 'breadthfirst', 'roots': ['Deployment'], 'animate': True},
            style={
                'width': '100%',
                'height': '450px',
                'float': 'left',
                'backgroundColor': '#82E0AA',
                'font-family': "Arial"
            },
            stylesheet=stylesheetset
        )
    ]),
    html.Pre(id='cytoscape-tapNodeData-json', style=styles['pre']),
    html.Div(className='one column', children=[
        dcc.Tabs(id='tabs-image-export', children=[
            dcc.Tab(label='', value='jpg')
        ]),
    html.Div(children='Download OGG Topology Diagram:', style=styles['standardstyle']),
    html.Button("Save as jpg", id="btn-get-jpg", style=styles['standardstyle']),
    ]),

])

@callback(Output('cytoscape-tapNodeData-json', 'children'),Input('cytoscape-image-export', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        print(infolist)
        filter_object = filter(lambda a: data['label'] in a, infolist)
        for attr in filter_object:
            filterattr = attr
        return (filterattr)
        
@callback(
    Output("cytoscape-image-export", "generateImage"),
    [
        Input('tabs-image-export', 'value'),
        Input("btn-get-jpg", "n_clicks")
    ])
def get_image(tab, get_jpg_clicks):

    # File type to output of 'jpg', or 'jpeg' (alias of 'jpg')
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
    app.run(debug=True, port=7079)