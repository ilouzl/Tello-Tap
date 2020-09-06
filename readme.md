## Tello-Tap Controller

Use your [Tap Strap](www.tapwithus.com) as a flight controller for DJI Tello!


Installation:
1. Clone this repo ```git clone https://github.com/ilouzl/Tello-Tep```
2. Create a virtual environment 
    ``` shell
    cd Tello-Tap
    virtualenv env
    source env/bin/activate
    ```
3. Install required packages ```pip install -r requirements.txt```
4. Pair Tap with your machine (Make sure "Developer Mode" is enable for your Tap)
5. Connect your machine to Tello's Wifi (SSID: TELLO-XXXXX) 
6. Run controller app ```python main.py```

### Tello SDK
https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf