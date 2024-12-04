from sqlite3 import connect
import numpy as np


class Database:
    """
    A class used to represent the Database for storing food waste data.
    """

    def __init__(self):
        """
        Initializes the Database with the database name.
        """
        self._db_name = "data.db"

    def table_exists(self, table_name):
        """
        Checks if a table exists in the database.

        Args:
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        db = connect(self._db_name)
        cursor = db.cursor()
        table_result = cursor.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{str(table_name)}';"
        ).fetchall()
        if table_result == [(0,)]:
            db.close()
            return False
        print(table_result)
        result_length = len(table_result)
        if result_length > 0:
            return True
        return False

    def create_db(self):
        """
        Creates the FoodWaste table in the database if it does not exist.
        """
        print("checking if exist")
        if not self.table_exists("FoodWaste"):
            db = connect(self._db_name)
            db.execute(
                """CREATE TABLE "FoodWaste" (
                "Epoch" INTEGER NOT NULL UNIQUE,
                "GuestNo" INTEGER NOT NULL,
                "ServingsNo" INTEGER NOT NULL,
                "PricingRank" INTEGER NOT NULL,
                "PrepMethodRank" INTEGER NOT NULL,
                "CustomerRank" INTEGER NOT NULL,
                "ServingsWasted" REAL,
                "DateTime" TEXT NOT NULL,
                PRIMARY KEY("Epoch")
            );"""
            )
            db.commit()
            db.close()

    def get(self):
        """
        Retrieves all records from the FoodWaste table.

        Returns:
            list: A list of tuples containing all records from the FoodWaste table.
        """
        db = connect(self._db_name)
        items = list(db.execute("SELECT * FROM FoodWaste"))
        db.close()
        return items

    def insert(self, vals):
        """
        Inserts a new record into the FoodWaste table.

        Args:
            vals (list): A list of values to insert into the table.
        """
        db = connect(self._db_name)
        query = "INSERT INTO FoodWaste VALUES(?, ?, ?, ?, ?, ?, ?, ?)"

        pricecat = ["Low", "Moderate", "High"]
        prep = ["Finger Food", "Sit-down Dinner", "Buffet"]
        regular = ["Occasional", "Regular"]

        vals[3] = pricecat[int(vals[3]) - 1]
        vals[4] = prep[int(vals[4]) - 1]
        vals[5] = regular[int(vals[5]) - 1]

        db.execute(
            query,
            (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]),
        )
        db.commit()
        db.close()


class RegressionModel:
    """
    A class used to represent the Regression Model for predicting food waste.
    """

    def __init__(self):
        """
        Initializes the RegressionModel with predefined model parameters.
        """
        self._model = {
            "beta": [
                [28.58492779],
                [2.71431472],
                [2.44460242],
                [0.1488482],
                [1.56153167],
                [5.30286446],
            ],
            "means": [318.23717949, 411.35977564, 1.88461538, 1.79647436, 2.14182692],
            "stds": [67.3699352, 64.63589751, 0.31948553, 0.71963337, 0.78236607],
        }
        self._beta = np.array(self._model["beta"])
        self._means = np.array(self._model["means"])
        self._stds = np.array(self._model["stds"])

    def predict_val(self, dat):
        """
        Predicts the value of food waste based on input data.

        Args:
            dat (dict): A dictionary containing the input data.

        Returns:
            float: The predicted value of food waste.
        """
        arr_a = np.array(
            [
                [
                    int(dat["guestno"]),
                    int(dat["serveno"]),
                    int(dat["regular"]),
                    int(dat["prep"]),
                    int(dat["price"]),
                ]
            ]
        )

        arr_b = (arr_a - self._means) / self._stds
        arr_A = np.insert(arr_b, 0, 1, axis=1)
        result = np.matmul(arr_A, self._beta)
        return result[0][0]