# a simpel pixelflut client

import socket
from venv import create
from PIL import Image
import random
# import threading
from multiprocessing import Process
import os

# get a image and convert it to a random list of pixels
def getpixels(imagepath, screensize, center=False, fill=False):
    image = Image.open(imagepath)
    # check if it is a image
    if image.format == None:
        print('not a image')
        return
    canvas = (200, 200)
    if fill:
        canvas = screensize
        offset = (0, 0)
    else:
        if center:
            offset = (int(((screensize[0] / 2) - canvas[0])), int(((screensize[1]) / 2) - canvas[1]))
        else:
            offset = (random.randint(0, screensize[0] - canvas[0]), random.randint(0, screensize[1] - canvas[1]))
            # offset = (200, 150)
    # screensize = (800, 600)
    resized_image = image.resize(canvas)
    pix = resized_image.convert('RGB').load()
    pixels = []
    for x in range(canvas[0]):
        for y in range(canvas[1]):
            r, g, b = pix[x,y]
            # pixels.append((x, y, r, g, b))
            pixels.append((x+offset[0], y+offset[1], r, g, b))
    # randomize the list
    random.shuffle(pixels)
    return pixels

def strings(pixels):
    # make a list of strings to send
    lines = []
    for pixel in pixels:
        line = "PX %s %s %s%s%sff\n" % (pixel[0], pixel[1], '%0*x' % (2,pixel[2]), '%0*x' % (2,pixel[3]), '%0*x' % (2,pixel[4]))
        lines.append(line)
    return lines

def connect(server_address, port):
    # Create a TCP/IP socket to a ip and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_address = ('') # ip
    # port = 1234
    server_address = (server_address, port)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    print('connected')
    return sock

def send_thread(lines, server_address, port):
    # connect to server
    sock = connect(server_address, port)
    # prepare to send by generating a string and encoding it
    data = ''.join(lines).encode()
    # send data in a loop
    while True:
        sock.sendall(data)


# main function
def main():
    # get image and server address from config file
    config = open('config.txt', 'r')
    imagepath = config.readline().strip()
    server_address = config.readline().strip()
    port = int(config.readline().strip())
    multicon = int(config.readline().strip())
    screenx = int(config.readline().strip())
    screeny = int(config.readline().strip())
    centering = int(config.readline().strip())
    fill = int(config.readline().strip())
    config.close()
    screensize = (screenx, screeny)
    # get pixels from image
    pixels = getpixels(imagepath, screensize, centering, fill)
    # make a list of strings to send
    lines = strings(pixels)

    # if multicon is not 0, connect to server multicon times in seperate proseses, starting each thread with a random offset
    if multicon != 0:
        for i in range(multicon):
            # random number between 0 and number of lines
            offset = (random.randint(0, len(lines)))
            # start thread with offset
            # create new list with offset and reapeat the skipped lines at the end
            newlines = lines[offset:] + lines[:offset]
            # threading.Thread(target=send_thread, args=(newlines, server_address, port)).start()
            Process(target=send_thread, args=(newlines, server_address, port)).start()

if __name__ == "__main__":
    main()
