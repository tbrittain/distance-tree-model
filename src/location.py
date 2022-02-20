import kdtree
from uuid import uuid4


class Location(object):
    """
    A location in the world using latitude and longitude.
    """

    def __init__(self, latitude: float, longitude: float, name: str = None):
        self._id = uuid4()
        self.latitude = latitude
        self.longitude = longitude
        self.coords = (self.latitude, self.longitude)
        self.name = name

    @staticmethod
    def decimal_to_dms(decimal: float, is_latitude=False) -> str:
        if is_latitude:
            direction = "S" if decimal < 0 else "N"
        else:
            direction = "W" if decimal < 0 else "E"

        decimal = abs(decimal)

        degrees = int(decimal)
        minutes = int((decimal - degrees) * 60)
        seconds = int((decimal - degrees - minutes / 60) * 3600)
        return f"{degrees:02d}°{minutes:02d}'{seconds:02d}\"{direction}"

    @staticmethod
    def from_string(string: str) -> "Location":
        """
        Creates a Location object from a DMS string.
        """

        string = string.replace(" ", "")
        string = string.replace("°", " ")
        string = string.replace("'", " ")
        string = string.replace("\"", " ")

        lat_long = [x.split(" ") for x in string.split(",")]

        lat = float(lat_long[0][0]) + float(lat_long[0][1]) / 60 + float(lat_long[0][2]) / 3600
        long = float(lat_long[1][0]) + float(lat_long[1][1]) / 60 + float(lat_long[1][2]) / 3600

        if lat_long[0][3] == "S":
            lat *= -1
        if lat_long[1][3] == "W":
            long *= -1

        return Location(lat, long)

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def __str__(self) -> str:
        formatted_name = self.name if self.name else "An unnamed location"

        return f"{formatted_name}: {self.decimal_to_dms(self.latitude, True)}" \
               f"{self.decimal_to_dms(self.longitude, False)} "

    def __repr__(self):
        return f"Location({self.latitude}, {self.longitude}, {self.name})"

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]


# Some constants of latitude and longitude
# https://www.latlong.net/convert-address-to-lat-long.html
first = Location(29.759776, -95.367863, "Tranquility Park")
second = Location(29.760744, -95.361919, "The Moonshiners Southern Table and Bar")
third = Location(29.755845, -95.359451, "Parking lots on Rusk near the Marriott")
fourth = Location(29.752026, -95.371339, "Close to that abandoned building downtown")
fifth = Location(29.745580, -95.374085, "Midtown Cadillac dealership")
sixth = Location(29.738463, -95.380802, "The Breakfast Klub near 59")
seventh = Location(29.705797, -95.459272)

locations = [first, second, third, fourth, fifth, sixth, seventh]

tree = kdtree.create(locations, dimensions=2)

city_hall = Location(29.760163, -95.369356, "City Hall")
closest_node = tree.search_nn(city_hall)
print(f"Closest node to {city_hall} is {closest_node[0]}")

local_foods_by_moonshiners = Location(29.761040, -95.362050, "Local Foods by Moonshiners")
closest_node = tree.search_nn(local_foods_by_moonshiners)
print(f"Closest node to {local_foods_by_moonshiners} is {closest_node[0]}")
