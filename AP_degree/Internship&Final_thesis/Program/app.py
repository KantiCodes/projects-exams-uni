import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
import dash_daq as daq
import DataHandlingLibrary.ERPHandling as erp_handler
from DataHandlingLibrary import DataHandlingMethods as sensor_handler
from datetime import datetime, timedelta
import random
from ModelLayer.MachineOne import MachineOne
from collections import deque
import logging
from logging.handlers import RotatingFileHandler
import dash_auth
import pytz

# Initialization of deques used to store values for diplays
x_deque = deque(maxlen=600)
y_deque = deque(maxlen=600)
y2_deque = deque(maxlen=600)
y3_deque = deque(maxlen=600)
#std_bottom_deque = deque(maxlen=1500)
#std_top_deque = deque(maxlen=1500)
machine_one = MachineOne(900)

app = dash.Dash(__name__)
# auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server
# OUTER WHOLE container DIV
app.layout = html.Div(
    id='container',
    children=[
        dcc.Interval(id='live_data_update', interval=8 * 1000, n_intervals=5),
        dcc.Interval(id='live_data_update2', interval=16 * 1000, n_intervals=5),

        # container box 1
        html.Div(children=[
            # container box 1 row 1
            html.Div(children=[], className='whitespace'),
            # containerbox 1 row 2
            html.Div(children=[
                # laddermachine name
                html.Div(children=[
                    html.H1(id='active_resource'),
                ], className='cb1-2-1'),

                # Date
                html.Div(children=[
                    html.H1(id='date_day_month'),
                ], className='cb1-2-2'),

                # Plan start
                html.Div(children=[
                    html.H1(id='planned_start_id'),
                ], className='cb1-2-3'),

                # Plan stop
                html.Div(children=[
                    html.H1(id='planned_stop_id'),
                ], className='cb1-2-4'),
            ], className='cb1-2'),
            # containerbox 1 row 3
            html.Div(children=[

                # Production number
                html.Div(children=[
                    html.H1(id='active_job_id'),
                ], className='cb1-3-1'),

                # Actual start
                html.Div(children=[
                    html.H1(id='actual_start_id'),
                ], className='cb1-3-2'),

                # Predicted stop
                html.Div(children=[
                    html.H1(id='actual_stop_id'),
                ], className='cb1-3-3'),

            ], className='cb1-3'),
            # containerbox 1 row 4
            html.Div(children=[

                # Name of product
                html.Div(children=[
                    html.H1(id='active_product_name'),
                ], className='cb1-4-1'),

            ], className='cb1-4'),

        ], className='contbox'),

        # container box 2 for graphs
        html.Div(children=[

            # containterbox for gauge
            html.Div(children=[

                # gauge outer box
                html.Div(children=[
                    daq.Gauge(
                        color={"gradient": False, "ranges": {"red": [0, 32], "yellow": [32, 64], "green": [64, 96]}},
                        id='gauge',
                        # label='Machine One Pace in Last 15 minutes',
                        min=0,
                        max=96,
                        value=4,
                        size=380,

                    ),
                    html.Div(children=[html.H3(id='gaugeCV')], className='gaugeCV'),
                ], className='gaugeContainer'),

            ], className='gauge'),

            # containerbox for graph
            html.Div(children=[

                # graph outer box
                html.Div(children=[

                    dcc.Graph(id='live_graph', style={'height': "100%", 'width': "100%", 'margin': 0}
                              ),
                ], className='graphContainer'),

            ], className='graph'),

        ], className='contboxGraphs'),

        # container box 3
        html.Div(children=[

            # container box 3 row 1
            html.Div(children=[

                # Planned output
                html.Div(children=[
                    html.H1(id='planned_output'),
                ], className='cb3-1-1'),

                # Time since last error
                html.Div(children=[
                    html.H1(id='time_since_last_error'),
                ], className='cb3-1-2'),

                # fail type
                html.Div(children=[
                    html.H1(id='fail_type'),
                ], className='cb3-1-3'),

            ], className='cb3-1'),

            # container box 3 row 2
            html.Div(children=[

                # Actual output
                html.Div(children=[
                    html.H1(id='actual_output'),
                ], className='cb3-2-1'),

                # Last error
                html.Div(children=[
                    html.H1(id='downtime_past_hour'),
                ], className='cb3-2-2'),

            ], className='cb3-2'),

            # container box 3 row 3 whitespace
            html.Div(children=[], className='whitespace'),

        ], className='contbox')

    ])


@app.callback(
    [
        Output('active_product_name', 'children'),
        Output('active_job_id', 'children'),
        Output('active_resource', 'children'),
        Output('planned_stop_id', 'children'),
        Output('planned_start_id', 'children'),
        Output('actual_start_id', 'children'),
        Output('actual_stop_id', 'children'),
        Output('date_day_month', 'children'),
        Output('actual_output', 'children'),

    ],

    [
        Input('live_data_update2', 'n_intervals'),
    ])
# Method for updating general information about the job
def update_general_info(n):
    erp,cr = erp_handler.getERPDataForThePeroid(60*60*24*1)
    if len(erp) > 0:
        
        erp_data = erp_handler.get_latest_product_data('laddermachine1', erp)
        name = erp_handler.get_name(erp_data)
        job_id = erp_handler.get_jobid(erp_data)
        planned_start = datetime.strptime(erp_handler.get_planned_start_time(erp_data), "%Y-%m-%dT%H:%M:%S")
        planned_stop = datetime.strptime(erp_handler.get_planned_stop_time(erp_data), "%Y-%m-%dT%H:%M:%S")
        actual_start = datetime.strptime(erp_handler.get_actual_start_time(erp_data), "%Y-%m-%dT%H:%M:%S")
        actual_end = datetime.strptime(erp_handler.get_predicted_stop_time(erp_data), "%Y-%m-%dT%H:%M:%S")
        # print(actual_end)
        resource = 'Stigemaskine 1 /\n1405'
        todays_date = sensor_handler.denmarkDateNow()
        todays_day = todays_date.day
        todays_month = todays_date.strftime("%B")
        display_date = (str(todays_day) + '.' + str(todays_month))
        current_output = machine_one.output_cj(erp)
    else:
        name = "---"
        job_id = "---"
        planned_start = datetime(2015,1,1,1,1,1)
        planned_stop = datetime(2015,1,1,1,1,1)
        actual_start = datetime(2015,1,1,1,1,1)
        actual_end = datetime(2015,1,1,1,1,1)
        resource = 'Stigemaskine 1 /\n1405'
        todays_date = sensor_handler.denmarkDateNow()
        todays_day = todays_date.day
        todays_month = todays_date.strftime("%B")
        display_date = (str(todays_day) + '.' + str(todays_month))
        current_output = '---'
        

    return name, 'JOBID: ' + str(job_id), resource, (
                'Planlagt stop: ' + str(planned_stop.time()) + " (" + str(planned_stop.day) + "." + str(
            planned_stop.month) + ")"), (
                       'Planlagt start: ' + str(planned_start.time()) + " (" + str(planned_start.day) + "." + str(
                   planned_start.month) + ")"), \
           ('Faktisk start: ' + str(actual_start.time()) + " (" + str(actual_start.day) + "." + str(
               actual_start.month) + ")"), (
                       'Forventet sluttidspunkt: ' + str(actual_end.time()) + " (" + str(actual_end.day) + "." + str(
                   actual_end.month) + ")"), display_date,'Produceret Antal: ' + str(current_output)


@app.callback(
    [
        Output('gauge', 'value'),
        Output('live_graph', 'figure'),
        Output('gaugeCV', 'children'),

    ],
    [
        Input('live_data_update', 'n_intervals'),
    ])
def update_graph_one(n):
    dataFromNoSQL, timeToPost = sensor_handler.getDataForThePeroid(900, '', "laddermachine1")
    machine_one._resetPortsValues()
    machine_one.AssignValuesToPorts(dataFromNoSQL)
    MachineOn, PaceIn, PaceOut, StringError, ScrewError, Allarm = machine_one.ports.values()
    # latestErp = erp_handler.getLatestProducts(machine_one.machineName)
    isoutput = machine_one.is_output(dataFromNoSQL)
#    isOff = machine_one.check_machine(dataFromNoSQL)
    
    y_deque.append(PaceOut * 4)

    if isoutput == True:
        y2_deque.append(max(y_deque) + 10)
    else:
        y2_deque.append(0)

 
#    if isOff == False:
#        y3_deque.append(max(y_deque) + 5)
#    else:
#        y3_deque.append(0)
        
    # y_deque.append(random.randint(1,50))
    x_deque.append(sensor_handler.denmarkDateNow())
#    std_bottom_deque.append(32)
#    std_top_deque.append(64)

    trace1 = plotly.graph_objs.Scatter(
        x=list(x_deque),
        y=list(y_deque),
        name='stigemængde pr. time',
        mode='lines'
    )

    trace2 = plotly.graph_objs.Bar(
        x=list(x_deque),
        y=list(y2_deque),
        marker=dict(color='rgb(205,201,198)'),
        width=[2],
        name='stige ud,'

    )
    
#    trace3 = plotly.graph_objs.Bar(
#        x=list(x_deque),
#        y=list(y3_deque),
#        marker=dict(color='rgb(255,0,0)'),
#        width=[2],
#        name='maskinestatus,'
#
#    )

    data = [trace1, trace2]
    #print("LOOK AT THIS: ", max(x_deque) - timedelta(minutes=30), max(x_deque))

    return PaceOut * 4, {'data': data, 'layout': go.Layout(yaxis=dict(range=[0, max(y_deque) * 1.5]),
                                                           xaxis=dict(range=[max(x_deque) - timedelta(minutes=30),
                                                                             max(x_deque)]),
                                                           margin=go.layout.Margin(l=30, r=30, b=20, t=30,
                                                                                   pad=2))}, str(PaceOut * 4)


@app.callback(
    [

        Output('planned_output', 'children'),
        Output('time_since_last_error', 'children'),
        Output('fail_type', 'children'),
        Output('downtime_past_hour', 'children'),
    ],
    [
        Input('live_data_update', 'n_intervals'),
    ])
def errors_info(n):
    interval = 3600
    data, cr = sensor_handler.getDataForThePeroid(interval, '', 'laddermachine1')

    tsle, error_type = machine_one.time_since_last_error(data)
    listOf, b = machine_one.searchForMachineDowntime(data, interval)
    if listOf == 0:
        downtime_past_hour = 0
    else:
        downtime_past_hour = machine_one.getDtFromTimeInterval(interval, listOf)
    time_since = ""
    if tsle == "IKKE TIL":
        time_since = "---"
    else:
        time_since = str(round(float(tsle) / 60))

    return 'Planlagt antal: ' + '---', 'Tid siden sidste fejl: ' + time_since + " minuter", 'Fejltype: ' + error_type, 'Samlet stop pa grund af fejl indenfor den sidste time: ' + str(
        int(downtime_past_hour / 60)) + " minuter"





if __name__ == "__main__":
    handler = RotatingFileHandler('dolleLogs.log', maxBytes=50000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.server.logger.addHandler(handler)
    app.run_server()