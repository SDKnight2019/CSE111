import math

import datetime 

import re

w = float(input('what is the width of the tire in millimeters? '))

a = float(input('what is the aspect ratio of the tire? '))

d = float(input('what is the diameter of the wheel in inches? '))

v = ((math.pi * (w ** 2)* a * (w * a + 2540 * d))/ 10000000000)

#print(f'{v:.2f}')


current_time = datetime.datetime.now()

formatted_time = current_time.strftime("%m/%d/%Y %I:%M %p")

with open("volumes.txt", "a") as file:
    file.write(f"{formatted_time} , {w}, {a}, {d}, {v:.2f}\n")

yes_or_no = input('would you like to buy tires in the size you gave us for your vehicle? yes or no?').strip().lower()

if yes_or_no == 'yes':
        
    while True:
            
        phone_number = input('What is your phone number?').strip()

        cleaned_phone = re.sub(r"[^\d]", "", phone_number)

        if len(cleaned_phone) ==10:
            
            print("Phone number accepted:", cleaned_phone)

            with open('volumes.txt', 'a') as file:
                file.write(f"Phone number: {cleaned_phone}\n")

                break
        
        else:
                
            print('invalid phone number. Please try again.')

else:
        
        print('No problem! Let us know if you changed your mind!')