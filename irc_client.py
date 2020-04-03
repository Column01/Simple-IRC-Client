import sys
import time
from threading import Thread

import irc.bot
import requests


class IRCClient(irc.bot.SingleServerIRCBot):
    
    def __init__(self, username, token, channel, server, port, settings, gui_instance):
        # USING IRC BOT CLASS TO HAVE BETTER FEATURES AND SINCE I'VE USED IT BEFORE
        self.client_username = username
        self.token = token
        self.channel = '#' + channel
        self.settings = settings
        self.server = server
        self.port = port
        irc.bot.SingleServerIRCBot.__init__(self, [(self.server, self.port, self.token)], self.client_username, self.client_username)
        self.gui = gui_instance
    
    def on_welcome(self, connection, event):
        # Request some info from twitch
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        # Add the user to the channel's users list if they do not already exist in it.
        # The library should handle removal from the PART message in IRC
        chan = event.target
        if event.source.nick not in self.channels[chan].users():
            self.channels[chan].add_user(event.source.nick)

        message = event.arguments[0]
        username = [event.tags[i]["value"] for i in range(len(event.tags)) if event.tags[i]["key"] == "display-name"][0]
        self.gui.write_to_chatbox(message, username)

    def send_privmsg(self, message):
        self.connection.privmsg(self.channel, message)
