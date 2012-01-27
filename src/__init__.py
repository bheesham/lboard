import sys
from time import time

from VideoCapture import Device
import cv2 as cv
from PIL import ImageEnhance, Image

import pygame
from pygame.locals import *

from functions import *

# Video resolution
vres = ( 640, 480 )

# Window size
wsize = ( 800, 600 )

# Set up the camera
cam                 = Device()
cam.setResolution( vres[0], vres[1] )
brightness          = 1.0
contrast            = 1.0

# Set up the main window
pygame.init()
screen              = pygame.display.set_mode( wsize )
pygame.display.set_caption( "lboard" )
pygame.font.init()
font                = pygame.font.SysFont( "Arial", 11 )

# Set some default values
C_WHITE             = ( 255, 255, 255 )     # Constant
C_BLACK             = ( 0, 0, 0 )           # Constant
C_BG                = ( 'Normal', 'Red', 'Green', 'Blue', 'Difference', 'Difference in Red', 'Difference in Green', 'Difference in Blue', 'Black' )

display_background  = 0
calibrated          = False
frame_count         = 0

imgRAW              = 0                     # The raw image from the webcam
imgCapture          = 0                     # The enhanced version from the webcam

imgOUT                  = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 3 )    # Converted image from the webcam (RGB)
imgOUT2                 = 0                                                 # The converted image NOT in OpenCV format 
imgConCAP               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 3 )    # Image to be displayed


imgRED              = [ 0, 0 ]              # Red Layers
imgGRE              = [ 0, 0 ]              # Green layers
imgBLU              = [ 0, 0 ]              # Blue layers
imgRED[1]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
imgGRE[1]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
imgBLU[1]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
imgRED[0]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
imgGRE[0]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
imgBLU[0]           = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )

imgREDDiff          = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 ) # The difference between the old and the new red frames
imgGREDiff          = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 ) # Old green, new green
imgBLUDiff          = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )

imgTM1              = 0 # Temporary images
imgTM2              = 0
imgTM3              = 0
imgTM4              = 0

imgREF              = 0                     # Our reference image (will be a few frames behind,
                                            # and then we'll take the difference between the two
                                            # then apply the colour filters to the image). 

imgPEN              = 0                     # Final image

while 1:
    # Hot keys and events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    keyinput = pygame.key.get_pressed()
    
    if( keyinput[K_q] ):        exit()                      # Quit
    
    if ( keyinput[K_1] ):       brightness          -= .1   # Brightness
    if ( keyinput[K_2] ):       brightness          += .1
    
    if ( keyinput[K_3] ):       contrast            -= .1   # Contrast
    if ( keyinput[K_4] ):       contrast            += .1
    
    if ( keyinput[K_b] ):                                   # Background
        display_background  += 1
        if ( display_background > 8 ):
            display_background = 0
    
    if ( keyinput[K_r] ):                                   # Reset calibration 
        display_background  = 0
        calibrated          = False
        frame_count         = 0
        
        imgRAW              = 0
        imgCapture          = 0
        
        imgOUT                  = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 3 )
        imgOUT2                 = 0
        imgConCAP               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 3 )
        
        imgRED[1]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgGRE[1]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgBLU[1]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgRED[0]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgGRE[0]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgBLU[0]               = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        
        imgREDDiff              = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgGREDiff              = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        imgBLUDiff              = cv.cv.CreateImage( wsize, cv.IPL_DEPTH_8U, 1 )
        
        imgTM1              = 0
        imgTM2              = 0
        imgTM3              = 0
        imgTM4              = 0
        
        imgREF              = 0
        imgPEN              = 0
    
    
    # Set this to true for now
    calibrated = True
    
    
    # Get the image from the webcam
    imgRAW                  = cam.getImage()                                                    # Get raw image from the webcam
    imgCapture              = ImageEnhance.Brightness( imgRAW ).enhance( brightness )           # Brightness
    imgCapture              = ImageEnhance.Contrast( imgCapture ).enhance( contrast )           # Contrast
    imgCapture              = imgCapture.transpose( Image.FLIP_LEFT_RIGHT ).resize( wsize )     # Flip and resize the image
    
    # Convert the image to a OpenCV compatible image (RGB)
    cv.cv.SetData( imgConCAP, imgCapture.tostring() )
    
    # Split up the different channels
    cv.cv.Split( imgConCAP, imgRED[1], imgBLU[1], imgGRE[1], None )
    
    # Get the difference between the old and the new frames
    if ( frame_count < 1 ) :
        cv.cv.Copy( imgRED[1], imgRED[0] )
        cv.cv.Copy( imgGRE[1], imgGRE[0] )
        cv.cv.Copy( imgBLU[1], imgBLU[0] )
    else:
        cv.cv.AbsDiff( imgRED[0], imgRED[1], imgREDDiff )
        cv.cv.AbsDiff( imgGRE[0], imgGRE[1], imgGREDiff )
        cv.cv.AbsDiff( imgBLU[0], imgBLU[1], imgBLUDiff )
    
    # Background Display
    screen.fill( C_BLACK )
    if ( display_background == 0 or calibrated == False or frame_count < 1 ):
        # Webcam output
        imgOUT2 = pygame.image.frombuffer( imgConCAP.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 1 ):
        # Red
        cv.cv.Merge( imgRED[1], None, None, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 2 ):
        # Green
        cv.cv.Merge( None, imgGRE[1], None, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 3 ):
        # Blue
        cv.cv.Merge( None, None, imgBLU[1], None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 4 ):
        # Differenced image
        cv.cv.Merge( imgREDDiff, imgGREDiff, imgBLUDiff, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 5 ):
        # Difference in Red
        cv.cv.Merge( imgREDDiff, None, None, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 6 ):
        # Difference in Green
        cv.cv.Merge( None, imgGREDiff, None, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    elif ( display_background == 7 ):
        # Difference in Blue
        cv.cv.Merge( None, None, imgBLUDiff, None, imgOUT )
        imgOUT2 = pygame.image.frombuffer( imgOUT.tostring(), wsize, "RGB" )
        screen.blit( imgOUT2, ( 0, 0 ) )
    else:
        # Black background
        screen.fill( C_BLACK )
        imgOUT2 = 0
    
    # Text info
    disp_phrase( "Background: %s" % C_BG[display_background] , ( 5, 5 ) , font, screen )
    
    
    # Copy over data
    cv.cv.Copy( imgRED[1], imgRED[0] )
    cv.cv.Copy( imgGRE[1], imgGRE[0] )
    cv.cv.Copy( imgBLU[1], imgBLU[0] )
    
    # Delete info from memory
    cv.cv.Zero( imgConCAP )
    cv.cv.Zero( imgOUT )
    
    cv.cv.Zero( imgRED[1] )
    cv.cv.Zero( imgGRE[1] )
    cv.cv.Zero( imgBLU[1] )
    
    cv.cv.Zero( imgREDDiff )
    cv.cv.Zero( imgGREDiff )
    cv.cv.Zero( imgBLUDiff )
    
    imgRAW      = 0
    imgCapture  = 0
    imgOUT2     = 0
    
    # Increase the frame count
    frame_count             += 1
    
    # Change the frame
    pygame.display.flip()