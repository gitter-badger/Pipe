
from collections import defaultdict

class Packet(defaultdict):
  '����� ������ � ���� ������' 

  def __init__(self):
    defaultdict.__init__(list)
  pass



class Modem(object):
  '����� �������-������� ������ � �������'

  def __init__(self):
    pass

  def getPacket(self):
    '�������� ������� ������'
    p = Packet()
    return p

  def store(self, packet, dt):
    '���������� ������ ������ � ��'
    pass

  def hasCommand(self):
    return False

  def getCommand(self):
    return None



class Storage(object):

  def __init__(self):
    pass

  def getModem(self, modemId):
    '����� ������� ������ � �� �� ��� ������'
    m = Modem()
    m.id = 10020  # ������������� � ��
    return m


try:
  m = stor.getModem(modemId)

  p = m.getPacket()
  p['coord'] = (20020.34, 20300.23)
  p['speed'] = 102.3
  p['asimut'] = 1
  p['code'] = 8888

  m.store(p, dt)
  m.store(p)
except Exception as E:
  log.error(E)