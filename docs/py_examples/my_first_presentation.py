# This two-slide presentation is based on the Gapminder example dataset bundled with Plotly Express.
# The code for the plots generated here are lifted verbatim from https://plotly.com/python/plotly-express/.

import plotly.express as px

from needful import Presentation, Slide

df = px.data.gapminder()

slide_1 = Slide(title="GDP Per Capita & Life Expectancy: 2007", columns=2)

fig_1 = px.scatter(df.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
                   hover_name="country", log_x=True, size_max=60, width=650, height=600)
fig_1.update_layout(margin=dict(t=30, l=10, r=10))

slide_1.add_plot(fig_1, row=1, column=2)

avg_life_exp = df.query("year==2007").groupby("continent").lifeExp.mean().round(1)

slide_1_text = f"""
* The plot on the right shows 2007 life expectancy against GDP per capita for 142 countries.
    * Countries are coloured according to their continent, and sized according to their population.


* Life expectancies in 2007 were lowest for African nations (avg. life expectancy: {avg_life_exp["Africa"]} yrs).
    * The highest was Oceania ({avg_life_exp["Oceania"]} yrs; only AUS & NZ data available.)


* Generally, higher GCP/capita are linked to longer life expectancies on all continents:
    * This effect is most robust for Asia, Americas and Europe.
    * It is less robust for Africa. E.g. South Africa has life expectancy approx. 20 years lower than
    countries with comparable GDP/capita.
"""
slide_1.add_textbox(content=slide_1_text, row=1, column=1)

slide_2 = Slide("GDP Per Capita & Life Expectancy: 1952–2007", columns=1)

# Generate the plot to be added to Slide #2.
fig_2 = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                   size="pop", color="continent", hover_name="country", facet_col="continent",
                   log_x=True, size_max=45, range_x=[100,100000], range_y=[25,90], height=450)

slide_2.add_plot(fig_2, row=1, column=1)

slide_2_text = """
* The animated plot above displays the change in GDP per capita and life expectancy between 1952–2007.
    * Click the play button (▶︎) to view the animation.
    * Use the slider to select individual years. 
"""
slide_2.add_textbox(slide_2_text, row=2, column=1)

pres = Presentation("My First Needful Presentation")

pres.add_slides([slide_1, slide_2])

pres.generate_html("My First Presentation.html")