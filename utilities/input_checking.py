import re 

class InputChecking:
    """Class for checking input data"""

    def __init__(self, master):
        """Initializes the class"""
        self.master = master

    def check_time_format(x) -> bool:
        """Checks for hh:mm:ss format"""
        import re
        pattern = r'^([0-1]?\d|2[0-3])(?::([0-5]?\d))?(?::([0-5]?\d))?$'
        match = re.search(pattern, x)
        if match:

            return True
        else:
            return False

    def check_date_format(x) -> bool:
        """Checks for yyyy-mm-dd format"""
        import re

        pattern = r'^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))$'
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
        if x.strip('-').replace('.', '').isdigit():
            return True
        elif x == "":
            return True
        else:
            return False

