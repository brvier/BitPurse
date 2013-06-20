# -*- coding: utf-8 -*-

"""
A library to post events to the MeeGo 1.2 Harmattan Event Feed

This library is intended to be used by N950, N9 application or
service developers who want to post their own content to the
MeeGo 1.2 Harmattan UX Event Feed screen.
"""

__license__ = """
Copyright (c) 2011, Thomas Perl <m@thp.io>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

__version__ = '1.0'
__author__ = 'Thomas Perl <thp.io/about>'
__url__ = 'http://thp.io/2011/eventfeed/'

__version_info__ = tuple(int(x) for x in __version__.split('.'))

# Dependency on PySide for encoding/decoding like MRemoteAction
from PySide.QtCore import QBuffer, QIODevice, QDataStream, QByteArray

# Python D-Bus Library dependency for communcating with the service
import dbus
import dbus.service
import dbus.mainloop
import dbus.glib

import datetime
import logging


logger = logging.getLogger(__name__)

# When the user clicks on "Refresh", this signal gets sent via D-Bus:
# signal sender=:1.8 -> dest=(null destination) serial=855 path=/eventfeed; interface=com.nokia.home.EventFeed; member=refreshRequested
# TODO: Implement support for receiving this signal

# MRemoteAction::toString()
# http://apidocs.meego.com/1.0/mtf/mremoteaction_8cpp_source.html
def qvariant_encode(value):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    stream = QDataStream(buffer)
    stream.writeQVariant(value)
    buffer.close()
    return buffer.buffer().toBase64().data().strip()

# MRemoteAction::fromString()
# http://apidocs.meego.com/1.0/mtf/mremoteaction_8cpp_source.html
def qvariant_decode(data):
    byteArray = QByteArray.fromBase64(data)
    buffer = QBuffer(byteArray)
    buffer.open(QIODevice.ReadOnly)
    stream = QDataStream(buffer)
    result = stream.readQVariant()
    buffer.close()
    return result


class EventFeedItem(object):
    """One item that can be posted to the event feed"""

    def __init__(self, icon, title, timestamp=None):
        """Create a new event feed item

        :param icon: Icon name or path to icon file (can be a URL)
        :param title: The title text describing this item
        :param timestamp: datetime.datetime object when the item happened (optional)
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()

        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        self.args = {
            'icon': icon,
            'title': title,
            'timestamp': timestamp,
        }

        # ID assigned when showing item
        self.id = -1

        # Callback for when the action is clicked
        self.callback = None

        # Action data (custom list of stuff for callback)
        self.action_data = None

    def set_body(self, body):
        """Body text of the item (string)"""
        self.args['body'] = body

    def set_image_list(self, image_list):
        """List of image filenames/URLs (list of strings)"""
        self.args['imageList'] = image_list

    def set_footer(self, footer):
        """Footer text, displayed near the time (string)"""
        self.args['footer'] = footer

    def set_video(self, video):
        """Flag to overlay a play button on the thumbnail (bool)"""
        self.args['video'] = video

    def set_url(self, url):
        """The URL to be opened when the item is clicked (string)"""
        self.args['url'] = url

    def set_action_data(self, *args):
        """The data to be sent when clicked (list of str, int, bool)"""
        self.action_data = args

    def set_custom_action(self, callback):
        """The action to be executed when clicked (callable)"""
        self.callback = callback


class EventFeedService(dbus.service.Object):
    EVENT_FEED_NAME = 'com.nokia.home.EventFeed'
    EVENT_FEED_PATH = '/eventfeed'
    EVENT_FEED_INTF = 'com.nokia.home.EventFeed'
    EVENT_FEED_CALL = 'addItem'

    DEFAULT_NAME = 'com.thpinfo.meego.EventFeedService'
    DEFAULT_PATH = '/EventFeedService'
    DEFAULT_INTF = 'com.thpinfo.meego.EventFeedService'

    def __init__(self, source_name, source_display_name, on_data_received=None):
        """Create a new client to the event feed service

        :param source_name: SLUG for the application (used in the service name)
        :param source_display_name: User-visible application name (in the UI)
        :param on_data_received: Callback for received data (optional)
        """
        dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus(dbus_main_loop)

        self.local_name = '.'.join([self.DEFAULT_NAME, source_name])
        logger.debug('Local D-Bus name: %s', self.local_name)
        bus_name = dbus.service.BusName(self.local_name, bus=session_bus)

        dbus.service.Object.__init__(self,
                object_path=self.DEFAULT_PATH,
                bus_name=bus_name)

        self.next_action_id = 1
        self.actions = {}
        self.source_name = source_name
        self.source_display_name = source_display_name
        self.on_data_received = on_data_received

        o = session_bus.get_object(self.EVENT_FEED_NAME, self.EVENT_FEED_PATH)
        self.event_feed = dbus.Interface(o, self.EVENT_FEED_INTF)

    @dbus.service.method(DEFAULT_INTF)
    def ReceiveActionCallback(self, action_id):
        action_id = int(action_id)
        logger.debug('Received callback ID %d', action_id)
        callable = self.actions[action_id]
        callable()

    @dbus.service.method(DEFAULT_INTF)
    def ReceiveActionData(self, *args):
        logger.debug('Received data: %r', args)
        if self.on_data_received is not None:
            self.on_data_received(*args)

    def add_item(self, item):
        """Send a EventFeedItem to the service to be displayed

        :param item: EventFeedItem to be displayed
        """
        if item.id != -1:
            logger.debug('Message %d already shown - updating footer.', item.id)
            self.update_item(item)
            return item.id

        action = item.callback
        action_data = item.action_data
        data = item.args.copy()

        data['sourceName'] = self.source_name
        data['sourceDisplayName'] = self.source_display_name

        if action is not None or action_data is not None:
            remote_action = [
                    self.local_name,
                    self.DEFAULT_PATH,
                    self.DEFAULT_INTF,
            ]

            if action is not None:
                action_id = self.next_action_id
                self.next_action_id += 1
                self.actions[action_id] = action
                remote_action.extend([
                    'ReceiveActionCallback',
                    qvariant_encode(action_id),
                ])
            else: # action_data is not None
                remote_action.append('ReceiveActionData')
                remote_action.extend([qvariant_encode(x) for x in action_data])

            data['action'] = ' '.join(remote_action)

        item.id = self.event_feed.addItem(data)

        return item.id

    def update_item(self, item):
        """Update a previously-sent EventFeedItem

        :param item: EventFeedItem to be updated
        """
        if item.id == -1:
            return False

        if 'footer' not in item.args:
            return False

        data = {'footer': item.args['footer']}
        data['sourceName'] = self.source_name
        data['sourceDisplayName'] = self.source_display_name

        self.event_feed.updateItem(item.id, data)
        return True

    def remove_items(self):
        """Remove all items """
        self.event_feed.removeItemsBySourceName(self.source_name)
        # No need to remember action IDs, because all items were removed
        self.actions = {}

