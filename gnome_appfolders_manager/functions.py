##
#     Project: GNOME App Folders Manager
# Description: Manage GNOME Shell applications folders
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2016-2022 Fabio Castelli
#     License: GPL-3+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

import fnmatch
from gettext import gettext, dgettext
import itertools
import logging
import os
import pathlib

from gi.repository import Gtk
from gi.repository import GdkPixbuf

from gnome_appfolders_manager.constants import DIR_UI

localized_messages = {}


def readlines(filename, empty_lines=False):
    """Read all the lines of a filename, optionally skipping empty lines"""
    result = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if line or empty_lines:
                result.append(line)
        f.close()
    return result


def text(message, gtk30=False, context=None):
    """Return a translated message and cache it for reuse"""
    if message not in localized_messages:
        if gtk30:
            # Get a message translated from GTK+ 3 domain
            full_message = message if not context else f'{context}\04{message}'
            localized_messages[message] = dgettext('gtk30', full_message)
            # Fix for untranslated messages with context
            if context and localized_messages[message] == full_message:
                localized_messages[message] = dgettext('gtk30', message)
        else:
            localized_messages[message] = gettext(message)
    return localized_messages[message]


def store_message(message, translated):
    """Store a translated message in the localized_messages list"""
    localized_messages[message] = translated


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return str(DIR_UI / filename)


def recursive_glob(starting_path, pattern):
    """Return a list of all the matching files recursively"""
    result = []
    for root, dirnames, filenames in os.walk(starting_path):
        for filename in fnmatch.filter(filenames, pattern):
            result.append(pathlib.Path(root) / filename)
    return result


def get_treeview_selected_row(widget):
    """Return the selected row in a GtkTreeView"""
    return widget.get_selection().get_selected()[1]


def get_treeview_selected_rows(widget):
    """Return the selected rows in a GtkTreeView"""
    return widget.get_selection().get_selected_rows()[1]


def get_pixbuf_from_icon_name(icon_name, size):
    """Get a Gdk.PixBuf from a theme icon"""
    theme = Gtk.IconTheme.get_default()
    path_icon_name = pathlib.Path(icon_name)
    if theme.has_icon(icon_name):
        # The icon was a theme icon
        icon = theme.load_icon(icon_name=icon_name,
                               size=size,
                               flags=Gtk.IconLookupFlags.USE_BUILTIN)
    elif theme.has_icon(path_icon_name.stem):
        # The theme contains an icon with the same file name
        icon = theme.load_icon(icon_name=path_icon_name.stem,
                               size=size,
                               flags=Gtk.IconLookupFlags.USE_BUILTIN)
    elif path_icon_name.is_file():
        # The icon was a full filename
        icon = GdkPixbuf.Pixbuf.new_from_file(icon_name)
    else:
        # The icon was not found in the current theme, search for filenames
        # with png or jpg extensions
        if (path_icon_name.suffix.lower() in ('.png', '.jpg', '.xpm', '.svg')):
            filenames = (icon_name, )
        else:
            filenames = (f'{icon_name}.png',
                         f'{icon_name}.jpg',
                         f'{icon_name}.xpm',
                         f'{icon_name}.svg')
        # Search for filenames in icons and pixmaps directories
        icon = None
        search_in_paths = ('/usr/share/icons',
                           '/usr/share/pixmaps')
        for path, filename in itertools.product(search_in_paths, filenames):
            file_path = pathlib.Path(path) / filename
            if file_path.is_file():
                icon = GdkPixbuf.Pixbuf.new_from_file(str(file_path))
                break
    if icon:
        # If size is not correct then resize the icon to the requested size
        if icon.get_width() != size or icon.get_height() != size:
            icon = icon.scale_simple(size, size,
                                     GdkPixbuf.InterpType.BILINEAR)
    else:
        logging.warning(f'missing icon: {icon_name}')
    return icon


def set_style_suggested_action(widget):
    """Add the suggested-action style to a widget"""
    widget.get_style_context().add_class("suggested-action")


# This special alias is used to track localization requests to catch
# by xgettext. The text() calls aren't tracked by xgettext
_ = text

__all__ = [
    'readlines',
    'text',
    'store_message',
    '_',
    'localized_messages',
    'get_ui_file',
    'recursive_glob',
    'get_treeview_selected_row',
    'get_treeview_selected_rows',
    'get_pixbuf_from_icon_name',
    'set_style_suggested_action'
]
