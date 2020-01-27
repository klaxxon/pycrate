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
import subprocess

def svnversion():
    p = subprocess.Popen("svnversion", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    return stdout

class _Generator(object):
    
    def __init__(self, dest='/tmp/dst.txt'):
        self.revision = svnversion()
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

class GoField():
    def __init__(self,  ctxt):
        self.name = ""
        self.type = ""
        # Tags are tags["range"] = "1..10"
        self.Used = False
        self._text_def = ctxt
        self.saveAsStruct = False
        self.tags = {} 

class GoTable():
    def __init__(self):
        self.table = ""
        self.indexFieldName = ""
        self.itable = False
        
class GoSet():
    def __init__(self):
        self.name = ""
        self.typName = ""
        self.modName = ""
        self.objNames = []
        
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
        # Is this a table index (@id), save it for later
        Consts_tab = [C for C in Obj._const if C['type'] == CONST_TABLE]
        if Consts_tab:
            if len(Consts_tab) > 1:
                asnlog('WNG, {0}.{1}: multiple table constraint, but compiling only the first'\
                       .format(self._mod_name, Obj._name))
            Const = Consts_tab[0]
            if Const["at"] is None:
                name =Obj._typeref.ced_path[-1]
                tableName = Obj._typeref.called[-1]
                #self.tableIndexNames[tableName] = name
        if Obj._name == "CellTrafficTrace":
            pass
        # Only interested in top level structs
        if Obj._parent is None:
            if hasattr(Obj._cont,  "__iter__"):
                # Does this object reference a SET?
                for aid in Obj._cont:
                    a = Obj._cont[aid]
                    if not hasattr(a, "_ref"):
                        continue
                    fieldName = a._name
                    fieldType = None
                    params = None
                    for ref in a._ref:
                        if isinstance(ref,  ASN1RefSet):
                            params = ref.called[-1]
                        elif isinstance(ref,  ASN1RefType):
                            fieldType = name_to_golang(ref.called[-1],  True)
                    if params not in self.setToStruct:
                        self.setToStruct[params] = []
                    if fieldType is None:
                        pass
                    o = {}
                    o["fieldName"] = fieldName
                    o["fieldType"] = fieldType
                    o["structName"] = Obj._name
                    self.setToStruct[params].append(o)
        if Obj._mode != MODE_SET:
            return
        # Save the contents of this set for later    
        if Obj._ref is not None:
            o = GoSet()
            val = Obj.get_val()
            o.name = Obj._name
            o.typName = Obj.get_typeref()._name
            o.modName = Obj._mod
            if val["root"] is not None:
                o.objNames += val["root"]
            if val["ext"] is not None:
                o.objNames += val["ext"]
            self.sets[Obj._mod + "." + Obj._name] = o
            pass
                    
    def gen_set(self, Obj):
        #
        # generate the type first
        #self.gen_type(Obj, compts=False)
        #
        # in case this is a parameterized object, no need to defined anything more
        if Obj._param:
            return
        #
        # now generate the set of values
        #self.wrl('{0}._val1 = {1}'.format(Obj._pyname, set_to_defin(ASN1Set(Obj._val), Obj, self)))

    def buildConstraint(self,  Obj):
        c = {}
        constraint = Obj.get_const()
        if len(constraint)== 0:
            return c
        # Any table reference? Maybe this is the lookup key?
        for a in constraint:
            if "at" in a:
                if a["at"] is None:
                    c["itableIdx"] = "1"
        constraint = constraint[-1]
        if constraint['type'] == 'VAL':
            c["range"] = constraint['text']
        elif constraint['type'] == 'SIZE':
            range = constraint['root'][-1]
            if isinstance(range, ASN1RangeInt):
                c["length"] = '{0}..{1}'.format( range.lb,  range.ub)
            else:
                c["length"] = range
                
        # Modifiers?
        if Obj.is_opt():
            c["mod"] = "optional"
        return c
       
    def lookupSimpleDefined(self,  name):
        stype = GoField("")
        if name in self.simpleTypes:
            stype = self.simpleTypes[name]
        if name in self.defined:
            if stype.type != name:
                stype.type = name
        return stype
    
    def getTags(self,  Obj):    
        tags = self.buildConstraint(Obj)
        tableRef = None
        if Obj._parent is not None:
            tblName =  Obj._parent._name + "." + Obj._parent._mod
            if tblName in self.tables:
                tableRef = self.tables[tblName]
                if tableRef.itable:
                    tags["itable"] = tableRef.table
                else:
                    if Obj._name == tableRef.indexFieldName:
                        tags["table"] = tableRef.table
                    else:
                        tags["lut"] = "table"
        if Obj.is_opt():
            tags["mod"]  = "optional"
        return tags
    
    def writeType(self,  fd,  Obj,  gft = None):
        objName = name_to_golang(Obj._name,  True)
        objType =objName
        # This could be an array of something where we get _item_ for a name.  If so resolve to the array type
        if Obj._typeref is not None:
            if  objName == "_item_":
                objType = name_to_golang(Obj._typeref.called[-1],  True)
            if objType in self.simpleTypes:
                stype = self.simpleTypes[objType]
                stype.tags.update(self.getTags(Obj))
                type = stype.type
                # If this type has been defined already, use the actual type
                if objName in self.defined:
                    type = objName
                fd.write(" {0} {1}".format(type,  formatTags(stype.tags)))
                return 
        if Obj._type==TYPE_SEQ  or Obj._type == TYPE_CHOICE:
            if Obj.get_refchain is not None:
                n = name_to_golang(Obj.get_refchain()[-1]._name,  True)
                fd.write("*{0}".format(n))
            else: 
                fd.write("*{0}".format(objType))
        elif Obj._type == TYPE_SEQ_OF:
            if Obj.get_cont() is not None:
                ref = Obj.get_cont()._typeref.called[-1]
                gref = name_to_golang(ref,  True)
                if gref in self.simpleTypes:
                    self.simpleTypes[gref].Used = True
                n = name_to_golang(ref,  True)
                tags = formatTags(self.getTags(Obj))
                if "length" not in tags:
                    tags["length"] = "x"
                fd.write("[]{0} {1}".format(n,  tags))
            else:
                n = name_to_golang(Obj.get_refchain()[0]._name,  True)
                fd.write("[]{0}".format(n))
        elif Obj._type == TYPE_INT:
            if objType not in self.defined:
                objType = "int"
            tags =self.getTags(Obj)
            tag = formatTags(tags)
            fd.write("{0} {1}".format(objType,  tag.strip()))
        elif Obj._type == TYPE_OID:
            fd.write("[]byte `length:\"x\"` ")
        elif Obj._type == TYPE_OPEN:
            tags =self.getTags(Obj)
            tag = formatTags(tags)
            fd.write("interface{{}} {0}".format(tag))
        elif Obj._type == TYPE_BIT_STR:
            tags = self.getTags(Obj)
            tags["type"] = "bitstring"
            fd.write("uint64 {0}".format(formatTags(tags)))
        elif Obj._type == TYPE_SEQ_OF:
            tags = self.getTags(Obj)
            n = name_to_golang(Obj.get_typeref()._name, True)
            fd.write("[]{0} {2}".format(n,  formatTags(tags),  mod))
        elif Obj._type == TYPE_OCT_STR:
            tags = self.getTags(Obj)
            tags["type"] = "octetstring"
            if "length" not in tags:
                tags["length"] = "x"
            fd.write("[]byte {0}".format(formatTags(tags)))
        elif Obj._type == TYPE_ENUM:
            if Obj.get_typeref() is not None:
                typeName = name_to_golang(Obj.get_typeref()._name,  True)
                if Obj.get_typeref()._typeref is not None:
                    typeName = name_to_golang(Obj.get_typeref()._typeref.called[-1] ,  True)
                if typeName in self.simpleTypes:
                    tags =  self.simpleTypes[typeName].tags
                    n = name_to_golang(typeName,  True)
                    fd.write("{0} {1}".format(n,  formatTags(tags)))
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
        elif Obj._type == TYPE_NULL:
            fd.write("interface{} `type:\"null\"`")
        else:
            fd.write(" //UNHANDLED TYPE {0}".format(Obj.TYPE))             
        return    

    def writeChoice(self,  fd,  Obj):
        fd.write("type {0} struct {{\n\tAsnCHOICE\n".format(name_to_golang(Obj._name,  True)))
        ext = ""
        if Obj._ext is not None:
            if len(Obj._ext) == 0:
                ext = "!!!PLACE_AT_END!!!"
            else:
                ext = Obj._ext
        for c in Obj._cont:
            child = Obj._cont[c]
            childName = name_to_golang(child._name,  True)
            if child._name in ext:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            fd.write("\t{0}  ".format(childName))
            self.writeType(fd,  child)
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")
        return 

    def writeSequence(self,  fd,  Obj):
        fd.write("type {0} struct {{\n\tAsn\n".format(name_to_golang(Obj._name,  True)))
        ext = ""
        if Obj._ext is not None:
            if len(Obj._ext) == 0:
                ext = "!!!PLACE_AT_END!!!"
            else:
                ext = Obj._ext
        for c in Obj._cont:
            child = Obj._cont[c]
            childName = name_to_golang(child._name,  True)
            if child._name in ext:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            fd.write("\t{0}  ".format(childName))
            self.writeType(fd,  child)
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")
        return 

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
            #childName = name_to_golang(child._name,  True)
            childType = None
            if child._typeref is not None:
                childType = name_to_golang(child._typeref.called[-1],  True)
            if ext == child._name:
                fd.write("\tAsnEXTENSION\n")
                ext = ""
            childType = name_to_golang(childType,  True)
            stype = self.lookupSimpleDefined(childType)
            if stype.type != "":
                childType = stype.type
            else:
                childType = "*" + childType
            fd.write("\tItem  []{0}".format(childType))
            tags = self.buildConstraint(Obj)
            # No constraints on octet string still requires array definition
            if "length" not in tags:  
                fd.write("`length:\"x\" {0}".format(buildTags(tags)))
                self.saveFieldType(Obj,  "[]byte")
            else:
                fd.write(" {0}".format(formatTags(tags)))
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")
        
    def setSimpleType(self,  st):
        if st.name in self.simpleTypes:
            print("{0} already defined {1}\n",  st.name,  self.simpleTypes[st.name])
            return
        self.simpleTypes[st.name] = st
        
    # Checks the type of fieldName in Obj and if enum, prefixes with Obj._name
    def getEnumPrefix(self,  Obj,  fieldName):
        clsName = Obj.get_refchain()
        if clsName is None:
            return None
        clsName = clsName[-1]._name
        cls = self.classes[clsName]
        if fieldName not in cls._cont:
            print("Field name {0} not in class {2}".format(fieldName,  clsName))
            return None
        fld = cls._cont[fieldName]
        if fld._type != TYPE_ENUM:
            return None
        enumName = fld.get_refchain()[-1]._name
        return enumName
        
    def gen(self):
        #self.objs = {}
        self.tables = {}
        #self.fieldTypes = {}
        self.defined = {}  # Types already defined
        #self.structs = {}
        self.simpleTypes = {}
        self.sets = {} # List of sets for the given class
        #self.tableIndexNames = {} # Given the class, this is the index field name
        #self.classToStructName = {} # For the class name has dict of object name and their type
        self.setToStruct = {} # For the set name, which structs are using it
        #self.fieldToType = {} # struct.field = fieldtype
        #self.classes = {} # Class name to object
        
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            modWritten = False
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                str = self.gen_const_table(Obj)
                if Obj._param is not None and Obj._mode == MODE_TYPE:
                    name = "###" + Obj._name
                    if name in self.sets:
                        panic
                    self.sets[name] = Obj

        # Don't write, save them since some may need to be removed because they are structs or whatnot
        const = {}
        # Constants and basic types and enumerations
        # Constants are written out to the consts.go file.
        # All other basic types are saved for use later.
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                goName = name_to_golang(obj_name,  True)
                if (Obj._type != TYPE_INT and Obj._type != TYPE_OCT_STR  and Obj._type != TYPE_BIT_STR and Obj._type != TYPE_ENUM and Obj._type != TYPE_STR_PRINT) or Obj._mode == MODE_SET:
                    continue
                str = ""
                constraint = self.getTags(Obj)
                if Obj._mode == MODE_VALUE:
                    str += '\n// {0} {1}\n'.format(obj_name,  Obj.get_typeref())
                    itype = "int"
                    if Obj._typeref != None:
                        itype =  name_to_golang(Obj._typeref.called[-1],  True)
                    str += 'const {0} {1} = {2}\n'.format(goName, itype,  Obj._val)
                    self.defined[stype.name] = stype
                elif Obj._mode == MODE_TYPE:
                    if Obj.get_root() == None:
                        # Basic type?
                        if Obj._type== TYPE_INT:
                            #fd.write("type {0} int64\n".format(goName))
                            stype = GoField(Obj._text_def)
                            stype.name = goName
                            stype.tags.update(constraint)
                            stype.type = "int"
                            self.setSimpleType(stype)
                            str += 'type {0} {1}\n'.format(goName, stype.type)
                            # Basic type but also defined (const)
                            self.defined[stype.name] = stype
                        elif Obj._type == TYPE_OCT_STR:
                            tags = self.getTags(Obj)
                            if "length" not in tags:
                                tags["length"] = "x"
                            str += "type {0} struct {{\n\tValue []byte {1}\n}}\n\n".format(goName,  formatTags(tags))
                        elif Obj._type == TYPE_BIT_STR:
                            stype = GoField(Obj._text_def)
                            stype.name = goName
                            stype.tags.update(constraint)
                            stype.type = "uint64"
                            self.setSimpleType(stype)
                        elif Obj._type == TYPE_STR_PRINT:
                            stype = GoField(Obj._text_def)
                            stype.name = goName
                            stype.tags["type"] = "printablestring" 
                            stype.tags.update(constraint)
                            stype.type = "string"
                            self.setSimpleType(stype)
                        else:
                            fd.write("type {0} UNKNOWN {1}\n".format(goName,  Obj.TYPE))
                    else:
                        # Must be enum?
                        str2 = "enum("
                        comma = False
                        for a in Obj.get_root():
                            if comma:
                                str2 += ", "
                            comma = True
                            str2 += name_to_golang(a, True)
                        if Obj.get_ext() is not None:
                            if comma:
                                str2 += ", "
                            str2 += "..."
                            for a in Obj.get_ext():
                                str2 += ", "
                                str2 += name_to_golang(a, True)
                        str2 += ")"
                        stype = GoField(Obj._text_def)
                        stype.name = goName
                        stype.tags["type"] = str2
                        stype.type = "int"
                        self.setSimpleType(stype)
                        str +='type {0} {1}\n'.format(goName, stype.type)
                        str += "const (\n"
                        idx = 0
                        for a in Obj.get_root():
                            str += "\t{1}_{0} {1} = {2}\n".format(name_to_golang(a,  True), goName,  idx)
                            idx += 1
                        str += ")\n"
                        self.defined[stype.name] = stype
                else:
                    stype = GoField(Obj._text_def)
                    stype.name = goName
                    str += "\n// {0}\n{1}".format(obj_name,  self.commentCode(Obj))
                    #fd.write('type {0} int64\n'.format(goName))
                    # Constraints?
                    stype.tags.update(constraint)
                    stype.type = "int"
                    self.setSimpleType(stype)
                if str != "":
                    const[goName] = str
        
        

        fd = open(self.dest + "/tables.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write('import (')
        fd.write('\t. "asn2gort"')
        fd.write(')\n\n')
        fd.write("// PyCrate GoGenerator revision {0}\n".format(self.revision))
        fd.write('// Table lookups\n')
        fd.write('func init() {\n')        
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                if Obj._type == TYPE_CLASS:
                    continue
                # Search through the objects contents for a field with reference to a set
                refset = None
                # Return the ref set field names
                refchild = []
                if Obj._ref is not None:
                    for a in Obj._ref:
                        if isinstance(a,  ASN1RefSet):
                            # Found it, return the name of set
                            refset = a.called[0] + "." + a.called[1]
                        elif isinstance(a,  ASN1RefClassField):
                            fldName = a.ced_path[0]
                            refchild.append(fldName)
                if refset is None:
                    continue
                refClass = False
                if hasattr(Obj,  "_ref"):
                    if Obj._ref is not None:
                        refCnt = 0
                        for a in Obj._ref:
                            if isinstance(a,  ASN1RefClassField) or isinstance(a, ASN1RefSet):
                                refCnt+=1
                        if refCnt == len(Obj._ref):
                            refClass = True
                # We have the object struct and the set it references, now all we do is create a lookup table entry with the default values.
                # Obj = Who we are adding table lookup
                # refset = Name of the set we will iterate over to add the specific table lookups and default values
                rset = self.sets[refset]
                # rset = Struct holding list of set properties including list of objects with default values
                if refClass:
                    for setInst in rset.objNames:
                        valStruct = ""
                        instName = ""
                        # Some of the fields in the lup structure may not apply to the type (refchild) so we ignore them
                        cont = Obj.get_cont()
                        if not hasattr(cont,  "__iter__"):
                            continue
                        # If this has a subtype, assume we are instance based on table line []ProtocolIEs and not populating a named instance like InitiatingMessage.
                        #if fld.get_cont() is not None:
                        #    instName = fld.get_cont()._typeref.called[-1]
                        id = None
                        instName = None
                        ifFieldName = None
                        for a in cont:
                            fld = cont[a]
                            fldName = name_to_golang(fld._name,  True)
                            refname = fld.get_refchain()[-1]._name
                            # Special case for value in open types: If the refname is in the setInst, then use it as a value
                            if refname in setInst:
                                instName = refname
                                # If this is referencing another type, use it
                                valRef = setInst[refname]._typeref
                                iName = valRef.called[-1]
                                valStruct += "{0}:{1}{{}},".format(fldName,  name_to_golang(iName, True))
                                # If valRef is in simpleTypes, set flag so it is saved as a struct, not a simple type
                                if valRef in self.simpleTypes:
                                    self.simpleTypes[valRef].saveAsStruct = True
                                continue
                            if fld._name not in setInst:
                                continue
                            val = setInst[fld._name]
                            # Table ID?
                            if fld._const[0]["at"] is None:
                                id = val
                                idFieldName = a
                            # If the type is ENUM, we need to add the name to the beginning
                            if fld._type == TYPE_ENUM:
                                ename = fld.get_refchain()[0]._typeref.called[-1]
                                val = ename + "_" + name_to_golang(val,  True)
                            valStruct += "{0}:{1},".format(fldName,  val)
                            #print("Field name {0} = {1}, {2}".format(fld._name,  refname,  defStruct))
                        # If instName is None, there is no mapping to this enty
                        if instName is not None:
                            valStruct = "{0}{{{1}}}".format(instName,  valStruct[:-1])
                            tblName = instName + "." + rset.modName
                            fd.write("AddTableRef(\"{0}\",{1},{2})\n".format(tblName,  id,  valStruct))
                            o = GoTable()
                            o.table = tblName
                            o.itable = False
                            o.indexFieldName = idFieldName
                            self.tables[o.table] = o
                else:
                    # In this case we are doing a lookup for each field mapped to a table
                    cont = Obj.get_cont()
                    if not hasattr(cont,  "__iter__"):
                        continue
                    for fname in cont:
                        fldType = None
                        fld = cont[fname]
                        c = fld.get_cont()
                        if c is not None:
                            if hasattr(c,  "_typeref"):
                                fldType = c._typeref.called[-1]
                                break
                    if fldType == None:
                        continue
                    className = "###" + fldType
                    if className not in self.sets:
                        print("Could not find field definition for {0} in self.sets".format(className))
                        continue
                    classCont = self.sets[className]
                    for setInst in rset.objNames:
                        valStruct = ""
                        instName = ""
                        # Some of the fields in the lup structure may not apply to the type (refchild) so we ignore them
                        cont = classCont.get_cont()
                        if not hasattr(cont,  "__iter__"):
                            continue
                        # If this has a subtype, assume we are instance based on table line []ProtocolIEs and not populating a named instance like InitiatingMessage.
                        #if fld.get_cont() is not None:
                        #    instName = fld.get_cont()._typeref.called[-1]
                        id = None
                        instName = None
                        idFieldName = None
                        for a in cont:
                            fld = cont[a]
                            fldName = name_to_golang(fld._name,  True)
                            refname = fld.get_refchain()[-1]._name
                            # Special case for value in open types: If the refname is in the setInst, then use it as a value
                            if refname in setInst:
                                instName = refname
                                # If this is referencing another type, use it
                                if setInst[refname]._typeref is None:
                                    valRef = name_to_golang(setInst[refname]._type,  True)
                                    valStruct += "{0}:{1}{{}},".format(fldName,  valRef)
                                else:
                                    valRef = name_to_golang(setInst[refname]._typeref.called[-1],  True)
                                    valStruct += "{0}:{1}{{}},".format(fldName,  valRef)
                                    # If valRef is in simpleTypes, set flag so it is saved as a struct, not a simple type
                                    if valRef in self.simpleTypes:
                                        self.simpleTypes[valRef].saveAsStruct = True
                                continue
                            if fld._name not in setInst:
                                continue
                            val = setInst[fld._name]
                            # Table ID?
                            if fld._const[0]["at"] is None:
                                id = val
                                idFieldName = a
                            # If the type is ENUM, we need to add the name to the beginning
                            if fld._type == TYPE_ENUM:
                                ename = fld.get_refchain()[0]._typeref.called[-1]
                                val = ename + "_" + name_to_golang(val,  True)
                            valStruct += "{0}:{1},".format(fldName,  val)
                            #print("Field name {0} = {1}, {2}".format(fld._name,  refname,  defStruct))
                        if instName is not None:
                            valStruct = "{0}{{{1}}}".format(name_to_golang(fldType,  True),  valStruct[:-1])
                            fd.write("AddTableRef(\"{0}.{1}\", {2}, {3})\n".format(obj_name,  Obj._mod,  id, valStruct))
                            o = GoTable()
                            o.table = obj_name + "." + Obj._mod
                            o.itable = True
                            o.indexFieldName = idFieldName
                            self.tables[o.table] = o
        fd.write('}\n')        
        fd.close()
                
        
        # Structs
        fd = open(self.dest + "/structs.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write('import (')
        fd.write('\t. "asn2gort"')
        fd.write(')\n\n')
        fd.write("// PyCrate GoGenerator revision {0}\n".format(self.revision))
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            fd.write("\n/*******************************\n")
            fd.write("**** Module {0}\n".format(mod_name))
            fd.write("********************************/\n")
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                goName = name_to_golang(obj_name,  True)
                # If this is already defined as a simple type, skip
                if goName in self.simpleTypes:
                    continue
                if goName in const:
                    continue
                if Obj._mode == MODE_SET or Obj._mode == MODE_VALUE or Obj.TYPE == "CLASS":
                    continue
                param = ""
                if Obj.get_param() is not None:
                    if hasattr(Obj._cont,  "_typeref"):
                        param = Obj._cont._typeref.called[-1]
                    elif Obj._typeref is not None:
                        param = Obj._typeref.called[-1]
                    #else:
                    #    continue
                fd.write('\n/* {0}, Mode {1}, TYPE {2}, Param {3}  */\n'.format(obj_name,  Obj._mode,  Obj.TYPE,  param))
                fd.write(self.commentCode(Obj))
                #if Obj.get_param() is not None:
                #    continue
                if Obj._mode == MODE_TYPE:
                    if Obj.TYPE == "CHOICE":
                        tableRef = self.writeChoice(fd,  Obj)
                    elif Obj.TYPE == "SEQUENCE":
                        tableRef = self.writeSequence(fd,  Obj)
                    elif Obj.TYPE == "SEQUENCE OF":
                        tableRef = self.writeSequenceOf(fd,  Obj)
                    else:
                        fd.write("type! {0} struct {{\n\tAsn\n".format(goName))
                        fd.write("\tValue  ")
                        tableRef = self.writeType(fd,  Obj)
                        fd.write("\n}\n")

        # Simple type with constraint are not simple type because they require tags
        for s in self.simpleTypes:
            stype = self.simpleTypes[s]
            if not stype.saveAsStruct:
                continue
            if s in const:
                del const[s]
            fd.write(self.commentCode(stype))
            fd.write("type {0} struct {{\n\tValue {1} {2}\n}}\n\n".format(s,  stype.type,  formatTags(stype.tags)))
        fd.close()

        fd = open(self.dest + "/types.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write("// PyCrate GoGenerator revision {0}\n".format(self.revision))
        # Common types
        fd.write("type OCTET_STRING struct {\n\tValue string `type:\"octetstring\"`\n}\n\n")
        for s in self.simpleTypes:
            stype = self.simpleTypes[s]
            if not stype.Used or stype.saveAsStruct:
                continue
            # If this has a constraint, it cannot be a simple type because it requires tags
            if len(stype.tags) > 0:
                continue
            fd.write(self.commentCode(stype))
            fd.write("type {0} {1}\n".format(s,  stype.type))
        fd.close()

        fd = open(self.dest + "/consts.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write("// PyCrate GoGenerator revision {0}\n".format(self.revision))
        for c in const:
            fd.write(const[c] + "\n")
        fd.close()
