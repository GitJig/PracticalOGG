'''
Based on example in https://dash.plotly.com/cytoscape/styling
'''
from dash import Dash, dcc, html, Input, Output, ctx, callback,State
import dash_cytoscape as cyto
import json
import numpy as np
import io
import os

ifilename = input('Enter a file name: ')
#print (ifilename)
firstDeploymentName = "OCIGGOracleDeployment"
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
#server = app.server

with open(ifilename) as jsonFile:
     data = json.load(jsonFile)

#Number of Extract/trail/replicat pairs
numtrees=len(data["data"]["items"])
Nodenum=0
ProcessType = ''
nonterminal_nodeslist = ["Deployment"]
nonterminal_processlist = ["Deployment"]
terminal_nodesiconlist = ["\ggicon.png"]
edgesourcelist =[]
edgetargetlist =[]
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
    
    if Extract is None :
        Extract = "NoExtract OR  Remote Trail"
        ProcessType="Extract"
        nonterminal_nodeslist.append(Extract)
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append('\MissingExtract.png')
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
        infolist.append(Extract)
         
    else: 
        nonterminal_nodeslist.append(Extract)
        ProcessType="Extract" 
        nonterminal_processlist.append(ProcessType)
        terminal_nodesiconlist.append("\Extract.png")
        edgesourcelist.append("Deployment")
        edgetargetlist.append(Extract)
        infolist.append("Extract is " + Extract)
        
    ProcessType="Trail"
    
    nonterminal_nodeslist.append((TrailName))
    nonterminal_processlist.append(ProcessType)
    terminal_nodesiconlist.append("\Trail.png")
    edgesourcelist.append(Extract)
    edgetargetlist.append(TrailName)
    infolist.append(TrailName + " has " + str(TrailNum) + " trail files \nTotal Size is " + str(TrailSize)+"KB" )
    
    if Replicats is None :
        Replicats = "NoReplicat"
   
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
            infolist.append("Replicat is " + Replicats[NumRep])
            NumRep += 1

# zip will merge 2 diff lists i.e. processlist and nodelist

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

colors = {
    'background': '#0D0D0D',
    'text': '#A6A6A6'
}
# Creating styles
stylesheetset = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(process)',
            'label': 'data(process)',
            'shape': 'oval',
            'color':'#A6A6A6',
            'font-family': "Arial"
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
            'shape':'oval',
            'color':'#A6A6A6',
            'font-family': "Arial"
        }
    },
    {
        'selector': '.nonterminal',
        'style': {
            'shape': 'square',
    
        }
    },
      {  'selector': 'edge',
                'style': {
                     'line-color': '#A6A6A6',
                     
                }
      },
      {
    'selector': 'label',             # as if selecting 'node' :/
    'style': {
        'content': 'data(label)',    # not to loose label content
        'color': '#A6A6A6',
        'background-color': '#A6A6A6'   # applies to node which will remain pink if selected :/
    }
    },
      
]
tab_height = '15vh'
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#4A4F59',
    'color': '#A6A6A6',
    'padding': '16px',
    'width':'550%',
    'line-width': tab_height
}


styles = {
    'output': {
        'overflow-y': 'scroll',
        'overflow-wrap': 'break-word',
        'height': 'calc(30% - 5px)',
        'border': 'black solid',
        'float':'bottom',
        'font-family': "Arial"
    },
    'tab': {'height': 'calc(15vh - 9px)'},
           'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'auto'
    },
        'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'auto',
        'font-family': "Arial",
        'font-size': '20px'
    }
}

app.layout = html.Div([
    html.H1(children='OCI GoldenGate Topology viewer v0.2', style={
        'textAlign': 'center','font-family':'Arial','backgroundColor': colors['background'],'color': colors['text'],'padding': 0}),
    html.Div(className='nine columns', children=[
        cyto.Cytoscape( 
            id='cytoscape-image-export',
            #elements=terminal_nodes + nonterminal_nodes + edges,
            elements=terminal_nodes +edges,
            layout={'name': 'breadthfirst', 'roots': ['Deployment'],'animate': True},
            style={
                    'width': '100%', 
                    'height': '450px',
                    'float': 'left',
                    'backgroundColor': colors['background'],
                    'font-family': "Arial",
                    'color': colors['text'],
                    'padding': 0
                   },
            stylesheet=stylesheetset
        )
    ]),
    html.Pre(id='cytoscape-tapNodeData-json', style=styles['pre']),
    html.Div(className='one column', children=[
        dcc.Tabs(id='tabs-image-export', children=[
            dcc.Tab(label='', value='jpg',style=tab_selected_style)
        ]),
        html.Label(children='Download Topology Diagram:',style={
        'textAlign': 'center','font-family':'Arial','width':'250%','backgroundColor': colors['background'],'color': colors['text']}),
        html.Button("Save as jpg", id="btn-get-jpg"),
    ])
])

@callback(Output('cytoscape-tapNodeData-json', 'children'),Input('cytoscape-image-export', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        #print(infolist)
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