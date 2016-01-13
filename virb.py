#!/usr/bin/python2.7
# -*- coding: utf8 -*-
"""Module to interact with Garmin virb cameras over wifi / mass storage 
This module also allows you to interact with the Garmin website and 
fetch firmware updates when you don't feel like using the Garmin supplied 
windows or Mac software.

I can't give you any warranty that any of these things will work,
especially the firmware upgrades could be dangerous.
"""
__author__ = 'Jan KLopper (jan@underdark.nl)'
__version__ = 0.1

import os
import sys
import simplejson
import requests

class virb(object):
  """Class to interact with virb cameras over wifi / http"""
  def __init__(self, host=("192.168.0.1",80)):
    self.host = host
    self.requests = 0
  
  def Status(self):
    """Returns the current camera status"""
    command = "status"
    data = {'command':command}
    return self._doPost(data=data)

  def Features(self):
    """Returns the features"""
    command = "features"
    data = {'command':command}
    return self._doPost(data=data)[command]

  def GetFeatures(self):
    """Returns the features list as a dictionary"""
    features = self.Features()
    results = {'enabled': {}, 'disabled': {}}
    for feature in features:
      name = str(feature['feature'])
      value = feature['value']
      try:
        value = int(value)
      except ValueError:
        value = str(value)
      if feature['enabled']:
        results['enabled'][name] = value
      else:
        results['disabled'][name] = value
    return results
  
  def SetFeatures(self, feature, value):
    """Update a features"""
    command = "updateFeature"
    data = {'command':command, 
            'feature':feature,
            'value':value}
    return self._doPost(data=data)['features']

  def Sensors(self):
    """Returns the current camera sensor readings"""
    command = "sensors"
    data = {'command':command}
    sensors = self._doPost(data=data)
    if len(sensors) == 0:
      raise VirbNoSensors('no Sensors are currently available')

  def DeviceInfo(self):
    """Returns the cameras device info"""
    command = "deviceInfo"
    data = {'command':command}
    return self._doPost(data=data)[command]

  def Locate(self):
    """Starts the camera emmiting its lost sound/flash"""
    command = "locate"
    data = {'command':command}
    return bool(int(self._doPost(data=data)['result']))

  def Found(self):
    """Stops the camera emmiting its lost sound/flash"""
    command = "found"
    data = {'command':command}
    return bool(int(self._doPost(data=data)['result']))

  def MediaDirList(self):
    """Returns the list of media directories on the device"""
    command = "mediaDirList"
    data = {'command':command}
    return self._doPost(data=data)#['mediaDirs']

  def MediaList(self, path=None):
    """Returns the list of media directories on the device"""
    command = "mediaList"
    data = {'command':command}
    if path:
      data['path'] = path
    return self._doPost(data=data)['media']


  def LivePreview(self, streamtype="rtp"):
    """Returns the cameras live preview url"""
    command = "livePreview"
    data = {'command':command,
            'streamType':streamtype}
    return self._doPost(data=data)['url']

  def SnapPicture(self, timer=0):
    """Take a picture"""
    command = "snapPicture"
    data = {'command':command, 
            'selfTimer':timer}
    return self._doPost(data=data)

  def StartRecording(self):
    """Start recording"""
    command = "startRecording"
    data = {'command':command}
    return bool(int(self._doPost(data=data)['result']))

  def StopRecording(self):
    """Stop recording"""
    command = "stopRecording"
    data = {'command':command}
    return bool(int(self._doPost(data=data)['result']))

  def StopStilRecording(self):
    """Stop recording still images"""
    command = "stopStillRecording"
    data = {'command':command}
    return bool(int(self._doPost(data=data)['result']))

  def _doPost(self, url="virb", data=None):
    url = 'http://%s:%d/%s' % (self.host[0], self.host[1], url)
    request = requests.post(url, data=simplejson.dumps(data))
    self.requests = self.requests + 1
    try:
      return request.json()
    except simplejson.scanner.JSONDecodeError:
      return request.text


class VirbUsb(object):
  def __init__(self, device):
    self.device = device

  def GetLog(self):
    """Yields a list of log entries on the device"""
    logfile = open('%s/Garmin/elog.txt' % self.device, 'r')
    logentry = []
    for line in logfile.readline():
      if len(line)>0:
        logentry.push(line)
      if logline == '-----------------------------------------':
        yield logentry
        logentry = []

  def ClearLog(self):
    """Clears the log entries on the device"""
    logfile = open('%s/Garmin/elog.txt' % self.device, 'w')
    logfile.close()
    return True

  def GetTracks(self):
    """Lists all the gpx tracks on the devices"""
    trackpath = '%s/Garmin/GPX' % self.device
    fileslist = os.listdir(trackpath)
    return [filename for filename in fileslist if os.path.isfile(os.path.join(trackpath, filename))] 

  def GetActivity(self):
    """Lists all FIT activity files on the device
    
    Use https://github.com/dtcooper/python-fitparse to parse these files into 
    something meaningfull. Or install fitparse using pip: `pip install fitparse`
    """
    activitypath = '%s/Garmin/Activity' % self.device
    fileslist = os.listdir(activitypath)
    return [filename for filename in fileslist if os.path.isfile(os.path.join(activitypath, filename))] 

  def GetMedia(self, extensions=('jpg', 'mp4')):
    """Lists all pictures/videos on the devices
    
    Possibly filter on extensions (lowercase) using the extensions argument as 
      a tuple
    """
    mediapath = '%s/DCIM/100_VIRB' % self.device
    fileslist = os.listdir(mediapath)
    return [filename for filename in fileslist if (os.path.isfile(os.path.join(mediapath, filename)) and filename[-3:].lower() in extensions)] 

  def UpdateFirmware(version=None):
    """This Upgrades the firmware on the Vibr
    
    It follows the known update procedure but handles everything on its own.
    
    GCD Update Procedure

    Use the links in Firmware History to download the zipped file for the 
    version you need.
    (https://www8.garmin.com/support/download_details.jsp?id=6565)
    Unzip the downloaded archive and extract the gcd file
    Rename the gcd file to gupdate.gcd
    Connect the VIRB to your computer via usb
    Copy the gupdate.gcd file to [µSD]\Garmin\gupdate.gcd
    Disconnect and reboot the VIRB
    Once the update is completed, the VIRB will delete the gupdate.gcd file"""
    if version:
      garmin = Garmin()
      firmware = garming.GetFirmware(version=version)
      targetpath = '%s/Garmin/gupdate-.gcd' % self.device
      print "Writing out data to device, do not reboot / power down"
      targetfile = open(targetpath, 'w')
      targetfile.write(firmware)
      print "Finishing writing out data to device, do not reboot / power down"
      os.fsync(targetfile)
      targetfile.close()
      print "All Done. Please reboot the Virb"
      return True
    return False


class Garmin(object):
  def GetFirmware(device="VIRB", version=4.00):
    """Version as float"""
    return requests.get("https://download.garmin.com/software/%s_%d.gcd" % (
        device, int(version*100)))

class VirbError(Exception):
  """General exception class for Vibr camera class"""


class VirbNoSensors(VirbError):
  """No sensors where located / enabled / connected to the Virb"""


if __name__ == '__main__':
  camera = virb()
  print repr(camera.Status())
  print repr(camera.DeviceInfo())
  print repr(camera.Features())
  print repr(camera.GetFeatures())  
  try:
    print repr(camera.Sensors())
  except VirbNoSensors:
    print 'no sensors connected'
  print repr(camera.MediaDirList())
  #print repr(camera.SnapPicture())
