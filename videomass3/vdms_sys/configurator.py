# -*- coding: UTF-8 -*-
"""
Name: configurator.py
Porpose: Set Videomass configuration and appearance on startup
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.21.2021
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

 This file is part of Videomass.

    Videomass is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Videomass is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import shutil
import platform
from videomass3.vdms_utils.utils import copydir_recursively
from videomass3.vdms_utils.utils import copy_restore


def parsing_fileconf(fileconf):
    """
    Make parsing of the configuration file and return
    object list with the current program settings data.
    """
    with open(fileconf, 'r', encoding='utf8') as fget:
        fconf = fget.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    dataconf = [x for x in lst if x]  # list without empties values

    return None if not dataconf else dataconf


def get_pyinstaller():
    """
    Get pyinstaller-based package attributes to determine
    how to use sys.executable
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('getattr frozen, hasattr _MEIPASS')
        frozen, meipass = True, True
        path = getattr(sys, '_MEIPASS', os.path.abspath(__file__))
        data_location = path

    else:
        frozen, meipass = False, False
        path = os.path.realpath(os.path.abspath(__file__))
        data_location = os.path.dirname(os.path.dirname(path))

    return(frozen, meipass, path, data_location)


class DataSource():
    """
    DataSource class determines the Videomass's configuration
    according to the Operating System and define the environment
    paths based on the program execution and/or where it's
    installed.
    """
    USER_NAME = os.path.expanduser('~')
    OS = platform.system()

    # Establish the conventional paths based on OS
    if OS == 'Windows':
        DIRPATH = "\\AppData\\Roaming\\videomass\\videomass.conf"
        FILE_CONF = os.path.join(USER_NAME + DIRPATH)
        DIR_CONF = os.path.join(USER_NAME + "\\AppData\\Roaming\\videomass")
        LOG_DIR = os.path.join(DIR_CONF, 'log')  # logs
        CACHE_DIR = os.path.join(DIR_CONF, 'cache')  # updates executable

    elif OS == "Darwin":
        DIRPATH = "Library/Application Support/videomass/videomass.conf"
        FILE_CONF = os.path.join(USER_NAME, DIRPATH)
        DIR_CONF = os.path.join(USER_NAME, os.path.dirname(DIRPATH))
        LOG_DIR = os.path.join(USER_NAME, "Library/Logs/videomass")
        CACHE_DIR = os.path.join(USER_NAME, "Library/Caches/videomass")

    else:  # Linux, FreeBsd, etc.
        DIRPATH = ".config/videomass/videomass.conf"
        FILE_CONF = os.path.join(USER_NAME, DIRPATH)
        DIR_CONF = os.path.join(USER_NAME, ".config/videomass")
        LOG_DIR = os.path.join(USER_NAME, ".local/share/videomass/log")
        CACHE_DIR = os.path.join(USER_NAME, ".cache/videomass")
    # -------------------------------------------------------------------

    def __init__(self):
        """
        Given the paths defined by `data_location` (a configuration
        folder for recovery > `self.srcpath`, a set of icons >
        `self.icodir` and a folder for the locale > `self.localepath`),
        it performs the initialization described in DataSource.
        """

        frozen, meipass, path, data_location = get_pyinstaller()
        self.apptype = None  # appimage, pyinstaller on None
        self.workdir = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        self.localepath = os.path.join(data_location, 'locale')
        self.srcpath = os.path.join(data_location, 'share')
        self.icodir = os.path.join(data_location, 'art', 'icons')
        self.ffmpeg_pkg = os.path.join(data_location, 'FFMPEG')
        launcher = os.path.isfile('%s/launcher' % self.workdir)

        if frozen and meipass or launcher:
            print('frozen=%s meipass=%s launcher=%s' % (frozen,
                                                        meipass,
                                                        launcher
                                                        ))
            self.apptype = 'pyinstaller' if launcher is False else None
            self.videomass_icon = "%s/videomass.png" % self.icodir

        else:
            if DataSource.OS == 'Windows':  # Installed with pip command
                print('Win32 executable=%s' % sys.executable)
                # HACK check this
                # dirname = os.path.dirname(sys.executable)
                # pythonpath = os.path.join(dirname, 'Script', 'videomass')
                # self.icodir = dirname + '\\share\\videomass\\icons'
                self.videomass_icon = self.icodir + "\\videomass.png"

            elif ('/tmp/.mount_' in sys.executable or os.path.exists(
                  os.path.dirname(os.path.dirname(os.path.dirname(
                  sys.argv[0]))) + '/AppRun')):
                # embedded on python appimage
                print('Embedded on python appimage')
                self.apptype = 'appimage'
                userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
                pixmaps = '/share/pixmaps/videomass.png'
                self.videomass_icon = os.path.join(userbase + pixmaps)

            elif 'usr/bin/videomass' in sys.argv[0]:
                print('Embedded on python appimage externally')
                self.apptype = 'appimage'
                userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
                pixmaps = '/share/pixmaps/videomass.png'
                self.videomass_icon = os.path.join(userbase + pixmaps)

            else:
                binarypath = shutil.which('videomass')

                if binarypath == '/usr/local/bin/videomass':
                    print('executable=%s' % binarypath)
                    # pip as super user, usually Linux, MacOs, Unix
                    share = '/usr/local/share/pixmaps'
                    self.videomass_icon = share + '/videomass.png'

                elif binarypath == '/usr/bin/videomass':
                    print('executable=%s' % binarypath)
                    # installed via apt, rpm, etc, usually Linux
                    share = '/usr/share/pixmaps'
                    self.videomass_icon = share + "/videomass.png"

                else:
                    print('executable=%s' % binarypath)
                    # pip as normal user, usually Linux, MacOs, Unix
                    userbase = os.path.dirname(os.path.dirname(binarypath))
                    pixmaps = '/share/pixmaps/videomass.png'
                    self.videomass_icon = os.path.join(userbase + pixmaps)
    # ---------------------------------------------------------------------

    def get_fileconf(self):
        """
        Get videomass configuration data from videomass.conf.
        Returns a dict object.

        This method performs the following main steps:

            1) Checks user videomass configuration dir; if not exists try to
               restore from self.srcpath
            2) Read the videomass.conf file; if not exists try to restore
               from self.srcpath
            3) Checks presets folder; if not exists try to restore from
               self.srcpath

        Note that when `copyerr` is not False, it causes a fatal error on
        videomass bootstrap.
        """
        copyerr = False
        existfileconf = True  # True > found, False > not found

        if os.path.exists(DataSource.DIR_CONF):  # if ~/.conf/videomass dir
            if os.path.isfile(DataSource.FILE_CONF):
                userconf = parsing_fileconf(DataSource.FILE_CONF)
                if not userconf:
                    existfileconf = False
                if float(userconf[0]) != 3.1:
                    existfileconf = False
            else:
                existfileconf = False

            if not existfileconf:  # try to restore only videomass.conf
                fcopy = copy_restore('%s/videomass.conf' % self.srcpath,
                                     DataSource.FILE_CONF)
                if fcopy:
                    copyerr, userconf = fcopy, None
                else:
                    userconf = parsing_fileconf(DataSource.FILE_CONF)
                    # read again file conf

            if not os.path.exists(os.path.join(DataSource.DIR_CONF,
                                               "presets")):
                # try to restoring presets directory on videomass dir
                drest = copydir_recursively(os.path.join(self.srcpath,
                                                         "presets"),
                                            DataSource.DIR_CONF)
                if drest:
                    copyerr, userconf = drest, None

        else:  # try to restore entire configuration directory
            dconf = copydir_recursively(self.srcpath,
                                        os.path.dirname(DataSource.DIR_CONF),
                                        "videomass")
            userconf = parsing_fileconf(DataSource.FILE_CONF)
            # read again file conf
            if dconf:
                copyerr, userconf = dconf, None

        return ({'ostype': DataSource.OS,
                 'srcpath': self.srcpath,
                 'fatalerr': copyerr,
                 'localepath': self.localepath,
                 'fileconfpath': DataSource.FILE_CONF,
                 'workdir': self.workdir,
                 'confdir': DataSource.DIR_CONF,
                 'logdir': DataSource.LOG_DIR,
                 'cachedir': DataSource.CACHE_DIR,
                 'FFMPEG_videomass_pkg': self.ffmpeg_pkg,
                 'app': self.apptype,
                 'confversion': userconf[0],
                 'outputfile': userconf[1],
                 'ffthreads': userconf[2],
                 'ffplayloglev': userconf[3],
                 'ffmpegloglev': userconf[4],
                 'ffmpeg_local': userconf[5],
                 'ffmpeg_bin': userconf[6],
                 'ffprobe_local': userconf[7],
                 'ffprobe_bin': userconf[8],
                 'ffplay_local': userconf[9],
                 'ffplay_bin': userconf[10],
                 'icontheme': userconf[11],
                 'toolbarsize': userconf[12],
                 'toolbarpos': userconf[13],
                 'toolbartext': userconf[14],
                 'clearcache': userconf[15],
                 'enable_youtubedl': userconf[16],
                 'outputfile_samedir': userconf[17],
                 'filesuffix': userconf[18],
                 'outputdownload': userconf[19],
                 'playlistsubfolder': userconf[20]}
                )
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the configuration
        file (see `Set icon themes map:`, on paragraph `6- GUI setup`
        by Videomass.conf).
        Returns a icontheme dict object.

        """
        keys = ('videomass', 'A/V-Conv', 'startconv', 'fileproperties',
                'playback', 'concatenate', 'preview', 'clear',
                'profile_append', 'scale', 'crop', 'rotate', 'deinterlace',
                'denoiser', 'statistics', 'settings', 'audiovolume',
                'youtube', 'presets_manager', 'profile_add', 'profile_del',
                'profile_edit', 'previous', 'next', 'startdownload',
                'download_properties', 'stabilizer')

        ext = 'svg' if 'wx.svg' in sys.modules else 'png'

        iconames = {'Videomass-Light':  # Videomass icons for light themes
                    {'x48': '%s/Sign_Icons/48x48_light' % self.icodir,
                     'x16': '%s/Videomass-Light/16x16' % self.icodir,
                     'x22': '%s/Videomass-Light/24x24' % self.icodir},
                    'Videomass-Dark':  # Videomass icons for dark themes
                    {'x48': '%s/Sign_Icons/48x48_dark' % self.icodir,
                     'x16': '%s/Videomass-Dark/16x16' % self.icodir,
                     'x22': '%s/Videomass-Dark/24x24' % self.icodir},
                    'Videomass-Colours':  # Videomass icons for all themes
                    {'x48': '%s/Sign_Icons/48x48' % self.icodir,
                     'x16': '%s/Videomass-Colours/16x16' % self.icodir,
                     'x22': '%s/Videomass-Colours/24x24' % self.icodir},
                    'Breeze':  # Breeze for light themes
                    {'x48': '%s/Sign_Icons/48x48_light' % self.icodir,
                     'x16': '%s/Breeze/16x16' % self.icodir,
                     'x22': '%s/Breeze/22x22' % self.icodir},
                    'Breeze-Dark':  # breeze for dark themes
                    {'x48': '%s/Sign_Icons/48x48_dark' % self.icodir,
                     'x16': '%s/Breeze-Dark/16x16' % self.icodir,
                     'x22': '%s/Breeze-Dark/22x22' % self.icodir},
                    'Breeze-Blues':  # breeze custom colorized for all themes
                    {'x48': '%s/Sign_Icons/48x48' % self.icodir,
                     'x16': '%s/Breeze-Blues/16x16' % self.icodir,
                     'x22': '%s/Breeze-Blues/22x22' % self.icodir}
                    }

        choose = iconames.get(icontheme)  # set appropriate icontheme

        iconset = (self.videomass_icon,
                   '%s/icon_videoconversions.%s' % (choose.get('x48'), ext),
                   '%s/convert.%s' % (choose.get('x22'), ext),
                   '%s/properties.%s' % (choose.get('x22'), ext),
                   '%s/playback.%s' % (choose.get('x16'), ext),
                   '%s/icon_concat.%s' % (choose.get('x48'), ext),
                   '%s/preview.%s' % (choose.get('x16'), ext),
                   '%s/edit-clear.%s' % (choose.get('x16'), ext),
                   '%s/profile-append.%s' % (choose.get('x22'), ext),
                   '%s/transform-scale.%s' % (choose.get('x16'), ext),
                   '%s/transform-crop.%s' % (choose.get('x16'), ext),
                   '%s/transform-rotate.%s' % (choose.get('x16'), ext),
                   '%s/deinterlace.%s' % (choose.get('x16'), ext),
                   '%s/denoise.%s' % (choose.get('x16'), ext),
                   '%s/statistics.%s' % (choose.get('x16'), ext),
                   '%s/configure.%s' % (choose.get('x16'), ext),
                   '%s/player-volume.%s' % (choose.get('x16'), ext),
                   '%s/icon_youtube.%s' % (choose.get('x48'), ext),
                   '%s/icon_prst_mng.%s' % (choose.get('x48'), ext),
                   '%s/newprf.%s' % (choose.get('x16'), ext),
                   '%s/delprf.%s' % (choose.get('x16'), ext),
                   '%s/editprf.%s' % (choose.get('x16'), ext),
                   '%s/go-previous.%s' % (choose.get('x22'), ext),
                   '%s/go-next.%s' % (choose.get('x22'), ext),
                   '%s/download.%s' % (choose.get('x22'), ext),
                   '%s/statistics.%s' % (choose.get('x22'), ext),
                   '%s/stabilizer.%s' % (choose.get('x16'), ext)
                   )
        values = [os.path.join(norm) for norm in iconset]  # normalize pathns

        return dict(zip(keys, values))
