from user_interface import UserInterface

# Create an instance of the UserInterface class
ui = UserInterface()

# Example observation data
observation_data = {
    'altitude': 45.0,
    'azimuth': 180.0,
    'timestamp': '2022-01-01 12:00:00'
}

# Handle the observation
ui.handle_observation(observation_data)
