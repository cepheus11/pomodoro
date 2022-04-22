from ctypes import CDLL, Structure, byref, c_int, c_void_p, c_char_p, c_uint32, c_uint8
from ctypes.util import find_library
import wave

PA_STREAM_PLAYBACK = 1
PA_SAMPLE_S16LE = 3
BUFFER_SIZE = 2048
ERROR = 0


class PASampleSpec(Structure):
    __slots__ = [
        'format',
        'rate',
        'channels',
    ]


PASampleSpec._fields_ = [
    ('format', c_int),
    ('rate', c_uint32),
    ('channels', c_uint8),
]

pasimple = CDLL(find_library("pulse-simple"))
assert(pasimple is not None)

simple_new = pasimple.pa_simple_new
simple_new.argtypes = [c_char_p, c_char_p, c_int, c_char_p, c_char_p, c_void_p, c_void_p, c_void_p, c_int]
simple_new.restype = c_void_p

simple_write = pasimple.pa_simple_write
simple_write.argtypes = [c_void_p, c_char_p, c_int, c_void_p]
simple_write.restype = c_int

simple_drain = pasimple.pa_simple_drain
simple_drain.argtypes = [c_void_p, c_void_p]
simple_drain.restype = c_int

simple_free = pasimple.pa_simple_free
simple_free.argtypes = [c_void_p]

def play_wavefile(wavefile_path, app_name):
    wave_file = wave.open(wavefile_path)
    spec = PASampleSpec()
    spec.format = PA_SAMPLE_S16LE
    spec.rate = wave_file.getframerate()
    spec.channels = wave_file.getnchannels()


    stream = simple_new(None, bytes(wavefile_path, "UTF-8"), PA_STREAM_PLAYBACK, None, bytes(app_name, "UTF-8"), byref(spec), None, None, ERROR)

    while True:
        buffer = wave_file.readframes(BUFFER_SIZE)
        if len(buffer) == 0:
            break
        simple_write(stream, buffer, len(buffer), ERROR)

    wave_file.close()
    simple_drain(stream, ERROR)
    simple_free(stream)
