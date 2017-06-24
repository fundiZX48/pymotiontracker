"""OpenGL cube example for the Bluetooth MPU6050 device.
Copyright 2017 Mark Mitterdorfer

Track device rotational movement and display to screen in form of a 3D OpenGL cube.
"""

import sys
sys.path.insert(0, "../src")
import motiontracker

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np
import time

def cube():
    """Draw a basic cube.
    """

    glBegin(GL_QUADS)

    # Front face  (z = 1.0)
    glColor3f(1.0, 0.0, 0.0) # Red
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)

    # Back face (z = -1.0)
    glColor3f(1.0, 1.0, 0.0) # Yellow
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, -1.0)

    # Top face (y = 1.0)
    glColor3f(0.0, 1.0, 0.0) # Green
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(1.0, 1.0, 1.0)

    # Bottom face (y = -1.0)
    glColor3f(1.0, 0.5, 0.0) # Orange
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(1.0, -1.0, -1.0)

    # Left face (x = -1.0)
    glColor3f(0.0, 0.0, 1.0) # Blue
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, 1.0)

    # Right face (x = 1.0)
    glColor3f(1.0, 1.0, 1.0) # White
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, -1.0)

    glEnd()

def axes():
    """Draw coordinate axes.
    Red = Positive X direction
    White = Positive Y direction
    Blue = Positive Z direction
    """

    glLineWidth(3.0)
    glBegin(GL_LINES)
    # X
    glColor3f(1.0, 0.0, 0.0) # Red

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)

    # arrow
    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(1.5, 0.5, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(1.5, -0.5, 0.0)

    # Y
    glColor3f(1.0, 1.0, 1.0) # White

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    # arrow
    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(0.5, 1.5, 0.0)

    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(-0.5, 1.5, 0.0)

    # Z
    glColor3f(0.0, 0.0, 1.0) # Blue

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 2.0)

    # arrow
    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.0, 0.5, 1.5)

    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.0, -0.5, 1.5)
    glEnd()

def get_median_roll_pitch_yaw(motion_session):
    """Obtain the median roll, pitch and yaw values from the device at rest.
    These values will be used to calibrate the device i.e. centre the device.

    Args:
        motion_session (MotionTracker) : A MotionTracker open session
    Returns:
        tuple (float): Median X, Y, Z
    """

    ang_x = motion_session.ang_x
    ang_y = motion_session.ang_y
    ang_z = motion_session.ang_z

    stats = np.array([ang_x, ang_y, ang_z])

    for _ in range(0, 1000):
        ang_x = motion_session.ang_x
        ang_y = motion_session.ang_y
        ang_z = motion_session.ang_z
        data = np.array([ang_x, ang_y, ang_z])
        stats = np.vstack([stats, data])

    (median_ang_x, median_ang_y, median_ang_z) = np.median(stats, axis=0)
    return(median_ang_x, median_ang_y, median_ang_z)

def main():
    """Main.
    """

    pygame.init()
    display = (1024, 768)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("pymotiontracker - OpenGL cube")

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST) # Enable depth testing for Z culling
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glTranslated(0.0, 0.0, -5.0)

    # Start motion sensor
    motion_session = motiontracker.MotionTracker(bd_addr="20:16:09:21:48:81")
    motion_session.start_read_data()
    print("Calibrating, do not move Bluetooth module!")
    # Allow read values to "settle in"
    time.sleep(2)

    (median_ang_x, median_ang_y, median_ang_z) = get_median_roll_pitch_yaw(motion_session)

    # Obtain the offsets used for calibration, see below
    roll_offset = median_ang_x
    pitch_offset = median_ang_y
    yaw_offset = median_ang_z

    while True:
        ang_x = motion_session.ang_x
        ang_y = motion_session.ang_y
        ang_z = motion_session.ang_z

        # Zero centre the roll, pitch and yaw - i.e. calibrate device
        # May need to change signs from - to +, and + to - depending on mounted
        # orientation of Bluetooth device.
        roll = round(-(ang_x - roll_offset), 2)
        pitch = round(-(ang_y - pitch_offset), 2)
        yaw = round(+(ang_z - yaw_offset), 2)

        print("roll:", roll, "pitch:", pitch, "yaw:", yaw)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quitting ...")
                # Stop motion sensor
                motion_session.stop_read_data()
                pygame.quit()
                quit()

        glPushMatrix()

        # This is not strictly correct as roll should be on the X axis,
        # pitch on the Y axis and yaw on the Z axis. But since OpenGL is a
        # right handed coordinate system, I inverted the axes to suit our purpose
        # for a motion (head) tracking application
        glRotated(yaw, 0, 1, 0)
        glRotated(pitch, 1, 0, 0)
        glRotated(roll, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Draw the cube and axes
        cube()
        axes()
        pygame.display.flip()

        # Restore to original matrix state
        glPopMatrix()

if __name__ == "__main__":
    main()
