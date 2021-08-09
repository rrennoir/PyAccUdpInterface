import datetime
import time
import socket
from multiprocessing.connection import Connection
import queue
from multiprocessing import Process, Queue, Pipe
from enum import Enum
from copy import deepcopy

import struct
import sys


class Cursor:

    def __init__(self, byte: bytes):
        self._cursor = 0
        self._byte_array = byte

    def read_u8(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 1]
        self._cursor += 1

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_u16(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 2]
        self._cursor += 2

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_u32(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 4]
        self._cursor += 4

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_i8(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 1]
        self._cursor += 1

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_i16(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 2]
        self._cursor += 2

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_i32(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 4]
        self._cursor += 4

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_f32(self) -> float:

        data = self._byte_array[self._cursor: self._cursor + 4]
        self._cursor += 4

        return struct.unpack("<f", data)[0]

    def read_string(self) -> str:

        lenght = self.read_u16()

        string = self._byte_array[self._cursor: self._cursor + lenght]
        self._cursor += lenght

        # ACC doesn't support unicode emoji (and maybe orther
        # unicode charactere)
        # so if an emoji is in a name it put garbage bytes...
        # 6 bytes of trash idk why, so I ingore them
        return string.decode("utf-8", errors="ignore")


class ByteWriter:

    def __init__(self) -> None:
        self.bytes_array = b""

    def write_u8(self, data: int) -> None:
        self.bytes_array += (data).to_bytes(1, sys.byteorder, signed=False)

    def write_u16(self, data: int) -> None:
        self.bytes_array += (data).to_bytes(2, sys.byteorder, signed=False)

    def write_u32(self, data: int) -> None:
        self.bytes_array += (data).to_bytes(4, sys.byteorder, signed=False)

    def write_i16(self, data: int) -> None:
        self.bytes_array += (data).to_bytes(2, sys.byteorder, signed=True)

    def write_i32(self, data: int) -> None:
        self.bytes_array += (data).to_bytes(4, sys.byteorder, signed=True)

    def write_f32(self, data: float) -> None:
        self.bytes_array += struct.pack("<f", data)[0]

    def write_str(self, data: str) -> None:
        # ACC does support unicode emoji but I do, hehe 😀
        byte_data = data.encode("utf-8")
        self.write_u16(len(byte_data))
        self.bytes_array += byte_data

    def get_bytes(self) -> bytes:
        return self.bytes_array


class Nationality(Enum):

    Any = 0
    Italy = 1
    Germany = 2
    France = 3
    Spain = 4
    GreatBritain = 5
    Hungary = 6
    Belgium = 7
    Switzerland = 8
    Austria = 9
    Russia = 10
    Thailand = 11
    Netherlands = 12
    Poland = 13
    Argentina = 14
    Monaco = 15
    Ireland = 16
    Brazil = 17
    SouthAfrica = 18
    PuertoRico = 19
    Slovakia = 20
    Oman = 21
    Greece = 22
    SaudiArabia = 23
    Norway = 24
    Turkey = 25
    SouthKorea = 26
    Lebanon = 27
    Armenia = 28
    Mexico = 29
    Sweden = 30
    Finland = 31
    Denmark = 32
    Croatia = 33
    Canada = 34
    China = 35
    Portugal = 36
    Singapore = 37
    Indonesia = 38
    USA = 39
    NewZealand = 40
    Australia = 41
    SanMarino = 42
    UAE = 43
    Luxembourg = 44
    Kuwait = 45
    HongKong = 46
    Colombia = 47
    Japan = 48
    Andorra = 49
    Azerbaijan = 50
    Bulgaria = 51
    Cuba = 52
    CzechRepublic = 53
    Estonia = 54
    Georgia = 55
    India = 56
    Israel = 57
    Jamaica = 58
    Latvia = 59
    Lithuania = 60
    Macau = 61
    Malaysia = 62
    Nepal = 63
    NewCaledonia = 64
    Nigeria = 65
    NorthernIreland = 66
    PapuaNewGuinea = 67
    Philippines = 68
    Qatar = 69
    Romania = 70
    Scotland = 71
    Serbia = 72
    Slovenia = 73
    Taiwan = 74
    Ukraine = 75
    Venezuela = 76
    Wales = 77
    Iran = 78
    Bahrain = 79
    Zimbabwe = 80
    ChineseTaipie = 81
    Chile = 82
    Uruguay = 83
    Madagascar = 84
    placeholder2 = 85
    placeholder3 = 86
    placeholder4 = 87
    placeholder5 = 88
    placeholder6 = 89
    placeholder7 = 90


class CarLocation(Enum):

    NONE = 0
    Track = 1
    Pitlane = 2
    PitEntry = 3
    PitExit = 4


class DriverCategory(Enum):

    bronze = 0
    Silver = 1
    Gold = 2
    Platium = 3


class CupCategory(Enum):

    Pro = 0
    ProAm = 1
    Am = 2
    Silver = 3
    National = 4


class SessionType(Enum):

    Practice = 0
    Qualifying = 4
    Superpole = 9
    Race = 10
    Hotlap = 11
    Hotstint = 12
    HotlapSuperpole = 13
    Replay = 14
    NONE = 15


class SessionPhase(Enum):

    NONE = 0
    Starting = 1
    PreFormation = 2
    FormationLap = 3
    PreSession = 4
    Session = 5
    SessionOver = 6
    PostSession = 7
    ResultUI = 8


class LapType(Enum):

    ERROR = 0
    OutLap = 1
    Regular = 2
    InLap = 3


class LapInfo:

    def __init__(self, cur: Cursor):

        self.lap_time_ms = cur.read_u32()
        self.car_index = cur.read_u16()
        self.driver_index = cur.read_u16()

        split_count = cur.read_u8()
        self.splits = []
        for _ in range(split_count):
            self.splits.append(cur.read_i32())

        self.is_invalid = cur.read_u8() > 0
        self.is_valid_for_best = cur.read_u8() > 0

        is_out_lap = cur.read_u8() > 0
        is_in_lap = cur.read_u8() > 0

        if is_out_lap:
            self.late_type = LapType.OutLap

        elif is_in_lap:
            self.late_type = LapType.InLap

        else:
            self.late_type = LapType.Regular

        for i, split in enumerate(self.splits):
            if split == 2147483647:  # Max int32 value
                self.splits[i] = 0

        if self.lap_time_ms == 2147483647:
            self.lap_time_ms = 0

        self._cur = cur

    def get_cur(self):
        cur = self._cur
        self._cur = None
        return cur


class Registration:

    def __init__(self):

        self.connection_id = -1
        self.connection_succes = False
        self.is_read_only = False
        self.error_msg = "Not Initialized yet"

    def update(self, cur: Cursor):

        self.connection_id = cur.read_i32()
        self.connection_succes = cur.read_u8() > 0
        self.is_read_only = cur.read_u8() == 0
        self.error_msg = cur.read_string()


class RealTimeUpdate:

    def __init__(self):
        self.event_index = -1
        self.session_index = -1
        self.session_type = SessionType.NONE
        self.phase = SessionPhase.NONE

        self.session_time = datetime.datetime.fromtimestamp(0)
        self.session_end_time = datetime.datetime.fromtimestamp(0)

        self.focused_car_index = -1
        self.active_camera_set = ""
        self.active_camera = ""
        self.current_hud_page = ""
        self.is_replay_playing = False
        self.replay_session_time = datetime.datetime.fromtimestamp(0)
        self.replay_remaining_time = datetime.datetime.fromtimestamp(0)

        self.time_of_day = datetime.datetime.fromtimestamp(0)
        self.ambient_temp = -1
        self.track_temp = -1
        self.best_session_lap = None

    def update(self, cur: Cursor):

        self.event_index = cur.read_u16()
        self.session_index = cur.read_u16()
        self.session_type = SessionType(cur.read_u8())
        self.phase = SessionPhase(cur.read_u8())

        session_time = cur.read_f32() // 1000
        if session_time == -1:
            # -1 means there is no time limit
            session_time = 0

        self.session_time = datetime.datetime.fromtimestamp(session_time)

        session_end_time = cur.read_f32() // 1000
        if session_end_time == -1:
            # -1 means there is no time limit
            session_end_time = 0

        self.session_end_time = datetime.datetime.fromtimestamp(
            session_end_time)

        self.focused_car_index = cur.read_i32()
        self.active_camera_set = cur.read_string()
        self.active_camera = cur.read_string()
        self.current_hud_page = cur.read_string()
        self.is_replay_playing = cur.read_u8() > 0
        self.replay_session_time = datetime.datetime.fromtimestamp(0)
        self.replay_remaining_time = datetime.datetime.fromtimestamp(0)

        if self.is_replay_playing:

            replay_session_time = cur.read_f32() // 1000
            if replay_session_time != -1:
                # -1 means there is no time limit
                self.replay_session_time = datetime.datetime.fromtimestamp(
                    replay_session_time)

            replay_remaining_time = cur.read_f32() // 1000
            if replay_remaining_time != -1:
                # -1 means there is no time limit
                self.replay_remaining_time = datetime.datetime.fromtimestamp(
                    replay_remaining_time)

        self.time_of_day = datetime.datetime.fromtimestamp(
            cur.read_f32() / 1000)
        self.ambient_temp = cur.read_u8()
        self.track_temp = cur.read_u8()
        self.best_session_lap = LapInfo(cur)


class RealTimeCarUpdate:

    def __init__(self, cur: Cursor):

        self.car_index = cur.read_u16()
        self.driver_index = cur.read_u16()
        self.driver_count = cur.read_u8()
        self.gear = cur.read_u8()
        self.world_pos_x = cur.read_f32()
        self.world_pos_y = cur.read_f32()
        self.yaw = cur.read_f32()
        self.car_location = CarLocation(cur.read_u8())
        self.kmh = cur.read_u16()
        self.position = cur.read_u16()
        self.cup_position = cur.read_u16()
        self.track_position = cur.read_u16()
        self.spline_position = cur.read_f32()
        self.lap = cur.read_u16()
        self.delta = cur.read_i32()
        self.best_session_lap = LapInfo(cur)
        cur = self.best_session_lap.get_cur()
        self.last_lap = LapInfo(cur)
        cur = self.last_lap.get_cur()
        self.current_lap = LapInfo(cur)


class TrackData:

    def __init__(self):

        self.track_name = ""
        self.track_id = -1
        self.track_meters = -1

        self.camera_sets = {}
        self.hud_page = []

    def update(self, cur: Cursor):

        _ = cur.read_i32()  # Connection id
        self.track_name = cur.read_string()
        self.track_id = cur.read_i32()
        self.track_meters = cur.read_i32()

        self.camera_sets = {}
        camera_set_count = cur.read_u8()
        for _ in range(camera_set_count):

            camera_set_name = cur.read_string()
            self.camera_sets.update({camera_set_name: []})

            camera_count = cur.read_u8()
            for _ in range(camera_count):
                camera_name = cur.read_string()
                self.camera_sets[camera_set_name].append(camera_name)

        self.hud_page = []
        hud_page_count = cur.read_u8()
        for _ in range(hud_page_count):
            self.hud_page.append(cur.read_string())


class CarInfo:

    def __init__(self, car_index: int):

        self.car_index = car_index
        self.model_type = -1
        self.team_name = ""
        self.race_number = -1
        self.cup_category = CupCategory.National
        self.current_driver_index = -1
        self.drivers = []
        self.nationality = Nationality.Any

    def update(self, cur: Cursor):

        self.model_type = cur.read_u8()
        self.team_name = cur.read_string()
        self.race_number = cur.read_i32()
        self.cup_category = CupCategory(cur.read_u8())
        self.current_driver_index = cur.read_u8()
        self.nationality = Nationality(cur.read_u16())

        self.drivers.clear()
        driver_count = cur.read_u8()
        for _ in range(driver_count):

            driver = DriverInfo(cur)
            cur = driver.get_cur()
            self.drivers.append(driver)

    def __str__(self) -> str:

        return (f"ID: {self.car_index} Team: {self.team_name} "
                "N°: {self.race_number}")


class EntryList:

    def __init__(self):

        self.entry_list = []

    def update(self, cur: Cursor):

        self.entry_list = []

        _ = cur.read_i32()  # Connection id
        car_entry_count = cur.read_u16()
        for _ in range(car_entry_count):
            self.entry_list.append(CarInfo(cur.read_u16()))

    def update_car(self, cur: Cursor):
        car_id = cur.read_u16()

        car_info = None
        for car in self.entry_list:
            if car.car_index == car_id:
                car_info = car

        if car_info:
            car_info.update(cur)


class DriverInfo:

    def __init__(self, cur: Cursor):
        self.first_name = cur.read_string()
        self.last_name = cur.read_string()
        self.short_name = cur.read_string()
        self.category = DriverCategory(cur.read_u8())
        self.nationality = Nationality(cur.read_u16())

        self._cur = cur

    def get_cur(self) -> Cursor:
        cur = self._cur
        self._cur = None
        return cur

    def __str__(self) -> str:

        return f"Name: {self.first_name} {self.last_name}"


class accUpdInterface:

    def __init__(self, ip, port, instance_info):

        self.registration = Registration()
        self.session = RealTimeUpdate()
        self.track = TrackData()
        self.entry_list = EntryList()
        self.connected = False

        self._name = instance_info["name"]
        self._psw = instance_info["password"]
        self._speed = instance_info["speed"]
        self._cmd_psw = instance_info["cmd_password"]

        self._udp_data = {
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

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("", 3400))

        self._ip = ip
        self._port = port
        self._last_time_requested = datetime.datetime.now()
        self._last_connection = datetime.datetime.now()

        self.child_pipe, self.parent_pipe = Pipe()
        self.data_queue = Queue()
        self.udp_interface_listener = Process(
            target=self.listen_udp_interface, args=(self.child_pipe, self.data_queue))

    @property
    def udp_data(self):
        self.parent_pipe.send("DATA_REQUEST")
        if self.parent_pipe.recv() == "DATA_OK":
            try:
                return self.data_queue.get_nowait()

            except(queue.Empty):
                # idk return None
                return None

    def listen_udp_interface(self, child_pipe: Connection, data_queue: Queue):

        self.connect()

        message = ""
        while message != "STOP_PROCESS":

            if child_pipe.poll():
                message = child_pipe.recv()

            now = datetime.datetime.now()
            # if connection was lost or not established wait 2s before asking again
            if (not self.connected and (now - self._last_connection).total_seconds() > 2):
                self.connect()
                self._last_connection = datetime.datetime.now()

            else:
                self.update()

            if message == "DATA_REQUEST":
                data_queue.put(deepcopy(self._udp_data))
                child_pipe.send("DATA_OK")
                message = ""

        self.disconnect()
        self._socket.close()
        child_pipe.send("PROCESS_TERMINATED")
        print("[ASM_Reader]: Process Terminated.")

    def start(self):

        print("[pyUIL] Listening to the UDP interface...")
        self.udp_interface_listener.start()

    def stop(self):

        print("[pyUIL]: Sending stopping command to process...")
        self.parent_pipe.send("STOP_PROCESS")

        print("[pyUIL]: Waiting for process to finish...")
        if (self.parent_pipe.recv() == "PROCESS_TERMINATED"):
            # Need to empty the queue before joining process (qsize() isn't 100% accurate)
            while self.data_queue.qsize() != 0:
                try:
                    _ = self.data_queue.get_nowait()
                except queue.Empty:
                    pass
        else:
            print(
                "[pyUIL]: Received unexpected message, program might be deadlock now.")

        self.udp_interface_listener.join()

    def update(self):

        # Add timeout after 1s delay to no get stuck for ever
        self._socket.settimeout(1.0)

        data = None
        try:
            data, _ = self._socket.recvfrom(2048)

        except socket.error:
            self.connected = False
            self._udp_data["connection"]["connected"] = False

        except socket.timeout:
            self.connected = False
            self._udp_data["connection"]["connected"] = False

        finally:
            self._socket.settimeout(None)

        if data:

            cur = Cursor(data)
            packet_type = cur.read_u8()

            if packet_type == 1:
                self.registration.update(cur)

                info = self._udp_data["connection"]
                info["id"] = self.registration.connection_id
                info["connected"] = True

                self.request_track_data()
                self.request_entry_list()

            elif packet_type == 2:
                self.session.update(cur)
                self.update_leaderboard_session()

            elif packet_type == 3:
                car_update = RealTimeCarUpdate(cur)
                self.is_new_entry(car_update)

            elif packet_type == 4:
                self.entry_list.update(cur)
                self.add_to_leaderboard()

            elif packet_type == 5:
                self.track.update(cur)

            elif packet_type == 6:
                self.entry_list.update_car(cur)

            elif packet_type == 7:
                # Don't care (:
                pass

    def is_new_entry(self, car_update):

        is_unkown = True
        for car in self.entry_list.entry_list:
            if car_update.car_index == car.car_index:
                is_unkown = False

        last_request = datetime.datetime.now() - self._last_time_requested
        if is_unkown and last_request.total_seconds() >= 1:
            self.request_entry_list()
            self._last_time_requested = datetime.datetime.now()

        elif not is_unkown:
            self.update_leaderboard(car_update)

    def add_to_leaderboard(self) -> None:

        self._udp_data["entries"].clear()

        for entry in self.entry_list.entry_list:
            self._udp_data["entries"].update({entry.car_index: {}})

    def update_leaderboard(self, data: RealTimeCarUpdate) -> None:

        entry_list = self.entry_list.entry_list

        entry_index = -1
        for index, entry in enumerate(entry_list):
            if entry.car_index == data.car_index:
                entry_index = index

        if entry_index >= 0 and len(entry_list[entry_index].drivers) > 0:
            car_info = entry_list[entry_index]
            drivers = car_info.drivers

            race_number = car_info.race_number
            cup_category = car_info.cup_category
            model_type = car_info.model_type
            team_name = car_info.team_name
            first_name = drivers[data.driver_index].first_name
            last_name = drivers[data.driver_index].last_name

        else:
            race_number = -1
            cup_category = CupCategory.National
            model_type = -1
            team_name = "Team Name"
            first_name = "First Name"
            last_name = "Last Name"

        self._udp_data["entries"][data.car_index].update({
            "position": data.position,
            "car_number": race_number,
            "car_id": data.car_index,
            "cup_category": cup_category.name,
            "cup_position": data.cup_position,
            "manufacturer": model_type,
            "team": team_name,
            "driver": {
                "first_name": first_name,
                "last_name": last_name,
            },
            "lap": data.lap,
            "current_lap": data.current_lap.lap_time_ms,
            "last_lap": data.last_lap.lap_time_ms,
            "best_session_lap": data.best_session_lap.lap_time_ms,
            "sectors": data.last_lap.splits,
            "car_location": data.car_location.name,
            "world_pos_x": data.world_pos_x,
            "world_pos_y": data.world_pos_y
        })

    def update_leaderboard_session(self) -> None:

        session = self._udp_data["session"]
        session.clear()

        session["track"] = self.track.track_name
        session["session_type"] = self.session.session_type.name
        session["session_time"] = self.session.session_time
        session["session_end_time"] = self.session.session_end_time
        session["air_temp"] = self.session.ambient_temp
        session["track_temp"] = self.session.track_temp

    def connect(self) -> None:

        msg = ByteWriter()
        msg.write_u8(1)
        msg.write_u8(4)
        msg.write_str(self._name)
        msg.write_str(self._psw)
        msg.write_i32(self._speed)
        msg.write_str(self._cmd_psw)

        print(msg.get_bytes())

        self._socket.sendto(msg.get_bytes(), (self._ip, self._port))
        self.connected = True

    def disconnect(self) -> None:

        c_id = self.registration.connection_id

        msg = ByteWriter()
        msg.write_u8(9)
        msg.write_i32(c_id)

        self._socket.sendto(msg.get_bytes(), (self._ip, self._port))

    def request_entry_list(self) -> None:

        c_id = self.registration.connection_id

        if c_id != -1:

            msg = ByteWriter()
            msg.write_u8(10)
            msg.write_i32(c_id)

            self._socket.sendto(msg.get_bytes(), (self._ip, self._port))

    def request_track_data(self) -> None:

        c_id = self.registration.connection_id

        msg = ByteWriter()
        msg.write_u8(11)
        msg.write_i32(c_id)

        self._socket.sendto(msg.get_bytes(), (self._ip, self._port))


if __name__ == "__main__":

    # Test zone

    info = {
        "name": "Ryan Rennoir",
        "password": "asd",
        "speed": 250,
        "cmd_password": ""
    }

    aui = accUpdInterface("127.0.0.1", 9000, info)
    aui.start()

    now = time.time()
    while time.time() < now + 3:
        data = aui.udp_data
        if data:
            print(data["entries"])
    aui.stop()
