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
