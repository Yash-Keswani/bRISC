# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: template.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0etemplate.proto\"\xb0\x01\n\x06locker\x12!\n\x05locks\x18\x01 \x03(\x0b\x32\x12.locker.LocksEntry\x12%\n\x07waiting\x18\x02 \x03(\x0b\x32\x14.locker.WaitingEntry\x1a,\n\nLocksEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\x1a.\n\x0cWaitingEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x08:\x02\x38\x01\"\xb0\x01\n\tline_info\x12\x0b\n\x03lno\x18\x01 \x02(\x05\x12\x0c\n\x04srcs\x18\x02 \x03(\x05\x12\r\n\x05\x64\x65sts\x18\x03 \x03(\x05\x12 \n\x03out\x18\x04 \x03(\x0b\x32\x13.line_info.OutEntry\x12\x0b\n\x03opc\x18\x05 \x02(\x05\x12\x0b\n\x03\x63\x61t\x18\x06 \x02(\t\x12\x11\n\tline_text\x18\x07 \x02(\t\x1a*\n\x08OutEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\"O\n\rrunning_state\x12\x10\n\x08STALLING\x18\x01 \x02(\x08\x12\x11\n\tBRANCHING\x18\x02 \x02(\x08\x12\x19\n\x05lines\x18\x03 \x03(\x0b\x32\n.line_info\"s\n\x08\x65xecutor\x12\x14\n\x03mem\x18\x01 \x02(\x0b\x32\x07.memory\x12\x16\n\x03reg\x18\x02 \x02(\x0b\x32\t.registry\x12\x0c\n\x04size\x18\x03 \x02(\x05\x12\x0c\n\x04time\x18\x04 \x02(\x05\x12\x1d\n\x05state\x18\x05 \x02(\x0b\x32\x0e.running_state\"7\n\x06memory\x12\x1a\n\tall_locks\x18\x01 \x02(\x0b\x32\x07.locker\x12\x11\n\tmem_value\x18\x02 \x03(\x05\"\xa2\x01\n\x08registry\x12\x1a\n\tall_locks\x18\x01 \x02(\x0b\x32\x07.locker\x12\n\n\x02PC\x18\x02 \x02(\x05\x12\r\n\x05\x46LAGS\x18\x03 \x02(\x05\x12\x0c\n\x04regs\x18\x04 \x03(\x05\x12#\n\x05sregs\x18\x05 \x03(\x0b\x32\x14.registry.SregsEntry\x1a,\n\nSregsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01')



_LOCKER = DESCRIPTOR.message_types_by_name['locker']
_LOCKER_LOCKSENTRY = _LOCKER.nested_types_by_name['LocksEntry']
_LOCKER_WAITINGENTRY = _LOCKER.nested_types_by_name['WaitingEntry']
_LINE_INFO = DESCRIPTOR.message_types_by_name['line_info']
_LINE_INFO_OUTENTRY = _LINE_INFO.nested_types_by_name['OutEntry']
_RUNNING_STATE = DESCRIPTOR.message_types_by_name['running_state']
_EXECUTOR = DESCRIPTOR.message_types_by_name['executor']
_MEMORY = DESCRIPTOR.message_types_by_name['memory']
_REGISTRY = DESCRIPTOR.message_types_by_name['registry']
_REGISTRY_SREGSENTRY = _REGISTRY.nested_types_by_name['SregsEntry']
locker = _reflection.GeneratedProtocolMessageType('locker', (_message.Message,), {

  'LocksEntry' : _reflection.GeneratedProtocolMessageType('LocksEntry', (_message.Message,), {
    'DESCRIPTOR' : _LOCKER_LOCKSENTRY,
    '__module__' : 'template_pb2'
    # @@protoc_insertion_point(class_scope:locker.LocksEntry)
    })
  ,

  'WaitingEntry' : _reflection.GeneratedProtocolMessageType('WaitingEntry', (_message.Message,), {
    'DESCRIPTOR' : _LOCKER_WAITINGENTRY,
    '__module__' : 'template_pb2'
    # @@protoc_insertion_point(class_scope:locker.WaitingEntry)
    })
  ,
  'DESCRIPTOR' : _LOCKER,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:locker)
  })
_sym_db.RegisterMessage(locker)
_sym_db.RegisterMessage(locker.LocksEntry)
_sym_db.RegisterMessage(locker.WaitingEntry)

line_info = _reflection.GeneratedProtocolMessageType('line_info', (_message.Message,), {

  'OutEntry' : _reflection.GeneratedProtocolMessageType('OutEntry', (_message.Message,), {
    'DESCRIPTOR' : _LINE_INFO_OUTENTRY,
    '__module__' : 'template_pb2'
    # @@protoc_insertion_point(class_scope:line_info.OutEntry)
    })
  ,
  'DESCRIPTOR' : _LINE_INFO,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:line_info)
  })
_sym_db.RegisterMessage(line_info)
_sym_db.RegisterMessage(line_info.OutEntry)

running_state = _reflection.GeneratedProtocolMessageType('running_state', (_message.Message,), {
  'DESCRIPTOR' : _RUNNING_STATE,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:running_state)
  })
_sym_db.RegisterMessage(running_state)

executor = _reflection.GeneratedProtocolMessageType('executor', (_message.Message,), {
  'DESCRIPTOR' : _EXECUTOR,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:executor)
  })
_sym_db.RegisterMessage(executor)

memory = _reflection.GeneratedProtocolMessageType('memory', (_message.Message,), {
  'DESCRIPTOR' : _MEMORY,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:memory)
  })
_sym_db.RegisterMessage(memory)

registry = _reflection.GeneratedProtocolMessageType('registry', (_message.Message,), {

  'SregsEntry' : _reflection.GeneratedProtocolMessageType('SregsEntry', (_message.Message,), {
    'DESCRIPTOR' : _REGISTRY_SREGSENTRY,
    '__module__' : 'template_pb2'
    # @@protoc_insertion_point(class_scope:registry.SregsEntry)
    })
  ,
  'DESCRIPTOR' : _REGISTRY,
  '__module__' : 'template_pb2'
  # @@protoc_insertion_point(class_scope:registry)
  })
_sym_db.RegisterMessage(registry)
_sym_db.RegisterMessage(registry.SregsEntry)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _LOCKER_LOCKSENTRY._options = None
  _LOCKER_LOCKSENTRY._serialized_options = b'8\001'
  _LOCKER_WAITINGENTRY._options = None
  _LOCKER_WAITINGENTRY._serialized_options = b'8\001'
  _LINE_INFO_OUTENTRY._options = None
  _LINE_INFO_OUTENTRY._serialized_options = b'8\001'
  _REGISTRY_SREGSENTRY._options = None
  _REGISTRY_SREGSENTRY._serialized_options = b'8\001'
  _LOCKER._serialized_start=19
  _LOCKER._serialized_end=195
  _LOCKER_LOCKSENTRY._serialized_start=103
  _LOCKER_LOCKSENTRY._serialized_end=147
  _LOCKER_WAITINGENTRY._serialized_start=149
  _LOCKER_WAITINGENTRY._serialized_end=195
  _LINE_INFO._serialized_start=198
  _LINE_INFO._serialized_end=374
  _LINE_INFO_OUTENTRY._serialized_start=332
  _LINE_INFO_OUTENTRY._serialized_end=374
  _RUNNING_STATE._serialized_start=376
  _RUNNING_STATE._serialized_end=455
  _EXECUTOR._serialized_start=457
  _EXECUTOR._serialized_end=572
  _MEMORY._serialized_start=574
  _MEMORY._serialized_end=629
  _REGISTRY._serialized_start=632
  _REGISTRY._serialized_end=794
  _REGISTRY_SREGSENTRY._serialized_start=750
  _REGISTRY_SREGSENTRY._serialized_end=794
# @@protoc_insertion_point(module_scope)
