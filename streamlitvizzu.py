# import streamlit, pandas and ipyvizzu
 
from streamlit.components.v1 import html
import streamlit as st
import pandas as pd
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
 
 
def create_chart():
    # initialize Chart
 
    chart = Chart(
        width="800px", height="600px", display=DisplayTarget.MANUAL
    )
 
    # create and add data to Chart
 
    data = Data()
    df1 = pd.read_csv(
        "https://ipyvizzu.vizzuhq.com/0.17/showcases/titanic/titanic.csv"
    )
    # continent,country,year,fertility,lifeExpectancy,mean_house_income,median_age_year,population
    df = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/gapminder_data.csv')
    # st.dataframe(df1)
    df=df[df['year']==2024]
    data.add_df(df)
 
    chart.animate(data)
 
    # add config to Chart
 
    chart.animate(
        Config(
            {
                "x": "population",
                "y": "continent",
                "label": "population",
                "title": "Población",
            }
        )
    )

    chart.animate(
        Config(
            {                
                "color": "continent",
            }
        )
    )

    chart.animate(
        Config(
            {
                "sort": "byValue",
            }
        )
    )

    # chart.animate(
    #     Config(
    #         {
    #             "x": "country",                
    #             "y": "population",
    #             "label": "country",
    #             "color": "country",
    #         }
    #     )
    # )
    chart.animate(
        Config(
            {
                "channels": {
                    "x": "lifeExpectancy",
                    "y": "fertility",
                    "size": "population",
                    "color": "continent",
                    "label": "country",
                },
                "geometry": "circle",
            }
        )
    )
    
    chart.animate(Config({"channels": {"label": "country"}}))
    
    chart.feature("tooltip", True)

    chart.animate(
        Config(
            {
                "channels": {
                    "x": "lifeExpectancy",
                    "y": "fertility",
                    "size": "population",
                    "color": "continent",
                    "label": "continent",
                },
                "geometry": "circle",
            }
        )
    )
    # chart.animate(Config({"x": "Count", "y": ["Sex", "Survived"]}))
 
    # add style to Chart
 
    # chart.animate(Style({"title": {"fontSize": 35}}))
 
    # return generated html code
 
    return chart._repr_html_()
 
 
# generate Chart's html code
 
CHART = create_chart()
 
 
# display Chart
 
html(CHART, width=900, height=600)
