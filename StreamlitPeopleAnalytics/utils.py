import plotly.express as px
import streamlit as st


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def aplicarFormatoChart(fig,controls=False,legend=False,hoverTemplate=None,titulo=None,subtitulo=None):
    fig.update_layout(paper_bgcolor='white')
    fig.update_layout(plot_bgcolor='white')
    fig.update_layout(showlegend=legend)
    fig.update_coloraxes(showscale=legend)
    fig.update_layout(title_pad_l=20)
    fig.update_layout(
    # font_family="Open Sans",
    #font_color="#8dc73f",
    # title_font_family="verdana",
    title_font_color="black",
    title_font_size=20,
    font_size=15,
    #legend_title_font_color="green"
    )

    if hoverTemplate:
        if hoverTemplate=="%":
            fig.update_traces(hovertemplate='<b>%{x}</b> <br> %{y:,.2%}')
        elif hoverTemplate=="$":
            fig.update_traces(hovertemplate='<b>%{x}</b> <br> $ %{y:,.1f}')
        elif hoverTemplate=="#":
            fig.update_traces(hovertemplate='<b>%{x}</b> <br> %{y:,.0f}')
    if controls:
        fig.update_xaxes(
            rangeslider_visible=True           
        )
    fig.update_layout(
            autosize=True,
            margin=dict(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4
            )
    )
    fig.update_layout(legend_title=None,legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    if titulo:
        fig.update_layout(title=f"<span style='font-size:20px'>{titulo}</span><br><span style='color:gray;font-size:15px'>{subtitulo}</span>")
    return fig
