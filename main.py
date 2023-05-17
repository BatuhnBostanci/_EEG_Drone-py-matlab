import lib.pyxdf as pyxdf
import os
import logging

from threading import Thread

from lib.tello import Tello
from tkinter import *

import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.WARNING)  # Use logging.INFO to reduce output.
#print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'signalone.xdf')))

fname = "signalone.xdf"
data, header = pyxdf.load_xdf(fname)

print("Found {} data:".format(len(data)))
for ix, stream in enumerate(data):
    print(data)
    print("Stream {}: {} - type {} - uid {} - shape {} at {} Hz (effective {} Hz)".format(
        ix + 1, stream['info']['name'][0],
        stream['info']['type'][0],
        stream['info']['uid'][0],
        (int(stream['info']['channel_count'][0]), len(stream['time_stamps'])),
        stream['info']['nominal_srate'][0],
        stream['info']['effective_srate'])
    )
    if any(stream['time_stamps']):
        print("\tDuration: {} s".format(
            stream['time_stamps'][-1] - stream['time_stamps'][0]))
print("Done.")

def plotThread():
    for stream in data:
        y = stream['time_series']

        if isinstance(y, list):
            # list of strings, draw one vertical line for each marker
            for timestamp, marker in zip(stream['time_stamps'], y):
                plt.axvline(x=timestamp)
                print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
        elif isinstance(y, np.ndarray):
            # numeric data, draw as lines
            plt.plot(stream['time_stamps'], y)
        else:
            raise RuntimeError('Unknown stream format')

    plt.show()


def telloThread():
    from lib.tello import Tello
    class UnitTestGUI:
        def __init__( self, master ):
            d, a = '20', '1'
            root.geometry("800x400")
            root.title('Tello Drone Control')
            root.resizable(width=False, height=False)

            tello = Tello()

            self.frame0 = Frame(root, width=800, height=10)
            self.frame_scale = Frame(root)

            self.frame12 = Frame(root)
            self.frame1 = Frame(self.frame12)
            self.frame2 = Frame(self.frame12)

            self.frame_flip = Frame(root)

            self.button_command = Button(self.frame0, text='command', width=10, command=lambda: tello.send_command('command')).grid(row=0, column=0, padx=90, pady=10)
            self.button_takeoff = Button(self.frame0, text='takeoff', width=10, command=lambda: Tello.send_command('takeoff')).grid(row=0, column=1, padx=90, pady=10)
            self.button_land = Button(self.frame0, text='land', width=10, command=lambda: tello.send_command('land')).grid(row=0, column=2, padx=90, pady=10)

            # buttons to control flying forward, back, left and right
            self.button_forward = Button(self.frame1, text='forward', height=1, width=8, command=lambda: tello.send_command('forward ' + d)).grid(row=0, column=1)
            self.button_back = Button(self.frame1, text='back', height=1, width=8, command=lambda: tello.send_command('back ' + d)).grid(row=2, column=1)
            self.button_left = Button(self.frame1, text='left', height=1, width=8, command=lambda: tello.send_command('left ' + d)).grid(row=1, column=0)
            self.button_right = Button(self.frame1, text='right', height=1, width=8, command=lambda: tello.send_command('right ' + d)).grid(row=1, column=2)

            # buttons to control flying up, down, spin left and spin right
            self.button_up = Button(self.frame2, text='up', height=1, width=8, command=lambda: tello.send_command('up ' + d)).grid(row=0, column=1)
            self.button_down = Button(self.frame2, text='down', height=1, width=8, command=lambda: tello.send_command('down ' + d)).grid(row=2, column=1)
            self.button_spinleft = Button(self.frame2, text='spin left', height=1, width=8, command=lambda: tello.send_command('cw ' + a)).grid(row=1, column=0)
            self.button_spinright = Button(self.frame2, text='spin right', height=1, width=8, command=lambda: tello.send_command('ccw ' + a)).grid(row=1, column=2)

            # buttons to control flipping forward, back, left and right
            self.button_flip_f = Button(self.frame_flip, text='flip forward', height=1, width=10, command=lambda: tello.send_command('flip f')).grid(row=0, column=1)
            self.button_flip_b = Button(self.frame_flip, text='flip back', height=1, width=10, command=lambda: tello.send_command('flip b')).grid(row=2, column=1)
            self.button_flip_l = Button(self.frame_flip, text='flip left', height=1, width=10, command=lambda: tello.send_command('flip l')).grid(row=1, column=0)
            self.button_flip_r = Button(self.frame_flip, text='flip right', height=1, width=10, command=lambda: tello.send_command('flip r')).grid(row=1, column=2)

            # scrollbar to set the angle to rotate
            self.angle_change = Scale(self.frame_scale, from_=1, to=360, orient=HORIZONTAL, tickinterval=60, resolution=1, length=200)
            self.angle_change.grid(row=0, column=1, padx=95)

            self.angle = Button(self.frame_scale, text='angle confirm', padx=4, command=self.angle_change)
            self.angle.grid(row=1, column=1)

            # scrollbar to set the distance to fly
            self.distance_change = Scale(self.frame_scale, from_=20, to=500, orient=HORIZONTAL, tickinterval=100, resolution=10, length=200)
            self.distance_change.grid(row=0, column=0, padx=95)

            self.distance = Button(self.frame_scale, text='distance confirm', padx=4, command=self.speed_change)
            self.distance.grid(row=1, column=0)

            self.frame0.pack()
            self.frame_scale.pack(pady=20)
            self.frame1.grid(row=0, column=0, padx=80)
            self.frame2.grid(row=0, column=1, padx=80)
            self.frame12.pack(pady=0)
            self.frame_flip.pack(pady=30)

        def speed_change(self):
            a = str(self.angle_change.get())
            print('rotate angle set: ', a)

        def speed_change(self):
            d = str(self.distance_change.get())
            print('flying distance set: ', d)

    root = Tk()
    gui = UnitTestGUI( root )
    root.mainloop()


if __name__ == "__main__":
    Thread1 = Thread(target=plotThread, args=()).start()
    Thread2 = Thread(target=telloThread, args=()).start()
