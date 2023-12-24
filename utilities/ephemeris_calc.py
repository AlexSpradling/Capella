from skyfield.api import load, Star, Topos
from skyfield.data import hipparcos
import datetime as dt
import tabulate
import prompt_toolkit
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter


# Load Data and Initialize Named Stars
def load_data_and_stars():
    planets = load("de421.bsp")
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)

    named_star_dict = {
        "Acamar": 13847,
        "Achernar": 7588,
        "Acrux": 60718,
        "Adhara": 33579,
        "Aldebaran": 21421,
        "Algol": 14576,
        "Alioth": 62956,
        "Alkaid": 67301,
        "Alnair": 109268,
        "Alnilam": 26311,
        "Alphard": 46390,
        "Alphecca": 76267,
        "Alpheratz": 677,
        "Altair": 97649,
        "Ankaa": 2081,
        "Antares": 80763,
        "Arcturus": 69673,
        "Atria": 82273,
        "Avior": 41037,
        "Becrux": 62434,
        "Bellatrix": 25336,
        "Betelgeuse": 27989,
        "Canopus": 30438,
        "Capella": 24608,
        "Deneb": 102098,
        "Denebola": 57632,
        "Diphda": 3419,
        "Dubhe": 54061,
        "Elnath": 25428,
        "Enif": 107315,
        "Eltanin": 87833,
        "Fomalhaut": 113368,
        "Gacrux": 61084,
        "Gienah": 102488,
        "Hadar": 68702,
        "Hamal": 9884,
        "Kaus Australis": 90185,
        "Kochab": 72607,
        "Markab": 113963,
        "Menkent": 68933,
        "Merak": 53910,
        "Miaplacidus": 45238,
        "Mirach": 5447,
        "Mirfak": 15863,
        "Nunki": 92855,
        "Peacock": 100751,
        "Polaris": 11767,
        "Pollux": 37826,
        "Procyon": 37279,
        "Rasalhague": 86032,
        "Regulus": 49669,
        "Rigel": 24436,
        "Rigel Kent": 71683,
        "RigilKentaurus": 71683,
        "Sabik": 84012,
        "Schedar": 3179,
        "Shaula": 85927,
        "Sirius": 32349,
        "Spica": 65474,
        "Suhail": 44816,
        "Vega": 91262,
        "Zubenelgenubi": 72622,
    }
    return planets, df, named_star_dict


# Celestial Body Selection Helper
def select_celestial_body(body_name, planets, df, named_star_dict):
    body_mappings = {
        "SunLL": "Sun",
        "SunUL": "Sun",
        "MoonLL": "Moon",
        "MoonUL": "Moon",
        "Mars": "Mars",
        "Venus": "Venus",
        "Jupiter": "Jupiter Barycenter",  # Barycenter for Jupiter
        "Saturn": "Saturn Barycenter",  # Barycenter for Saturn
        "Uranus": "Uranus Barycenter",  # Barycenter for Uranus
        "Mercury": "Mercury",
    }

    # Check if the body is a planet or its barycenter
    if body_name in body_mappings:
        return planets[body_mappings[body_name]]

    # Check if the body is a named star
    star_id = named_star_dict.get(body_name)
    if star_id is not None:
        return Star.from_dataframe(df.loc[star_id])

    # Return None if no valid celestial body is found
    return None


class BodyValidator(Validator):
    def __init__(self, named_star_dict):
        self.valid_bodies = [
            "SunLL",
            "SunUL",
            "MoonLL",
            "MoonUL",
            "Mars",
            "Venus",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Mercury",
        ] + list(named_star_dict.keys())

    def validate(self, document):
        text = document.text
        if text not in self.valid_bodies:
            raise ValidationError(
                message="Please enter a valid body", cursor_position=len(text)
            )


class EphemerisCalculator:
    def __init__(
        self,
        year,
        month,
        day,
        hour,
        minute,
        second,
        body,
        latitude,
        longitude,
        planets,
        df,
        named_star_dict,
    ):
        self.body = body
        self.latitude = latitude
        self.longitude = longitude
        self.planets = planets
        self.df = df
        self.named_star_dict = named_star_dict

        ts = load.timescale()
        self.datetime = dt.datetime(
            year, month, day, hour, minute, second, tzinfo=dt.timezone.utc
        )
        self.t = ts.utc(self.datetime)

    def compute_gha_dec(self):
        celestial_body = select_celestial_body(
            self.body, self.planets, self.df, self.named_star_dict
        )
        if not celestial_body:
            print(f"Unknown celestial body: {self.body}")
            return

        position = self.planets["Earth"] + Topos(
            latitude_degrees=self.latitude, longitude_degrees=self.longitude
        )
        astro = position.at(self.t).observe(celestial_body).apparent()

        alt, az, distance = astro.altaz()
        ra, dec, _ = astro.radec(epoch="date")
        gha = (self.t.gast - ra.hours) * 15 % 360
        ghaa = self.t.gast * 15

        print(
            f"{self.body} at {self.datetime} in position {self.latitude}, {self.longitude}"
        )
        print(
            tabulate.tabulate(
                [
                    ["GHA", f"{gha}°"],
                    ["DEC", f"{dec}"],
                    ["GHAa", f"{ghaa}°"],
                    ["RA", f"{ra}"],
                    ["ALT", f"{alt}"],
                    ["AZ", f"{az}"],
                    ["DIST", f"{distance.au:.2f} AU"],
                ]
            )
        )


def get_user_input(named_star_dict):
    # Define the prompt toolkit completer and validator
    body_completer = WordCompleter(
        [
            "SunLL",
            "SunUL",
            "MoonLL",
            "MoonUL",
            "Mars",
            "Venus",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Mercury",
        ]
        + list(named_star_dict.keys()),
        ignore_case=True,
    )
    body_validator = BodyValidator(named_star_dict)

    # Get input from user
    body = prompt_toolkit.prompt(
        "Select Body: ", completer=body_completer, validator=body_validator
    )
    year = int(prompt_toolkit.prompt("Year: "))
    month = int(prompt_toolkit.prompt("Month: "))
    day = int(prompt_toolkit.prompt("Day: "))
    hour = int(prompt_toolkit.prompt("Hour: "))
    minute = int(prompt_toolkit.prompt("Minute: "))
    second = int(prompt_toolkit.prompt("Second: "))
    latitude = float(prompt_toolkit.prompt("Latitude: "))
    longitude = float(prompt_toolkit.prompt("Longitude: "))

    return year, month, day, hour, minute, second, body, latitude, longitude


def main():
    planets, df, named_star_dict = load_data_and_stars()

    # Get user input
    year, month, day, hour, minute, second, body, latitude, longitude = get_user_input(
        named_star_dict
    )

    # Create EphemerisCalculator instance and compute
    calculator = EphemerisCalculator(
        year,
        month,
        day,
        hour,
        minute,
        second,
        body,
        latitude,
        longitude,
        planets,
        df,
        named_star_dict,
    )
    calculator.compute_gha_dec()


if __name__ == "__main__":
    main()
