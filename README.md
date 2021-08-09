# PyAccUdpInterface

ACC UDP interface listener written in python 😀.

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

Kunos don't give any documentation on their udp interface except the code example they give and I'm too lazy to write one myself 😅

```py
{
    "connection": {
        "id": ...,
        "connected": ...
    },
    "entries": {},
    "session": {
        "track": "None",
        "session_type": ...,
        "session_time": ...,
        "session_end_time": ...,
        "air_temp": ...,
        "track_temp": ...
    },
}
```