import plotly.express as px

def line_chart(df,x,y,title, color=None):
    fig = px.line(df, x=x,y=y,title=title,markers=True)
    if color:
        fig.update_traces(line=dict(width=3, color=color))

    fig.update_layout(template="plotly_white", height=400,title_x=0.02, margin=dict( l=20,r=20,t=60,b=20),
        hovermode="x unified"
    )
    return fig

def bar_chart(df,x,y,title,color=None, orientation="v"):
    fig = px.bar(df, x=x,y=y,title=title,text_auto=True, orientation=orientation)
    if color:
        fig.update_traces(marker_color=color)
    fig.update_layout(template="plotly_white", height=400, title_x=0.02,margin=dict(l=20,r=20,t=60,b=20))
    return fig

def pie_chart(df, names,values,title):
    fig = px.pie( df, names=names, values=values, hole=0.45,title=title)
    fig.update_layout(template="plotly_white", height=400,title_x=0.02,margin=dict(l=20,r=20,t=60,b=20))
    return fig