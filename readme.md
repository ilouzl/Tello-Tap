## Tello-Tap Controller

Use your [Tap Strap](www.tapwithus.com) as a flight controller for DJI Tello!

Prerequisites:
1. A **Tap Strap 2** with the latest FW and with "Developer Mode" enabled on TapManager App.
2. A DJI Tello drone...

Installation:
1. Clone this repo ```git clone https://github.com/ilouzl/Tello-Tap.git```
2. Create a virtual environment 
    ``` shell
    cd Tello-Tap
    virtualenv env
    source env/bin/activate
    ```
3. Install required packages ```pip install -r requirements.txt```

Usage:
1. Pair Tap with your machine.
2. Connect your machine to Tello's Wifi (SSID: TELLO-XXXXX) 
3. Run controller app ```python src/controller.py```

Controls:
1. TBD



References:
* DJI Tello [SDK](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
* Tap Strap [Python SDK](https://github.com/tapwithus/tap-python-sdk)
* Easytello [Python package](https://github.com/Virodroid/easyTello)