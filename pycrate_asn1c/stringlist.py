

class StringList:
  name = ""

  def __init__(self, name):
    self.name = name
    self.l = []
    self.l.append("// Created by pycrate Go {0}".format(name))

  def write(self, str):
    self.l.append(str)

  def reset(self):
    self.l = []

  def items(self):
    return self.l