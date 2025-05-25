import dash
from dash import html, dash_table, dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

### output functions ###

def showtable(idname):    
    return dash_table.DataTable(id=idname,
                                page_action='none',
                                fixed_rows={'headers': True},
                                style_table={'height': '300px', 'overflowY': 'auto'})



# def showtable(idname, dataframe, max_rows=100):    
#     return dash_table.DataTable(id=idname,
#                                 columns=[{"name": i, "id": i} for i in dataframe.columns],
#                                 data=dataframe[:max_rows].to_dict('records'),
#                                 page_action='none',
#                                 fixed_rows={'headers': True},
#                                 style_table={'height': '300px', 'overflowY': 'auto'})
                                # , 'width':'1000px',},    )

def showtext(idname, size, text):
    if size=='H1':
        return html.H1(text,id=idname)
    elif size=='H2':
        return html.H2(text,id=idname)
    elif size=='H3':
        return html.H3(text,id=idname)
    elif size=='H4':
        return html.H4(text,id=idname)
    elif size=='H5':
        return html.H5(text,id=idname)
    elif size=='H6':
        return html.H6(text,id=idname)

def showmk(idname, text):
    return dcc.Markdown(text, id=idname)


def showgraph(idname):
    return dcc.Graph(id=idname) 





### input functions ###        
def input_text(idname):
    return dcc.Input(id=idname, 
                     placeholder='Enter a value...',
                     type='text',
                     value='',
                    )


def input_textarea(idname):
    return dcc.Textarea(id=idname,
                        placeholder='Enter a value...',
                        value='This is a TextArea component',
                       )

def button(idname, text):
    return html.Button(text, 
                       id=idname, 
                       n_clicks=0,
                      )

    

def dropdown_menu(idname, menu):
    return dcc.Dropdown(id=idname,
                        options=[{"label": name, "value": name} for name in menu],
                        value=menu[1],
                        placeholder='select value',
                        )


def checklist_menu(idname, menu):
    return dcc.Checklist(id=idname, 
                         options=[{"label": name, "value": name} for name in menu],
                         value=menu[0],
                         )

    

    

