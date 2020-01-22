# -*- coding: UTF-8 -*-
#/**
# * Software Name : pycrate
# * Version : 0.4
# *
# * Copyright 2016. Benoit Michau. ANSSI.
# *
# * This library is free software; you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public
# * License as published by the Free Software Foundation; either
# * version 2.1 of the License, or (at your option) any later version.
# *
# * This library is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * Lesser General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with this library; if not, write to the Free Software
# * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, 
# * MA 02110-1301  USA
# *
# *--------------------------------------------------------
# * File Name : pycrate_asn1c/gen_pycrate_asn1rt.py
# * Created : 2016-12-21
# * Authors : Benoit Michau 
# *--------------------------------------------------------
#*/

import os
from os import listdir
from os.path import isfile, join,  isdir
from .utils  import *
from .glob   import *
from .setobj import *
from .refobj import *
from .asnobj import get_asnobj, ASN1Obj, INT, OID

class _Generator(object):
    
    def __init__(self, dest='/tmp/dst.txt'):
        self.dest = dest
        self.indent = 0
        pkg = self.dest
        p = pkg[::-1].index("/")
        p = len(pkg) - p
        self.dir = pkg[0:p-1]
        pmod = pkg[p:].lower()
        self.pkg = pmod
        if not os.path.isdir(self.dest):
            os.mkdir(self.dest)
        self.indent = 0
        self.gen()
        self.pgo2go(self.dest )
        
    
    def wrs(self, structName,  s):
        s += "\n"
        if structName not in self.structs:
            self.structs[structName] = s 
        else:
            self.structs[structName] += s

    def wrl(self, s):
        self.fd.write('{0}\n'.format(s))
    
    def gen(self):
        pass
        
    def pgo2go(self,  dir):
        defines = {}
        pgo = [f for f in listdir(dir) if isfile(join(dir, f))]
        for fn in pgo:
            if fn[-3:] != "pgo":
                continue
            fd = open(join(dir, fn), 'r')
            while True:
                l = fd.readline()
                if l == "":
                    break
                pos = l.find("//define:")
                if pos == -1:
                    continue
                l = l[pos+9:]
                pos = l.find(" ")
                if pos == -1:
                    continue
                name = l[:pos]
                val = l[pos+1:]
                defines[name] = val
            fd.close()

        for fn in pgo:
            if fn[-3:] != "pgo":
                continue
            fd = open(join(dir, fn), 'r')
            ofn = join(dir,  fn[:-3] + "go")
            ofd = open(ofn, 'w')
            while True:
                l = fd.readline()
                if l == "":
                    break
                pos = l.find("//define:")
                if pos != -1:
                    continue
                while True:
                    start = l.find("//replace:")
                    if start == -1:
                        break
                    v = l[start+10:]
                    pos = v.find(" ")
                    if pos == -1:
                        pos = len(v)
                    name = l[start+10 : (pos + start + 10)].strip()
                    if name in defines:
                        v = defines[name]
                        o = ""
                        if len(l) == start+pos+10:
                            o = l[0:start] + v 
                        else:
                            o = l[0:start] + v
                        l = o + l[(start+pos+10):]
                    else:
                        print("Unknown pre-processor name \"{0}\"\n".format(name))
                        break
                ofd.write(l)
            fd.close()
            ofd.close()

#------------------------------------------------------------------------------#
# Go source code generator
#------------------------------------------------------------------------------#
# generate Go source code 

_mode_lut = {
    'TYPE'              : 'MODE_TYPE',
    'SET'               : 'MODE_SET',
    'VALUE'             : 'MODE_VALUE'
    }

_tag_lut = {
    'IMPLICIT'          : 'TAG_IMPLICIT',
    'EXPLICIT'          : 'TAG_EXPLICIT',
    'CONTEXT-SPECIFIC'  : 'TAG_CONTEXT_SPEC',
    'PRIVATE'           : 'TAG_PRIVATE',
    'APPLICATION'       : 'TAG_APPLICATION',
    'UNIVERSAL'         : 'TAG_UNIVERSAL',
    'AUTOMATIC'         : 'TAG_AUTOMATIC'
    }

_type_lut = {
    'NULL'              : 'TYPE_NULL',
    'BOOLEAN'           : 'TYPE_BOOL',
    'INTEGER'           : 'TYPE_INT',
    'REAL'              : 'TYPE_REAL',
    'ENUMERATED'        : 'TYPE_ENUM',
    'BIT STRING'        : 'TYPE_BIT_STR',
    'OCTET STRING'      : 'TYPE_OCT_STR',
    'OBJECT IDENTIFIER' : 'TYPE_OID',
    'REALTIVE-OID'      : 'TYPE_REL_OID',
    #
    'IA5String'         : 'TYPE_STR_IA5',
    'PrintableString'   : 'TYPE_STR_PRINT',
    'NumericString'     : 'TYPE_STR_NUM',
    'VisibleString'     : 'TYPE_STR_VIS',
    'BMPString'         : 'TYPE_STR_BMP',
    'UTF8String'        : 'TYPE_STR_UTF8',
    'ISO646String'      : 'TYPE_STR_ISO646',
    'TeletexString'     : 'TYPE_STR_TELE',
    'VideotexString'    : 'TYPE_STR_VID',
    'GraphicString'     : 'TYPE_STR_GRAPH',
    'T61String'         : 'TYPE_STR_T61',
    'GeneralString'     : 'TYPE_STR_GENE',
    'UniversalString'   : 'TYPE_STR_UNIV',
    'ObjectDescriptor'  : 'TYPE_OBJ_DESC',
    #
    'GeneralizedTime'   : 'TYPE_TIME_GEN',
    'UTCTime'           : 'TYPE_TIME_UTC',
    #
    'CHOICE'            : 'TYPE_CHOICE',
    'SEQUENCE'          : 'TYPE_SEQ',
    'SEQUENCE OF'       : 'TYPE_SEQ_OF',
    'SET'               : 'TYPE_SET',
    'SET OF'            : 'TYPE_SET_OF',
    #
    'OPEN_TYPE'         : 'TYPE_OPEN',
    'ANY'               : 'TYPE_OPEN',
    'EXTERNAL'          : 'TYPE_EXT',
    'EMBEDDED PDV'      : 'TYPE_EMB_PDV',
    'CHARACTER STRING'  : 'TYPE_CHAR_STR',
    #
    'CLASS'             : 'TYPE_CLASS',
    'INSTANCE OF'       : 'TYPE_INSTOF' 
    }



class GoGenerator(_Generator):
    """
    PycrateGenerator generates Python source code to be loaded into the pycrate
    ASN.1 runtime, located in pycrate_asn1rt
    """
    
    def commentCode(self, o ):
        str = ""
        braceCount = 0
        parenCount = 0
        for a in o._text_def:
            if a == '{':
                if braceCount == 0:
                    str += a
                    a = "\n"
                braceCount += 1
            elif a == '}':
                if braceCount == 1:
                    str += "\n"
                braceCount-=1
            elif a == '(':
                parenCount+=1
            elif a == ')':
                parenCount -=1
            elif a == ',' and parenCount == 0:
                str += a
                a = "\n"
            str += a
        return "/*\n{0}\n*/\n".format(str)
        
    def gen_const_table(self, Obj):
        # table constraint: processing only a local and single constraint
        Consts_tab = [C for C in Obj._const if C['type'] == CONST_TABLE]
        if Consts_tab:
            if len(Consts_tab) > 1:
                asnlog('WNG, {0}.{1}: multiple table constraint, but compiling only the first'\
                       .format(self._mod_name, Obj._name))
            Const = Consts_tab[0]
            # If the table lookup has not been saved, save it 
            indexName = Obj._typeref.ced_path[-1]
            table = Obj._typeref.called[-1]
            root = C['tab']['val']['root'] 
            ext = C['tab']['val']['ext']
            if table not in self.tables:
                tbl = {}
                tbl['name'] = table
                tbl['idx'] = indexName
                tbl["root"] =root
                tbl['ext'] = ext
                self.tables[table] = tbl 
            '''           
            #ConstTab = Const['tab']
            link_name = None
            # check if the same constraint was already defined somewhere in the root object
            if hasattr(self, '_const_tabs'):
                ConstTabVal = Const['tab'].get_val()
                for ct in self._const_tabs:
                    # HOLLY PYTHON: comparing damned complex dict values...
                    if ConstTabVal == ct[1]:
                        # the table of values get already compiled, just need to link it
                        link_name = ct[0]
                        break
            if link_name is None:
                # create the table set object
                Const['tab']._pyname = '_{0}_tab'.format(Obj._pyname)
                self.gen_set(Const['tab'])
                link_name = Const['tab']._pyname
                if not hasattr(self, '_const_tabs'):
                    self._const_tabs = [(link_name, Const['tab'].get_val())]
                else:
                    self._const_tabs.append( (link_name, Const['tab'].get_val()) )
                    '''

    def buildConstraint(self,  Obj):
        c = {}
        str = ""
        constraint = Obj.get_const()
        if len(constraint)== 0:
            return ""
        constraint = constraint[-1]
        if constraint['type'] == 'VAL':
            range = constraint['text']
            str = 'range:"{0}"'.format( range)
            c["val"] = range
        elif constraint['type'] == 'SIZE':
            range = constraint['root'][-1]
            if isinstance(range, ASN1RangeInt):
                str = 'length:"{0}..{1}"'.format( range.lb,  range.ub)
                c["val"] = '{0}..{1}'.format( range.lb,  range.ub)
            else:
                str = 'length:"{0}"'.format( range)
                c["val"] = range
        # Modifiers?
        if Obj.is_opt():
            str += " mod:\"optional\""
        c["tag"] = str
        return c
        
    def writeType(self,  fd,  Obj):
        objName = name_to_golang(Obj._name,  True)
        if objName in self.defines:
            fd.write(" //replace:{0}".format(objName))
            return
        if Obj.TYPE=="SEQUENCE":
            fd.write("*{0}".format(objName))
        elif Obj.TYPE == "INTEGER":
            tag = ""
            if Obj.get_classref() is not None:
                tag += " table:\"{0}\" ".format(Obj.get_classref()._name)
            tag += self.buildConstraint(Obj)["tag"]
            if tag != "":
                fd.write("{0} `{1}`".format(objName,  tag.strip()))
            else:
                fd.write("{0} ".format(objName))
        elif Obj.TYPE == "OBJECT IDENTIFIER":
            fd.write("[]byte `array:\"x\"` ")
        elif Obj.TYPE == "OPEN_TYPE":
            fd.write("interface{} `type:\"table\"` ")
        elif Obj.TYPE == "BIT STRING":
            fd.write("uint64 `type:\"bitstring\" {0}`".format(self.buildConstraint(Obj)["tag"]))
        elif Obj.TYPE == "SEQUENCE OF":
            # Do mod spearately since we are only using the constraint val
            mod = ""
            if Obj.is_opt():
                mod="mod:\"optional\""
            fd.write("[]{0} `array:\"{1}\" {2}`".format(name_to_golang(Obj.get_typeref()._name, True),  self.buildConstraint(Obj)["val"],  mod))
        elif Obj.TYPE == "OCTET STRING":
            mod = ""
            c = self.buildConstraint(Obj)
            # No constraints on octet string still requires array definition
            if Obj.is_opt():
                mod="mod:\"optional\""
            if c == "":  
                fd.write("[]byte `array:\"x\" {0}`".format(mod))
            else:
                fd.write("[]byte `array:\"{0}\" {1}`".format(c["val"],  mod))
        elif Obj.TYPE == "ENUMERATED":
            if Obj.get_typeref() is not None:
                fd.write("//replace:{0}".format(name_to_golang(Obj.get_typeref()._name,  True)))
            else:
                str = "`type:\"enum("
                comma = False
                for a in Obj.get_root():
                    if comma:
                        str += ","
                    comma = True
                    str += name_to_golang(a, True)
                str += ")\"`"
                fd.write("int {0}".format(str))
        else:
            fd.write(" //UNHANDLED TYPE {0}".format(Obj.TYPE))                

    def writeChoice(self,  fd,  Obj):
        fd.write("type {0} struct {{\n\tAsnCHOICE\n".format(name_to_golang(Obj._name,  True)))
        ext = ""
        if Obj._ext is not None:
            if len(Obj._ext) == 0:
                ext = "!!!PLACE_AT_END!!!"
            else:
                ext = Obj._ext[-1]
        for c in Obj._cont:
            child = Obj._cont[c]
            childName = name_to_golang(child._name,  True)
            if ext == child._name:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            fd.write("\t{0}  ".format(childName))
            self.writeType(fd,  child)
            fd.write("\n")
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")

    def writeSequence(self,  fd,  Obj):
        fd.write("type {0} struct {{\n\tAsn\n".format(name_to_golang(Obj._name,  True)))
        ext = ""
        if Obj._ext is not None:
            if len(Obj._ext) == 0:
                ext = "!!!PLACE_AT_END!!!"
            else:
                ext = Obj._ext[-1]
        for c in Obj._cont:
            child = Obj._cont[c]
            childName = name_to_golang(child._name,  True)
            if ext == child._name:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            fd.write("\t{0}  ".format(childName))
            self.writeType(fd,  child)
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")

    def writeSequenceOf(self,  fd,  Obj):
        fd.write("type {0} struct {{\n\tAsn\n".format(name_to_golang(Obj._name,  True)))
        ext = ""
        if Obj._ext is not None:
            if len(Obj._ext) == 0:
                ext = "!!!PLACE_AT_END!!!"
            else:
                ext = Obj._ext[-1]
        if Obj._cont is not None:
            child = Obj._cont
            childName = name_to_golang(child._name,  True)
            if ext == child._name:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            fd.write("\t{0}  []".format(childName))
            self.writeType(fd,  child)
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")
                
    def gen(self):
        self.tables = {}
        self.fieldTypes = {}
        self.structs = {}
        self.defines = {}
        modlist = []
        # Constants and basic types and enumerations
        fd = open(self.dest + "/consts.pgo", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            modName = name_to_defin(mod_name).lower()
            self._mod_name = mod_name
            pymodname = name_to_defin(mod_name)
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            modWritten = False
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                str = self.gen_const_table(Obj)
                goName = name_to_golang(obj_name,  True)
                if (Obj.TYPE != "INTEGER" and Obj.TYPE != "ENUMERATED") or Obj._mode == MODE_SET:
                    continue
                if modWritten == False:
                    modWritten = True
                    fd.write("/*******************************\n")
                    fd.write("**** Module {0}\n".format(mod_name))
                    fd.write("********************************/\n")
                if Obj._mode == MODE_VALUE:
                    fd.write('\n// {0} {1}\n'.format(obj_name,  Obj.get_typeref()))
                    itype = "int"
                    if Obj._typeref != None:
                        itype =  name_to_golang(Obj._typeref.called[-1],  True)
                    fd.write('const {0} {1} = {2}\n'.format(goName, itype,  Obj._val))
                elif Obj._mode == MODE_TYPE:
                    if Obj.get_root() == None:
                        # Basic type?
                        if Obj.TYPE == "INTEGER":
                            fd.write("type {0} int64\n".format(goName))
                        else:
                            fd.write("type {0} UNKNOWN {1}\n".format(goName. Obj.TYPE))
                        continue
                    # Must be enum?
                    str = "`type:\"enum("
                    comma = False
                    for a in Obj.get_root():
                        if comma:
                            str += ","
                        comma = True
                        str += name_to_golang(a, True)
                    str += ")\"`"
                    fd.write('//define:{0} int64 {1}\n'.format(goName,  str))
                    self.defines[goName] = True
                else:
                    fd.write("\n// {0}\n{1}".format(obj_name,  self.commentCode(Obj)))
                    fd.write('type {0} int64\n'.format(goName))
                    # Constraints?
                    constraint = Obj.get_const()
                    if constraint[-1]['type'] == 'VAL':
                        range = constraint[-1]['text']
                        fd.write('//define:{0} int64 `range:"{1}"`\n'.format(goName,  range))
                        self.defines[goName] = True
                continue
        fd.close()

        # Structs
        fd = open(self.dest + "/structs.pgo", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write('import (')
        fd.write('\t. "asn2gort"')
        fd.write(')\n\n')
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            pymodname = name_to_defin(mod_name)
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            fd.write("\n/*******************************\n")
            fd.write("**** Module {0}\n".format(mod_name))
            fd.write("********************************/\n")
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                if obj_name == "s1Setup":
                    pass
                if Obj._mode == MODE_SET or Obj._mode == MODE_VALUE or Obj.TYPE == "CLASS":
                    continue
                fd.write('\n/* {0}, Mode {1}, TYPE {2}, Param {3}  */\n'.format(obj_name,  Obj._mode,  Obj.TYPE,  Obj.get_param()))
                fd.write(self.commentCode(Obj))
                #if Obj.get_param() is not None:
                #    continue
                if Obj._mode == MODE_TYPE:
                    if Obj.TYPE == "CHOICE":
                        self.writeChoice(fd,  Obj)
                    elif Obj.TYPE == "SEQUENCE":
                        self.writeSequence(fd,  Obj)
                    elif Obj.TYPE == "SEQUENCE OF":
                        self.writeSequenceOf(fd,  Obj)
            modlist.append(pymodname)
        fd.close()
        '''
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            pymodname = name_to_defin(mod_name)
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            modWritten = False
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                self.gen_const_table(Obj)
        '''
        fd = open(self.dest + "/tables.pgo", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write('import (')
        fd.write('\t. "asn2gort"')
        fd.write(')\n\n')
        fd.write('// Table lookups\n')
        fd.write('func init() {\n')
        # All of out tables for lookup
        for tbl in self.tables:
            c = self.tables[tbl]
            root = c['root']
            idx = c['idx']
            # Runs through each member of the set
            for a in root:
                # Parameterized?
                if isinstance(a,  ASN1RefSet):
                    pass
                else:
                    index = a[idx]
                    # Now we must run through each item
                    # Each item in a set can specify one or more Types, we save these
                    # Each item in a set can specify zero or more values, save these also
                    structRef = {}
                    valRef = {}
                    for b in a:
                        if b == idx:
                            continue
                        x = a[b]
                        if b[0] >= 'A' and b[0] <='Z':
                            structRef[b] = x._typeref.called[-1]
                        else:
                            valRef[b] = name_to_golang(x, True)
                    # Now we can instantiate the Go struct for this lookup with the specified values
                    for x in structRef:
                        struct = "{0}{{".format(x)
                        # Add default values
                        vals = ""
                        for y in valRef:
                            vals += "{0}:{1}, ".format(name_to_golang(y, True), valRef[y])
                        vals += "Value:{0}{{}}".format(structRef[x])
                        struct += vals + "}"
                        fd.write("\tAddTableRef(\"{0}_{1}\", {2}, {3})\n".format(tbl,  x,  index,  struct))
        fd.write('}')
        fd.close()
