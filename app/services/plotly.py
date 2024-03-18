import json
import collections

import plotly as plotly
import plotly.graph_objects as go



def get_graph(raw_data):
    sorted_data = sorted(raw_data, key=lambda d: d['n'])
    nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    data_freq = list(d["data_frequency"] for d in sorted_data)
    ben_freq = list(d["benford_frequency"] for d in sorted_data)
    diff_freq = list(d["difference_frequency"] for d in sorted_data)

    data_freq_per = list(d["data_frequency_percent"] for d in sorted_data)
    ben_freq_per = list(d["benford_frequency_percent"] for d in sorted_data)
    diff_freq_per = list(d["difference_frequency_percent"] for d in sorted_data)

    fig = go.Figure()
    fig_percents = go.Figure()
    # Create and style traces
    fig.add_trace(go.Scatter(x=nums, y=data_freq, name='Data #',
                             line=dict(color='firebrick', width=4)))
    fig_percents.add_trace(go.Scatter(x=nums, y=data_freq_per, name='Data # %',
                             line=dict(color='royalblue', width=4)))
    fig.add_trace(go.Scatter(x=nums, y=ben_freq, name='Benford #',
                             line=dict(color='firebrick', width=4,
                                       dash='dash')  # dash options include 'dash', 'dot', and 'dashdot'
                             ))
    fig_percents.add_trace(go.Scatter(x=nums, y=ben_freq_per, name='Benford # %',
                             line=dict(color='royalblue', width=4, dash='dash')))
    fig.add_trace(go.Scatter(x=nums, y=diff_freq, name='Diff. #',
                             line=dict(color='firebrick', width=4, dash='dot')))
    fig_percents.add_trace(go.Scatter(x=nums, y=diff_freq_per, name='Diff. # %',
                             line=dict(color='royalblue', width=4, dash='dot')))
    # Edit the layout
    fig.update_layout(title='Input Digit Frequency, Predicted Benford Frequency, and Difference',
                      xaxis_title='Digit',
                      yaxis_title='Counts')

    fig_percents.update_layout(title='Input Digit Frequency, Predicted Benford Frequency, and Difference', xaxis_title='Digit', yaxis_title='Percent')
    return [fig, fig_percents]


def dump_plotly_data(data):
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON