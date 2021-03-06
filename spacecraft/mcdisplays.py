from mcpi.minecraft import Minecraft
from mcpi import block
from mcmodels import ISS, Stairs, Rocket, LaunchPad
from mcsensors import DisplayTube
from time import sleep, time
from mcclock import Clock

"""
SpaceCRAFT - Astro Pi competition[http://astro-pi.org/] entry
Conceived by Hannah Belshaw
Created by Martin O'Hanlon[http://www.stuffaboutcode.com]
For the Raspberry Pi Foundation[https://www.raspberrypi.org]

mcdisplays.py

Displays information from the Astro Pi in Minecraft
"""

def roundDegrees(number):
    ROUNDDEGREESTO = 15
    return round((number / ROUNDDEGREESTO),0) * ROUNDDEGREESTO

class ISSTowerMinecraftDisplay():
    """
    Hannah's vision of how we would display the data in Minecraft
    
    A minecraft display which is 3 towers showing sensor data leading up to
    the ISS, with a clock and rocket launch tower
    """
    def __init__(self, mc, pos):

        self.mc = mc
        self.pos = pos

        self.time = None
        self.cputemperature = None
        self.temperature = None
        self.humidity = None
        self.pressure = None
        self.orientation = {"yaw": 0, "pitch": 0, "roll": 0}
        self.joystick = {"up": 0, "down": 0, "left": 0, "right": 0, "button": 0}
        
        #calculate the positions of the towers, iss, clock and stairs
        temppos = pos.clone()
        temppos.x += 2

        humiditypos = pos.clone()
        humiditypos.x -= 2

        pressurepos = pos.clone()
        pressurepos.z += 2

        cputemppos = pos.clone()
        cputemppos.z -= 2

        isspos = pos.clone()
        isspos.y += 40

        clockpos = pos.clone()
        clockpos.x -= 30
        clockpos.z -= 10
        clockpos.y += 11

        rocketpos = pos.clone()
        rocketpos.x += 15
        rocketpos.z -= 10

        stairspos = pos.clone()
        stairspos.z -= 5

        #create the clock
        self.clock = Clock(mc, clockpos, block.WOOL.id, 11)

        #clear an area for the tubes
        self.mc.setBlocks(
            self.pos.x - 3,
            self.pos.y,
            self.pos.z - 3,
            self.pos.x + 3,
            self.pos.y + 20,
            self.pos.z + 3,
            block.AIR.id)
        
        #create the tubes
        self.tempTube = DisplayTube(
            mc, temppos, 20,
            10, 40,
            block.LAVA.id)

        self.humidityTube = DisplayTube(
            mc, humiditypos, 20,
            20, 50,
            block.WATER)

        self.pressureTube = DisplayTube(
            mc, pressurepos, 20,
            950, 1050,
            block.OBSIDIAN)

        self.cputempTube = DisplayTube(
            mc, cputemppos, 20,
            30, 50,
            block.WOOL.id, 14)

        #create the ISS
        self.iss = ISS(mc, isspos)
        
        #create the stairs
        self.stairs = Stairs(mc, stairspos, 6, 38, block.DIAMOND_BLOCK.id)

        #create the launch pad and rocket
        self.launchpad = LaunchPad(mc, rocketpos)
        self.rocket = Rocket(mc, rocketpos, cleararea = False)

    def update(self, time, cpuTemperature, temperature, humidity, pressure, orientation, joystick):        
        #update the clock
        self.clock.setTime(time)

        #update the towers
        self.cputempTube.setValue(cpuTemperature)
        self.tempTube.setValue(temperature)
        self.humidityTube.setValue(humidity)
        self.pressureTube.setValue(pressure)

        #rotate the ISS
        yaw, pitch, roll = orientation["yaw"], orientation["pitch"], orientation["roll"]
        yaw, pitch, roll = roundDegrees(yaw), roundDegrees(pitch), roundDegrees(roll)
        if self.iss.rotate(yaw, pitch, roll):
            #if the iss was rotated, redraw the stairs as the ISS might have destroyed them
            self.stairs.draw()

        #has the joystick been pressed?
        if joystick["button"] == 1 or joystick["left"] == 1 or joystick["right"] == 1 or joystick["up"] == 1 or joystick["down"] == 1:
            #launch the rocket and then redraw it and the launch pad
            self.rocket.launch(75)
            self.launchpad.redraw()
            self.rocket.reset()
                    
        #update the values
        self.time = time
        self.cpuTemperature = cpuTemperature
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.orientation = orientation
        self.joystick = joystick

    def clear(self):
        #clear the display
        self.tempTube.clear()
        self.humidityTube.clear()
        self.pressureTube.clear()
        self.cputempTube.clear()
        self.iss.clear()
        self.clock.clear()
        self.stairs.clear()
        self.rocket.clear()
        self.launchpad.clear()

    
#test
if __name__ == "__main__":
    mc = Minecraft.create()
    pos = mc.player.getTilePos()
    pos.x += 5
    pos.y = mc.getHeight(pos.x, pos.y)
    mcdisplay = ISSTowerMinecraftDisplay(mc, pos)
    try:
        mcdisplay.update(
            time(), 40, 30, 40, 1000,
            {"yaw": 0, "pitch": 0, "roll": 0},
            {"up": 0, "down": 0, "left": 0, "right": 0, "button": 0})
        sleep(10)
        mcdisplay.update(
            time(), 45, 20, 30, 1050,
            {"yaw": 45, "pitch": 45, "roll": 0},
            {"up": 1, "down": 1, "left": 1, "right": 1, "button": 1})
        sleep(10)
    finally:
        mcdisplay.clear()
    
