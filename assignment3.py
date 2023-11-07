"""Assignment 3."""
import datetime
import os
import pandas as pd

# TODO Check if changing is beneficial
START_DATE = datetime.date(2019, 3, 1)
END_DATE = datetime.date(2019, 8, 31)

# IMPORTANT! CHANGE ACCORDING TO YOUR SYSTEM
DIR = "D:/OneDrive/uni/nhhcourses/for14/assignments/assignment3"
TRIPS_FILE = "trip_data.csv"

# SUBOPTIMAL?
CARS = [6,7,8,9,10]


class Fleet:
    """A class that holds the cars of the rental company."""

    def __init__(self):
        self._cars = self.create_car_objects(CARS)
        self._trips = store_trips(CARS)
        #self._utilisation = self._compute_utilisation()

    def _compute_utilisation(self):
        """A method that returns the utilisation of all cars stored in the fleet.

        Returns:
            List: Utilisations of all cars stored in the fleet.
        """
        utilisation = []

        for car in self._cars:
            utilisation.append(car.get_utilisation())

        return utilisation

    def rearrange(self):
        """A method that rearranges the trips saved in the trips variable.
        """
        for index, row in self._trips.iterrows():
            start = row["start_ts"]
            end = row["last_logout_ts"]

            for car in self._cars:
                if car.get_number_trips() == 0 or start >= car.get_end_last_trip():
                    car.add_trip(start, end)
                    break

    def create_car_objects(self, car_ids):
        """A method that creates a list of cars based on their IDs.

        Args:
            car_ids (List): The IDs of cars that should be instantiated.

        Returns:
            List: A list of cars with corresponding IDs.
        """
        car_array = []
        for car_id in car_ids:
            car_array.append(Car(car_id=car_id))
        return car_array


class Car:
    """A class that saves the characteristics of a car of the rental company."""

    def __init__(self, car_id):
        self._id = car_id
        self._trips = pd.DataFrame(columns=["start", "end"])
        self._end_last_trip = datetime.date(1970, 1, 1) # First trip always after 1970
        self._number_trips = 0
        # self._utilisation = self._compute_utilisation()

    def add_trip(self, start, end):
        """A method that adds a trip to the car's trips dataframe.

        Args:
            start (Datetime): The start of the trip.
            end (Datetime): The end of the trip.
        """
        new_trip = {"start": start, "end": end}
        df_new_trip = pd.DataFrame([new_trip])
        self._trips = pd.concat([self._trips, df_new_trip])
        self._end_last_trip = end
        self._number_trips += 1

    def get_end_last_trip(self):
        """A method that returns the end of the last trip.

        Returns:
            Datetime: End of the last trip of the car.
        """
        return self._end_last_trip

    def get_number_trips(self):
        """A method that returns the number of trips of the car.

        Returns:
            Integer: Number of trips that the car currently has.
        """
        return self._number_trips

    def _compute_utilisation(self):
        """A method that computes the utilisation of the car.

        Returns:
            #Float: The utilisation of the car.
        """
        # rental_time = 0

        rental_time = sum(self._trips["last_logout_ts"] - self._trips["start_ts"])

        # for item in self._trips:
        #     time = sum(item.iloc[:, 1] - item.iloc[:, 0], datetime.timedelta())
        #     rental_time += time

        period_length = END_DATE - START_DATE

        return rental_time / period_length

    # ---------------- GETTERS AND SETTERS ---------------- #

    def get_id(self):
        """Getter method for the id variable.

        Returns:
            Integer: The id variable of the car object.
        """
        return self._id

    def get_trips(self):
        """Getter method for the trips variable.

        Returns:
            Dataframe: The trips variable of the car object.
        """
        return self._trips

#    def get_utilisation(self):
        """Getter method for the utilisation variable.

        Returns:
            Float: The utilisation variable of the car object.
        """
#        return self._utilisation


# ---------------- HELPER FUNCTIONS ---------------- #

# TODO Change description
def store_trips(cars):
    """ A method that loads the trips of all cars and processes them
    in order to be used by the Fleet class.

    Returns:
        dataframe: The subsetted and sorted dataframe
        only including those trips that are done by cars
        specified in cars and lying in the date interval
        specified by the global variables.
    """
    trips = import_csv(DIR, TRIPS_FILE)
    trips = select_by_value(trips, "car_id", cars)

    date_interval = (START_DATE, END_DATE)
    time_columns = ("start_ts", "last_logout_ts")

    trips = convert_columns_to_datetime(trips, time_columns)
    trips = select_by_date_interval(trips, time_columns, date_interval)

    sort_by = "start_ts"
    trips = sort_df(trips, sort_by)

    return trips


def select_by_value(df, column, values):
    """Function that takes a list of values and returns
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


def convert_columns_to_datetime(df, columns):
    """Converts character columns to datetime.

    Args:
        columns (list): A list of columns that should be converted.
        df (dataframe): The dataframe to be changed.

    Returns:
        dataframe: A dataframe with converted columns.
    """
    return_df = df.copy()

    for column in columns:
        return_df[column] = pd.to_datetime(return_df[column], utc=True)
        return_df[column] = return_df[column].dt.tz_convert("Europe/Oslo")

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
    df_copy = df_copy.reset_index(drop=True)

    return df_copy


def select_by_date_interval(df, columns, interval):
    """A function that selects rows of a df based on the
    column values being inside a date interval.

    Args:
        df (Dataframe): The dataframe to be subsetted.
        columns (Tuple): The name of the columns to base the subsetting on
        interval (Tuple): The date interval to be filtered for

    Returns:
        dataframe: a new dataframe with only subsetted rows.
    """
    return df[(df[columns[0]].dt.date >= interval[0]) & (df[columns[1]].dt.date <= interval[1])]



def import_csv(directory, filename):
    """Imports csv data file into the workspace
    and returns a dataframe with all entries.

    Args:
        directory (String): Name of the directory
        filename (String): Name of the csv file.

    Returns:
        Dataframe: A dataframe representation of the csv file.
    """
    os.chdir(directory)

    with open(filename, encoding="utf-8") as csvfile:
        return pd.read_csv(csvfile, delimiter=";")
