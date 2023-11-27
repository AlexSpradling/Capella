sudo apt-get update
sudo apt-get install python3

python3 -m venv myenv
source myenv/bin/activate

pip install dataclasses

touch celestial_navigation.py
touch user_interface.py
touch app.py

python app.py
