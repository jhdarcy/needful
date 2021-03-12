from needful import Presentation, Slide

slide_1 = Slide(title="This is Slide #1", columns=1)

slide_1_text = """
Here are some bullet points for Slide #1:

* Bullet 1.
* Bullet 2.
    * *Bullet 2a*
    * *Bullet 2b*
* And so on...

**...you get the idea.**
"""

slide_1.add_textbox(content=slide_1_text, row=1, column=1)

slide_2 = Slide(title="Welcome to Slide #2", columns=1)

slide_2_text = """
Now for some [Lorem Ipsum](https://www.lipsum.com/):

<br>
<center>
*Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus placerat mauris ut mattis hendrerit.
Proin ornare leo tortor, a iaculis nisi eleifend quis. Proin feugiat elit vitae dolor faucibus vestibulum.
Curabitur tempus placerat lacus sit amet feugiat. Sed vel sodales neque. Phasellus in tempus neque.
Maecenas auctor turpis vel ex bibendum dapibus. Aliquam ac ex eget neque convallis interdum. Etiam maximus suscipit magna,
a porttitor turpis sagittis a. Phasellus sodales vitae elit non porttitor. Aliquam condimentum felis a dictum porta.
In blandit, eros vitae facilisis condimentum, dolor leo luctus enim, et semper nibh nunc sed tellus.*
</center>
"""

slide_2.add_textbox(slide_2_text, row=1, column=1)

pres = Presentation(title="My First Needful Presentation")
pres.add_slides([slide_1, slide_2])

pres.generate_html("My First Presentation.html")