import math

w = float(input('what is the width of the tire in millimeters? '))

a = float(input('what is the aspect ratio of the tire? '))

d = float(input('what is the diameter of the wheel in inches? '))

v = ((math.pi * (w ** 2)* a * (w * a + 2540 * d))/ 10000000000)

print(f'{v:.2f}')





