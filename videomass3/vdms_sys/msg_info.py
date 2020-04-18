# -*- coding: UTF-8 -*-

#########################################################
# Name: msg_info.py
# Porpose: Gets Version, Copyright and program Description
# Compatibility: Python3, Python2
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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


def current_release():
    """
    General info strings
    NOTE: number version > major number.minor number.micro number(patch number)
    the sub release a=alpha release, b=beta release, c= candidate release
    Example 19.1.1c1
    """
    Release_Name = 'Videomass'
    Program_Name = 'videomass'
    Version = '2.0.5'
    Release = 'April 18 2020'
    Copyright = '© 2013-2020'
    Website = 'http://jeanslack.github.io/Videomass/'
    Author = 'Gianluca Pernigotto (aka jeanslack)'
    Mail = '<jeanlucperni@gmail.com>'
    Comment = ("\nThanks to:\n"
               "FFmpeg, FFmpeg is a trademark of Fabrice Bellard, \n"
               "originator of the FFmpeg project:\n"
               "<http://ffmpeg.org/>\n"
               "Material design icons from Google:\n"
               "http://google.github.io/material-design-icons/#getting-icons"
               "Flat Color Icons:\n"
               "https://icons8.com/color-icons"
               )
    return (Release_Name, Program_Name, Version, Release,
            Copyright, Website, Author, Mail, Comment)


def descriptions_release():
    """
    General info string
    """
    Copyright = current_release()
    Author = current_release()
    Mail = current_release()

    short_d = ("Videomass is a cross-platform GUI for FFmpeg")

    long_d = ("-Videomass- is not a converter. It provides a graphical\n"
              "interface to writing presets for FFmpeg\n")

    short_l = ("GPL3 (Gnu Public License)")

    license = ("Copyright - %s %s\n"
               "Author and Developer: %s\n"
               "Mail: %s\n\n"
               "Videomass is free software: you can redistribute\n"
               "it and/or modify it under the terms of the GNU General\n"
               "Public License as published by the Free Software\n"
               "Foundation, either version 3 of the License, or (at your\n"
               "option) any later version.\n\n"

               "Videomass is distributed in the hope that it\n"
               "will be useful, but WITHOUT ANY WARRANTY; without\n"
               "even the implied warranty of MERCHANTABILITY or\n"
               "FITNESS FOR A PARTICULAR PURPOSE.\n"
               "See the GNU General Public License for more details.\n\n"

               "You should have received a copy of the GNU General\n"
               "Public License along with this program. If not, see\n"
               "http://www.gnu.org/licenses/" % (Copyright[4],
                                                 Author[6],
                                                 Author[6],
                                                 Mail[7]))
    return (short_d, long_d, short_l, license)
