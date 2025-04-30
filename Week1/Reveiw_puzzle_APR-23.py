import math

Length = float(input("what is the height of the pendulum?"))

time = 2 * math.pi * math.sqrt(Length / 9.81)

print(f"Time(seconds){time:.2f}")