Based on the requirements, here are the core classes, functions, and methods that will be necessary for the web version of new_capella:

1. `CelestialNavigation`: This class will handle the celestial navigation calculations and statistics.

   - `calculate_position`: Method to calculate the position based on celestial observations.
   - `calculate_statistics`: Method to calculate statistics for greater accuracy.

2. `Observation`: This class will represent a single celestial observation.

   - `altitude`: The altitude of the celestial body.
   - `azimuth`: The azimuth of the celestial body.
   - `timestamp`: The timestamp of the observation.

3. `UserInterface`: This class will handle the web user interface.

   - `display_position`: Method to display the calculated position on the UI.
   - `display_statistics`: Method to display the calculated statistics on the UI.
   - `handle_observation`: Method to handle user input of celestial observations.

Now, let's proceed with creating the necessary files and their contents.

1. `celestial_navigation.py`

