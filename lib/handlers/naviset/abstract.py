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
            self.uid = protocolPacket.deviceImei
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
        log.info("Send acknowledgement, checksum = %d" % packet.checksum)
        return self.send(buf)

    @classmethod
    def getAckPacket(cls, packet):
        """
         Returns acknowledgement buffer value
         @param packet: a L{packets.Packet} subclass
        """
        return b'\x01' + pack('<H', packet.checksum)

    def processCommandExecute(self, task, data):
        """
         Execute command for the device
         @param task: id task
         @param data: data dict()
        """
        log.info('Observer is sending a command:')
        log.info(data)
        self.sendCommand(data['command'])

    def getInitiationData(self, config):
        """
         Returns initialization data for SMS wich will be sent to device
         @param config: config dict
         @return: array of dict or dict
        """
        command0 = 'COM3 1234,' + config['host'] + ',' + str(config['port'])
        command1 = 'COM13 1234,1,'+ config['gprs']['apn'] \
            + ',' + config['gprs']['username'] \
            + ',' + config['gprs']['password'] + '#'
        return [{
            "message": command0
        }, {
            "message": command1
        }]

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
        config = h.getInitiationConfig({
            "identifier": "0123456789012345",
            "host": "trx.maprox.net",
            "port": 21200
        })
        data = h.getInitiationData(config)
        self.assertEqual(data, [{
            'message': 'COM3 1234,trx.maprox.net,21200'
        }, {
            'message': 'COM13 1234,1,,,#'
        }])
        message = h.getTaskData(321312, data)
        self.assertEqual(message, {
            "id_action": 321312,
            "data": json.dumps(data)
        })