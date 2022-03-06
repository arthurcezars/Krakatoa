import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECOND = 5

NUMERATOR, DENOMINATOR = spl.A_weighting(RATE)

p = pyaudio.PyAudio()


#Alterar o parametro 'input_device_index' para trocar de qual fonte é 
#gravado o som, se deixar vazio pega da fonte padrão do equipamento.
#Em notebooks é o microfone da webcam.
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                frames_per_buffer=CHUNK, input_device_index=2)

def is_meaningful(old, new):
    return abs(old - new) > 3

def listen(old=0, error_count=0, min_decibel=100, max_decibel=0):
    print('Escutando...')
    while True:
        try:
            block = stream.read(CHUNK)
        except IOError as e:
            error_count += 1
            print(" (%d) Error recording: %s" % (error_count, e))
        else:
            decoded_block = numpy.fromstring(block, numpy.int16)

            y = lfilter(NUMERATOR, DENOMINATOR, decoded_block)
            new_decibel = 20 * numpy.log10(spl.rms_flat(y))
            if is_meaningful(old=old, new=new_decibel):
                old = new_decibel
                print('A-wighted: {:+.2f} dB'.format(new_decibel))

if __name__ == '__main__':
    print('Iniciando o programa')
    listen()