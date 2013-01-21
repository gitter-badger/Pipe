# -*- coding: utf8 -*-
'''
@project   Maprox <http://www.maprox.net>
@info      Naviset base class for other Naviset firmware
@copyright 2012, Maprox LLC
'''


import json
from struct import pack

from kernel.logger import log
from kernel.config import conf
from lib.handler import AbstractHandler
import lib.handlers.naviset.packets as packets
from urllib.parse import urlencode
from urllib.request import urlopen
from lib.ip import get_ip

# ---------------------------------------------------------------------------

class NavisetHandler(AbstractHandler):
    """
     Base handler for Naviset protocol
    """

    # private buffer for headPacket data
    __headPacketRawData = None

    def processData(self, data):
        """
         Processing of data from socket / storage.
         @param data: Data from socket
         @param packnum: Number of socket packet (defaults to 0)
         @return: self
        """
        protocolPackets = packets.PacketFactory.getPacketsFromBuffer(data)
        for protocolPacket in protocolPackets:
            self.processProtocolPacket(protocolPacket)

        return super(NavisetHandler, self).processData(data)

    def processProtocolPacket(self, protocolPacket):
        """
         Process naviset packet.
         @type protocolPacket: packets.Packet
         @param protocolPacket: Naviset protocol packet
        """
        self.sendAcknowledgement(protocolPacket)
        if not self.__headPacketRawData:
            self.__headPacketRawData = b''

        if isinstance(protocolPacket, packets.PacketHead):
            log.info('HeadPack is stored.')
            self.__headPacketRawData = protocolPacket.rawData
            self.uid = protocolPacket.deviceIMEI
            return

        observerPackets = self.translate(protocolPacket)
        if len(observerPackets) == 0:
            log.info('Location packet not found. Exiting...')
            return

        log.info(observerPackets)
        self._buffer = self.__headPacketRawData + protocolPacket.rawData
        self.store(observerPackets)

    def sendCommand(self, command):
        """
         Sends command to the tracker
         @param command: Command string
        """
        log.info('Sending "' + command + '"...')
        log.info('[IS NOT IMPLEMENTED]')

    def receiveImage(self, packet):
        """
         Receives an image from tracker.
         Sends it to the observer server, when totally received.
        """
        log.error('Image receiving...')
        log.info('[IS NOT IMPLEMENTED]')

    def translate(self, protocolPacket):
        """
         Translate gps-tracker data to observer pipe format
         @param protocolPacket: Naviset protocol packet
        """
        list = []
        if (protocolPacket == None): return list
        if not isinstance(protocolPacket, packets.PacketData):
            return list
        if (len(protocolPacket.items) == 0):
            return list
        for item in protocolPacket.items:
            packet = {'uid': self.uid}
            packet.update(item.params)
            packet['time'] = packet['time'].strftime('%Y-%m-%dT%H:%M:%S.%f')
            list.append(packet)
            #packet['sensors']['acc'] = value['acc']
            #packet['sensors']['sos'] = value['sos']
            #packet['sensors']['extbattery_low'] = value['extbattery_low']
            #packet['sensors']['analog_input0'] = value
        return list

    def sendAcknowledgement(self, packet):
        """
         Sends acknowledgement to the socket
         @param packet: a L{packets.Packet} subclass
        """
        buf = self.getAckPacket(packet)
        log.info("Send acknowledgement, crc = %d" % packet.crc)
        return self.send(buf)

    @classmethod
    def getAckPacket(cls, packet):
        """
         Returns acknowledgement buffer value
         @param packet: a L{packets.Packet} subclass
        """
        return b'\x01' + pack('<H', packet.crc)

    def processCommandExecute(self, task, data):
        """
         Execute command for the device
         @param task: id task
         @param data: data dict()
        """
        log.info('Observer is sending a command:')
        log.info(data)
        self.sendCommand(data['command'])

    def processCommandFormat(self, task, data):
        """
         Processing command to form config string
         @param task: id task
         @param data: request
        """
        data = json.loads(data)
        command0 = 'COM3 1234,' \
            + str(data['host'] or get_ip()) + ',' \
            + str(data['port'] or conf.port)
        command1 = 'COM13 1234,1,'+ str(data['gprs']['apn'] or '') \
            + ',' + str(data['gprs']['username'] or '') \
            + ',' + str(data['gprs']['password'] or '') \
            + '#'
        string = '{"list": ["' + command0 + '", "' + command1 + '"]}'
        log.debug('Formatted string result: ' + string)
        message = {
            'result': string,
            'id_action': task
        }
        log.debug('Formatted string sent: ' \
            + conf.pipeFinishUrl + urlencode(message))
        connection = urlopen(conf.pipeFinishUrl,
            urlencode(message).encode('utf-8'))

    def processCommandReadSettings(self, task, data):
        """
         Sending command to read all of device configuration
         @param task: id task
         @param data: data string
        """
        pass

    def processCommandSetOption(self, task, data):
        """
         Set device configuration
         @param task: id task
         @param data: data dict()
        """
        #current_db = db.get(self.uid)
        #if not current_db.isReadingSettings():
        #    pass
        pass

# ===========================================================================
# TESTS
# ===========================================================================

import unittest
#import time
class TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_packetData(self):
        import kernel.pipe as pipe
        h = NavisetHandler(pipe.Manager(), None)
        #data = b'\x01"\x00\x03868204000728070\x042\x00\xe0\x00\x00\x00\x00\xe1\x08Photo ok\x137'
        #protocolPackets = packets.PacketFactory.getPacketsFromBuffer(data)
        protocolPackets = []
        for packet in protocolPackets:
          self.assertEqual(packet.header, 1)