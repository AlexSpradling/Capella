import re


class InputChecking:
    """Class for checking input data"""

    def __init__(self, master):
        """Initializes the class"""
        self.master = master

    def check_time_format(x) -> bool:
        """Checks for hh:mm:ss format"""
        import re

        pattern = r"^([0-1]?\d|2[0-3])(?::([0-5]?\d))?(?::([0-5]?\d))?$"
        match = re.search(pattern, x)
        if match:
            return True
        else:
            return False

    def check_date_format(x) -> bool:
        """Checks for yyyy-mm-dd format"""
        import re

        pattern = r"^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))$"
        match = re.search(pattern, x)
        if match:
            return True
        else:
            return False

    def check_hs_format(x) -> bool:
        """Checks for dd-mm.t format"""
        pattern = r"^([0-8][0-9]|89)+-(0?[0-9]|[1-5][0-9])\.\d"
        match = re.search(pattern, x)
        if match:
            return True
        else:
            return False

    def check_lat_format(x) -> bool:
        """Checks for dd-mm.t-N/S format"""
        pattern = r"^([0-8][0-9]|89)+-(0?[0-9]|[1-5][0-9])\.\d-[N|S]+"
        match = re.search(pattern, x)
        if match:
            return True
        else:
            return False

    def check_long_format(x) -> bool:
        """Checks for ddd-mm.t-E/W format"""
        pattern = r"^([0-1][0-9][0-9]|179)+-(0?[0-9]|[1-5][0-9])\.\d-[W|E]+"
        match = re.search(pattern, x)
        if match:
            return True
        else:
            return False

    def validate_number(x) -> bool:
        """Validates that the input is a number"""
        if x.strip("-").replace(".", "").isdigit():
            return True
        elif x == "":
            return True
        else:
            return False

    def check_celestial_body(x) -> bool:
        """Checks that the body is in the list of celestial bodies"""

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

        planets = [
            "SunLL",
            "SunUL",
            "MoonLL",
            "MoonUL" "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
        ]
        if x in named_star_dict.keys() or x in planets:
            return True
        else:
            return False
