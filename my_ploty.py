import plotly.plotly as py
import plotly.graph_objs as go

# Add original data
x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# last 8 weeks of data (y0 is the most recent):
y0_org=[1, 0, 1, 1, 0, 1, 0]
y1_org=[1, 1, 0, 1, 1, 0, 0]
y2_org=[0,1 , 1, 1, 0, 1, 0]
y3_org=[1, 1, 0, 1, 0, 0, 0]
y4_org=[1, 1, 1, 1, 0, 1, 0]
y5_org=[0, 1, 1, 1, 0, 1, 0]
y6_org=[1, 1, 0, 1, 0, 1, 0]
y7_org=[1, 1, 0, 1, 0, 0, 0]
y8_org=[1, 1, 0, 1, 0, 1, 0]


# Add data to create cumulative stacked values
y0_stck=y0_org
y1_stck=[y0+y1 for y0, y1 in zip(y0_org, y1_org)]
y2_stck=[y0+y1+y2 for y0, y1, y2 in zip(y0_org, y1_org, y2_org)]
y3_stck=[y0+y1+y2+y3 for y0, y1, y2, y3 in zip(y0_org, y1_org, y2_org, y3_org)]
y4_stck=[y3_stck+y4 for y3_stck, y4 in zip(y3_stck, y4)]
y5_stck=[y4_stck+y5 for y4_stck, y5 in zip(y4_stck, y5)]
y6_stck=[y5_stck+y6 for y5_stck, y6 in zip(y5_stck, y6)]
y7_stck=[y6_stck+y7 for y6_stck, y7 in zip(y6_stck, y7)]
y8_stck=[y7_stck+y8 for y7_stck, y8 in zip(y7_stck, y8)]

# Make original values strings and add % for hover text
y0_txt=[str(y0)+'%' for y0 in y0_org]
y1_txt=[str(y1)+'%' for y1 in y1_org]
y2_txt=[str(y2)+'%' for y2 in y2_org]

trace0 = go.Scatter(
    x=x,
    y=y0_stck,
    text=y0_txt,
    hoverinfo='x+text',
    mode='lines',
    line=dict(width=0.5,
              color='rgb(131, 90, 241)'),
    fill='tonexty'
)
trace1 = go.Scatter(
    x=x,
    y=y1_stck,
    text=y1_txt,
    hoverinfo='x+text',
    mode='lines',
    line=dict(width=0.5,
              color='rgb(111, 231, 219)'),
    fill='tonexty'
)
trace2 = go.Scatter(
    x=x,
    y=y2_stck,
    text=y2_txt,
    hoverinfo='x+text',
    mode='lines',
    line=dict(width=0.5,
              color='rgb(184, 247, 212)'),
    fill='tonexty'
)
data = [trace0, trace1, trace2]

fig = go.Figure(data=data)
py.iplot(fig, filename='stacked-area-plot-hover')
