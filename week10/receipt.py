import csv
from datetime import datetime

def read_dictionary(filename, key_column_index):
    """Read the contents of a CSV file into a compound
    dictionary and return the dictionary.

    Parameters
        filename: the name of the CSV file to read.
        key_column_index: the index of the column
            to use as the keys in the dictionary.
    Return: a compound dictionary that contains
        the contents of the CSV file.
    """
    dictionary = {}
    try:
        with open(filename, mode="r", newline='') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  
            for row in reader:
                if len(row) == 0:
                    continue
                key = row[key_column_index]
                dictionary[key] = [row[1], float(row[2])]
        return dictionary
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except PermissionError:
        print(f"Error: No permission to read '{filename}'.")

def main():
    try:
        print("Inkom Emporium\n")
        products_dict = read_dictionary("products.csv", 0)
        number_of_items = 0
        subtotal = 0.0
        SALES_TAX_RATE = 0.06
        with open("request.csv", mode="r", newline='') as request_file:
            reader = csv.reader(request_file)
            next(reader)  
            for row in reader:
                if len(row) == 0:
                    continue
                product_number = row[0]
                quantity = int(row[1])
                product_info = products_dict[product_number]
                product_name = product_info[0]
                product_price = product_info[1]
                print(f"{product_name}: {quantity} @ {product_price:.2f}")
                number_of_items += quantity
                subtotal += product_price * quantity
        print(f"\nNumber of Items: {number_of_items}")
        print(f"Subtotal: {subtotal:.2f}")
        sales_tax = subtotal * SALES_TAX_RATE
        print(f"Sales Tax: {sales_tax:.2f}")
        total = subtotal + sales_tax
        print(f"Total: {total:.2f}\n")
        print("Thank you for shopping at the Inkom Emporium.")
        current_date_and_time = datetime.now()
        print(f"{current_date_and_time:%a %b %d %H:%M:%S %Y}")
    except FileNotFoundError as e:
        print("Error: missing file")
        print(e)
    except KeyError as e:
        print("Error: unknown product ID in the request.csv file")
        print(e)
    except PermissionError as e:
        print("Error: No permission to read a file.")
        print(e)

if __name__ == "__main__":
    main()
