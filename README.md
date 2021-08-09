# PyAccSharedMemory

ACC UDP interface listner written in python 😀.

## Usage

Basic code example.

```py
    # Setup basic information
    info = {
        "name": "Ryan Rennoir",
        "password": "asd",
        "speed": 250,
        "cmd_password": ""
    }

    # Create UDP listener instance
    aui = accUpdInterface("127.0.0.1", 9000, info)

    aui.start()

    while condition:
        # Receive most latest data available
        data = aui.udp_data # Return a dict

    # Close listener process and socket
    aui.stop()
```

## Data structure

Dictionary containing 3 dictionaries, each one of them contains all the information available through the shared memory and have the same as the official documentation.

```py
{
    "connection": {
        "id": -1,
        "connected": False
    },
    "entries": {},
    "session": {
        "track": "None",
        "session_type": SessionType.NONE.name,
        "session_time": datetime.datetime.fromtimestamp(0),
        "session_end_time": datetime.datetime.fromtimestamp(0),
        "air_temp": 0,
        "track_temp": 0
    },
}
```