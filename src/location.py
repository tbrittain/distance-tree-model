import math
from uuid import uuid4


class Location(object):
    """
    A location in the world using latitude and longitude.
    """

    def __init__(self, latitude: float, longitude: float, name: str = None, location_id: str = None):
        self.location_id = location_id if location_id else str(uuid4())
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
        :param string: The DMS string in the format such as "40° 39' 51" N, 73° 56' 19" W"
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

    @staticmethod
    def distance(location1: "Location", location2: "Location", metric=False) -> float:
        """
        Calculates the distance between two locations using the Haversine formula.

        :param location1: The first location.
        :param location2: The second location.
        :param metric: Whether to return the distance in kilometers or miles.
        :return: The distance between the two locations.
        """

        earth_radius_km = 6371
        diff_lat = math.radians(location1.latitude - location2.latitude)
        diff_long = math.radians(location1.longitude - location2.longitude)

        a = math.sin(diff_lat / 2) * math.sin(diff_lat / 2) + \
            math.cos(math.radians(location1.latitude)) * math.cos(math.radians(location2.latitude)) * \
            math.sin(diff_long / 2) * math.sin(diff_long / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance_km = earth_radius_km * c
        if metric:
            return distance_km
        else:
            return distance_km * 0.621371

    @staticmethod
    def _degrees_to_radians(degrees: float) -> float:
        return degrees * (math.pi / 180)

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __hash__(self):
        return hash(self.coords)

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
