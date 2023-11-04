"""A program that reschedules car trips for a rental company and prints the new utilisation."""

import pandas as pd
import os
import datetime


def main():
    # Change depending on file location
    os.chdir("D:/OneDrive/uni/nhhcourses/for14/assignments/assignment2")

    with open("trip_data.csv") as csvfile:
        trips = pd.read_csv(csvfile, delimiter=";")

    # Preprocessing ----
    car_list = [6, 7, 8, 9, 10]
    selected_trips = select_by_value(trips, "car_id", car_list)

    columns = ["start_ts", "last_logout_ts"]
    selected_trips = convert_columns_to_datetime(columns, selected_trips)

    sort_by = ["car_id", "start_ts"]
    selected_trips = sort_df(selected_trips, sort_by)

    # Calculate entire timespan from first reservation to last reservation ----
    rental_period = duration(selected_trips)

    # Calculate utilisation before rescheduling ----
    utilisation_per_car = calculate_utilisation_per_car(selected_trips, rental_period)
    print(f"The utilisation by car before rescheduling is: {utilisation_per_car}")
    
    # Reschedule and calculate utilisation after rescheduling ----
    rescheduled_trips = reschedule(selected_trips)
    new_utilisation = calculate_utilisation_per_car(rescheduled_trips, rental_period)
    print(f"The utilisation by car after rescheduling is: {new_utilisation}")


# Functions ----
def select_by_value(df, column, values):
    """ Function that takes a list of values and returns
        the corresponding rows in a dataframe.

    Args:
        df (dataframe): The dataframe of which the subset should be selected.
        column (String): A string that defines the column in which the value should be 
        values (list): A list of values whose rows should be selected.

    Returns:
        dataframe: A dataframe of all rows corresponding to the values.
    """
    selection = df.loc[df[column].isin(values)]

    return selection


def convert_columns_to_datetime(columns, df):
    """ Converts character columns to datetime.

    Args:
        columns (list): A list of columns that should be converted.
        df (dataframe): The dataframe to be changed.

    Returns:
        dataframe: A dataframe with converted columns.
    """
    return_df = df.copy()

    for column in columns:
        return_df[column] = pd.to_datetime(return_df[column], utc = True)
        return_df[column] = return_df[column].dt.tz_convert('Europe/Oslo')

    return return_df


def sort_df(df, by):
    """Sorts a dataframe by a column, and resets the indices.

    Args:
        df (dataframe): The dataframe to be sorted.
        by (String): The column to be sorted after.

    Returns:
        dataframe: The dataframe with applied changes.
    """
    df_copy = df.copy()

    df_copy = df_copy.sort_values(by)
    df_copy = df_copy.reset_index(drop = True)

    return df_copy


def duration(trips):
    """ Function that gives the length of the rental period based on df.

    Args:
        df (dataframe): A dataframe with the trips to be evaluated.

    Returns:
        timedelta: The total length of the rental period.
    """
    first_utilisation = trips.min()["start_ts"]
    last_utilisation = trips.max()["last_logout_ts"]
    utilisation_length = last_utilisation - first_utilisation

    return utilisation_length


def calculate_utilisation_per_car(trips, period):
    """A function that calculates utilisation share by car.

    Args:
        trips (dataframe): A dataframe of all trips.
        period (timedelta): The length of the total rental period.

    Returns:
        List: A list of the utilisation share by car.
    """
    grouped_trips = trips.groupby("car_id")

    # Calculate utilised time per car
    sum_utilisation = []
    for key, item in grouped_trips:
        time = sum(item.iloc[:,1] - item.iloc[:,0], datetime.timedelta()) 
        sum_utilisation.append(time)

    # Calculate utilisation share per car
    share_utilisation = []
    for time in sum_utilisation:
        if time == 0:
            share_utilisation.append(1) # If car is not used, utilisation is 1
        else:
            share_utilisation.append(time / period)

    return share_utilisation



# Rescheduling
def reschedule(trips):
    """A function that reschedules the trips given in "trips" using a greedy algorithm.

    Args:
        trips (dataframe): A dataframe of trips. 

    Returns:
        dataframe: A dataframe with rescheduled trips.
    """
    # Sort trips by start time
    sort_by_start = "start_ts"
    sorted_trips = sort_df(trips, sort_by_start)

    assigned_trips = [[], [], [], [], []] # List of lists of dictionaries

    for index, row in sorted_trips.iterrows():
        start = row["start_ts"]
        end = row["last_logout_ts"]
        
        for i in range(len(assigned_trips)):
            # For all trips, do the following:
            # There are cars 6 to 10.
            # 1. Check if the trip can be assigned to car 6 (the trip starts after the end of the current trip)
            # 2. If yes, assign it to the car
            # 3. If no, assign the trip to the next car
            # 4. Repeat until all trips are assigned
            if len(assigned_trips[i]) == 0 or start >= assigned_trips[i][-1]["end"]:
                assigned_trips[i].append({"start": start, "end": end, "car_id": i+6})
                break

    rescheduled_trips = pd.DataFrame(sum(assigned_trips, [])) # Create a dataframe from the list of lists of dictionaries
    return rescheduled_trips


if __name__ == "__main__":
    main()