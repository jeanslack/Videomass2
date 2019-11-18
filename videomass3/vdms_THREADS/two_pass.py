# -*- coding: UTF-8 -*-

#########################################################
# Name: one_pass_process.py 
# Porpose: FFmpeg long processing task with one pass conversion
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov 16 2019
#########################################################
# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################

import wx
import subprocess
import itertools
import os
from threading import Thread
import time
from pubsub import pub

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf # path to the configuration directory:
ffmpeg_url = get.ffmpeg_url
ffmpeg_loglev = get.ffmpeg_loglev

if not OS == 'Windows':
    import shlex
    
not_exist_msg =  _("Is 'ffmpeg' installed on your system?")

#----------------------------------------------------------------#    
def logWrite(cmd, sterr, logname):
    """
    writes ffmpeg commands and status error during threads below
    
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
        
    else:
        apnd = "%s\n\n" % (cmd)
        
    with open("%s/log/%s" % (DIRconf, logname), "a") as log:
        log.write(apnd)
        
#------------------------------ THREADS -------------------------------#
"""
NOTE MS Windows:

subprocess.STARTUPINFO() 

https://stackoverflow.com/questions/1813872/running-
a-process-in-pythonw-with-popen-without-a-console?lq=1>

NOTE capturing output in real-time (Windows, Unix):

https://stackoverflow.com/questions/1388753/how-to-get-output-
from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

"""
class TwoPass(Thread):
    """
    This class represents a separate thread which need to read the 
    stdout/stderr in real time mode. The subprocess module is instantiated 
    twice for two different tasks: the process on the first video pass and 
    the process on the second video pass for video only.
    """
    def __init__(self, varargs, duration, logname, timeseq):
        """
        The 'volume' attribute may have an empty value, but it will 
        have no influence on the type of conversion.
        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False # process terminate
        self.filelist = varargs[1] # list of files (elements)
        self.passList = varargs[5] # comand list set for double-pass
        self.outputdir = varargs[3] # output path
        self.extoutput = varargs[2] # format (extension)
        self.duration = duration # duration list
        self.time_seq = timeseq # a time segment
        self.volume = varargs[7]# volume compensation data
        self.count = 0 # count first for loop
        self.countmax = len(varargs[1]) # length file list
        self.logname = logname # title name of file log
        self.nul = 'NUL' if OS == 'Windows' else '/dev/null'
        
        self.start()# start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        
        """
        for (files,
             folders,
             volume,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.outputdir, 
                                                self.volume, 
                                                self.duration,
                                                fillvalue='',
                                                ):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione

            #--------------- first pass
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
                
            pass1 = ('%s %s %s -i "%s" %s %s"%s/%s.log" -y %s' % (
                                                            ffmpeg_url, 
                                                            ffmpeg_loglev,
                                                            self.time_seq,
                                                            files, 
                                                            self.passList[0],
                                                            passpar,
                                                            folders, 
                                                            filename,
                                                            self.nul,
                                                            )) 
            self.count += 1
            count = 'File %s/%s - Pass One' % (self.count, self.countmax,)
            cmd = "%s\n%s" % (count, pass1)
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)# write n/n + command only
            
            if not OS == 'Windows':
                pass1 = shlex.split(pass1)
                info = None
            else: # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                with subprocess.Popen(pass1, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True,
                                      startupinfo=info,) as p1:
                    
                    for line in p1.stderr:
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=0
                                     )
                        if self.stop_work_thread: # break second 'for' loop
                            p1.terminate()
                            break
                        
                    if p1.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p1.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p1.wait(),
                                 self.logname)
                                 #append exit error number
                                 
            except OSError as err:
                e = "%s\n  %s" % (err, not_exist_msg)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             end='error',
                             )
                break
                    
            if self.stop_work_thread: # break first 'for' loop
                p1.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p1.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
            #--------------- second pass ----------------#
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
                
            pass2 = ('%s %s %s -i "%s" %s %s %s'
                     '"%s/%s.log" -y "%s/%s.%s"' % (ffmpeg_url,
                                                    ffmpeg_loglev,
                                                    self.time_seq,
                                                    files, 
                                                    self.passList[1], 
                                                    volume,
                                                    passpar,
                                                    folders, 
                                                    filename,
                                                    folders, 
                                                    filename,
                                                    self.extoutput,
                                                    ))
            count = 'File %s/%s - Pass Two' % (self.count, self.countmax,)
            cmd = "%s\n%s" % (count, pass2)
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)
            
            if not OS == 'Windows':
                pass2 = shlex.split(pass2)
                info = None
            else: # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(pass2, 
                                  stderr=subprocess.PIPE, 
                                  bufsize=1, 
                                  universal_newlines=True,
                                  startupinfo=info,) as p2:
                    
                    for line2 in p2.stderr:
                        #print (line2, end=''),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line2, 
                                     duration=duration,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            p2.terminate()
                            break
                        
                    if p2.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p2.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p2.wait(), 
                                 self.logname)
                                 #append exit error number
                        
            if self.stop_work_thread: # break first 'for' loop
                p2.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p2.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
    #--------------------------------------------------------------------#
    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True