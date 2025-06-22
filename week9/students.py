import csv
 
 
def main():
    I_NUMBER_INDEX = 0
    NAME_INDEX = 1
    I_NUMBER = GET_STUDENT_I_NUMBER()
       
    student_dict = read_dictionary('students.csv', I_NUMBER_INDEX)
 
 
 
 
 
def read_dictionary(filename, key_column_index):
    """Read the contents of a CSV file into a
    dictionary and return the dictionary.
 
    Parameters
        filename: the name of the CSV file to read.
    Return: a dictionary that contains
        the contents of the CSV file.
    """
    dictionary = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            key = row[key_column_index]
            dictionary[key] = row[1]
        return dictionary
 
def GET_STUDENT_I_NUMBER():
     
    I_NUMBER = input("Please Enter an I-Number: ")
    while len(I_NUMBER) != 9:
        I_NUMBER = input("Please Enter A Valid 9 Digit I-Number: ")
    I_NUMBER = int(I_NUMBER)
    return I_NUMBER
   
 
 
 
 
 
if __name__ == "__main__":
    main()
 