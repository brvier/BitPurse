import dbus
import dbus.service

def safe_str(txt):
    if txt:
        return txt.encode()
    else:
        return ''

def safe_first_line(txt):
    txt = safe_str(txt)
    lines = util.remove_html_tags(txt).strip().splitlines()
    if not lines or lines[0] == '':
        return ''
    else:
        return lines[0]

class DBusProxy(dbus.service.Object):
    #DBusPodcastsProxy(lambda: self.channels, self.on_itemUpdate_activate(), self.playback_episodes, self.download_episode_list, bus_name)
    def __init__(self, sendTo, busname):
        self._send_to = sendTo
        dbus.service.Object.__init__(self, \
                object_path='/', \
                bus_name=busname)


    @dbus.service.method(dbus_interface='net.khertan.bitpurse', in_signature='s', out_signature='')
    def sendWithLink(self, btcaddr):
        self._send_to(btcaddr)
        return 
       