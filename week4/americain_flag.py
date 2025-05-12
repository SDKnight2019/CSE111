import turtle

def draw_rectangle(x, y, width, height, color):
    turtle.penup()
    turtle.goto(x, y)
    turtle.setheading(0)
    turtle.pendown()
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(2):
        turtle.forward(width)
        turtle.right(90)
        turtle.forward(height)
        turtle.right(90)
    turtle.end_fill()

def draw_star(x, y, radius, color):
    turtle.penup()
    turtle.goto(x, y)
    turtle.setheading(-72/2)
    turtle.forward(radius)
    turtle.setheading(0)
    turtle.pendown()
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(5):
        turtle.forward(radius * 2)
        turtle.right(144)
    turtle.end_fill()

def draw_us_flag(flag_width):
    turtle.speed(0)
    flag_height = flag_width * 10 / 19
    stripe_height = flag_height / 13
    union_width = flag_width * 0.4
    union_height = stripe_height * 7

    # Draw the 13 stripes
    for i in range(13):
        color = 'red' if i % 2 == 0 else 'white'
        draw_rectangle(-flag_width / 2, flag_height / 2 - i * stripe_height,
                       flag_width, stripe_height, color)

    # Draw the blue union
    draw_rectangle(-flag_width / 2, flag_height / 2,
                   union_width, union_height, 'navy')

    # Draw the 50 stars
    star_radius = stripe_height * 0.3
    rows = 9
    cols_even = 6
    cols_odd = 5
    spacing_x = union_width / cols_even
    spacing_y = union_height / rows

    for row in range(rows):
        num_stars = cols_even if row % 2 == 0 else cols_odd
        offset_x = 0 if row % 2 == 0 else spacing_x / 2
        for col in range(num_stars):
            x = -flag_width / 2 + offset_x + col * spacing_x + spacing_x / 2
            y = flag_height / 2 - row * spacing_y - spacing_y / 2
            draw_star(x, y, star_radius, 'white')

    turtle.hideturtle()
    turtle.done()

# Set your desired flag width here
draw_us_flag(760)
