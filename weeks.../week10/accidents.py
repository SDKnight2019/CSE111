# Import the csv module so that it can be used
# to read from the accidents.csv file.
import csv

# Column numbers from the accidents.csv file.
YEAR_COLUMN = 0
FATALITIES_COLUMN = 1
INJURIES_COLUMN = 2
CRASHES_COLUMN = 3
FATAL_CRASHES_COLUMN = 4
DISTRACT_COLUMN = 5
PHONE_COLUMN = 6
SPEED_COLUMN = 7
DUI_COLUMN = 8
FATIGUE_COLUMN = 9


def main():
    # Prompt for filename until file opens successfully
    while True:
        filename = input("Name of file that contains NHTSA data: ")
        try:
            text_file = open(filename, "rt")
            break
        except FileNotFoundError as e:
            print(e)
            print("File not found. Please try again.")

    # Prompt for percentage, validate input and range
    while True:
        perc_input = input("Percent reduction of texting while driving [0, 100]: ")
        try:
            perc_reduc = float(perc_input)
        except ValueError as e:
            print(f"Error: {e}")
            continue
        if perc_reduc < 0:
            print(f"Error: {perc_reduc} is too low. Please enter a different number.")
            continue
        if perc_reduc > 100:
            print(f"Error: {perc_reduc} is too high. Please enter a different number.")
            continue
        break

    print()
    print(f"With a {perc_reduc}% reduction in using a cell",
        "phone while driving, approximately the",
        "following number of injuries and deaths",
        "would have been prevented in the USA.", sep="\n")
    print()
    print("Year, Injuries, Deaths")

    try:
        with text_file:
            reader = csv.reader(text_file, strict=True)
            next(reader)  # skip header

            for row_num, row in enumerate(reader, start=2):
                try:
                    year = row[YEAR_COLUMN]
                    injur, fatal = estimate_reduction(row, PHONE_COLUMN, perc_reduc)
                    print(year, injur, fatal, sep=", ")
                except ZeroDivisionError:
                    print(f"Error: Zero Fatal crashes at line {row_num} in {filename} skipping row.")
                except IndexError as e:
                    print(f"Error in row {row_num}: {e}")
    except csv.Error as e:
        print(f"Error: CSV formatting issue in file {filename}: {e}")


def estimate_reduction(row, behavior_key, perc_reduc):
    """Estimate and return the number of injuries and deaths that
    would not have occurred on U.S. roads and highways if drivers
    had reduced a dangerous behavior by a given percentage.

    Parameters
        row: a CSV row of data from the U.S. National Highway Traffic
            Safety Administration (NHTSA)
        behavior_key: heading from the CSV file for the dangerous
            behavior that drivers could reduce
        perc_reduc: percent that drivers could reduce a dangerous
            behavior
    Return: The number of injuries and deaths that may have been
        prevented
    """
    
    behavior = int(row[behavior_key])
    fatal_crashes = int(row[FATAL_CRASHES_COLUMN])
    ratio = perc_reduc / 100 * behavior / fatal_crashes

    fatalities = int(row[FATALITIES_COLUMN])
    injuries = int(row[INJURIES_COLUMN])

    reduc_fatal = int(round(fatalities * ratio, 0))
    reduc_injur = int(round(injuries * ratio, 0))
    return reduc_injur, reduc_fatal


# If this file was executed like this:
# > python accidents.py
# then call the main function. However, if this file
# was simply imported, then skip the call to main.
if __name__ == "__main__":
    main()
