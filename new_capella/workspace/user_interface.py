from celestial_navigation import CelestialNavigation, Observation

class UserInterface:
    def __init__(self):
        self.navigation = CelestialNavigation()

    def display_position(self, position):
        # Display the calculated position on the web UI
        pass

    def display_statistics(self, statistics):
        # Display the calculated statistics on the web UI
        pass

    def handle_observation(self, observation_data):
        # Parse the observation data and create an Observation object
        observation = Observation(
            altitude=observation_data['altitude'],
            azimuth=observation_data['azimuth'],
            timestamp=observation_data['timestamp']
        )

        # Perform celestial navigation calculations
        position = self.navigation.calculate_position([observation])

        # Perform statistical calculations for greater accuracy
        statistics = self.navigation.calculate_statistics([observation])

        # Display the results on the web UI
        self.display_position(position)
        self.display_statistics(statistics)
