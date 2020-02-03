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
        self.revision = svnversion().strip()
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
'''        
class GoSet():
    def __init__(self):
        self.name = ""
        self.typName = ""
        self.modName = ""
        self.structName = ""
        self.objNames = []
'''        
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
        return
        if Obj._ref is not None:
            o = GoSet()
            val = Obj.get_val()
            o.name = Obj._name
            o.typName = Obj.get_typeref()._name
            o.modName = Obj._mod
            # Find reference that is not the typeref
            for a in Obj._ref:
                if isinstance(a,  ASN1RefType):
                    if a.called[-1] != o.typName:
                        o.structName = a.called[1] + "." + a.called[0]
                        break
            if val["root"] is not None:
                o.objNames += val["root"]
            if val["ext"] is not None:
                o.objNames += val["ext"]
            #self.sets[Obj._mod + "." + Obj._name] = o
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

    # Simply returns a dict of "range" and/or "opt", "tableidx"
    def buildConstraint(self,  Obj):
        c = {}
        # Modifiers?
        if Obj.is_opt():
            c["mod"] = "optional"

        constraint = Obj.get_const()
        if len(constraint)== 0:
            return c
        ext = None
        # Any table reference? Maybe this is the lookup key?
        for a in constraint:
            ''' 
            If this has an extended constraint, we must flag it as having the extension declared outside of the field
              type ::= SEQUENCE {
                 a INTEGER (0..255,...)  // The bit to test whether the constraint extension is used is within the SEQUENCE bitstream
                 b extINT  // The bit to test whether the constraint extension is used is in this fields bitstream
              }
              extINT ::= INTEGER (1..10,...)   
            '''
            if "ext" in a:
                ext = a["ext"]
                if ext is not None:
                    c["extConstraint"] = 1
            if "root" in a:
                val = ""
                for b in a["root"]:
                    if isinstance(b, ASN1RangeInt):
                        if len(val) > 0:
                            val += ","
                        val += '{0}..{1}'.format( b.lb,  b.ub)
                    elif isinstance(b,  int):
                        if len(val) > 0:
                            val += ","
                        val += "{0}".format(b)
                    else:
                        val = range
                if ext is not None:
                    val += ",..."
                c["range"] = val
                
            if "at" in a:
                if a["at"] is None:
                    c["tableIdx"] = "true"
        return c
       
    def markTypeUsed(self,  name):
        # If name is in simpleTypes, set flag so it is saved as a struct, not a simple type
        if name in self.simpleTypes:
            self.simpleTypes[name].Used = True
        
    def markGenStruct(self,  name):
        # If name is in simpleTypes, set flag so it is saved as a struct, not a simple type
        if name in self.simpleTypes:
            self.simpleTypes[name].saveAsStruct = True
        
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
        tblName = None
        if Obj._parent is not None:
            tblName =  Obj._parent._name + "/" 
        # Let's find a ASN1RefSet
        refName = None
        for a in Obj._ref:
            if isinstance(a,  ASN1RefSet):
                refName =  a.called[1] + "." + a.called[0]
                if tblName is None:
                    tblName = Obj._name + "/" + refName
                else:
                    tblName += refName
                break
        if refName is not None:
            if tblName in self.tables:
                tags["table"] = tblName
            else:
                print("Cannot locate table ",  tblName)
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
                tags = stype.tags.copy()
                tags.update(self.getTags(Obj))
                # Prefer length over range
                if "range" in tags and "length" in tags:
                    del tags["range"]
                type = stype.type
                # If this type has been defined already, use the actual type
                if objName in self.defined:
                    type = objName
                self.markTypeUsed(type)
                fd.write(" {0} {1}".format(type,  formatTags(tags)))
                return 
        if Obj._type==TYPE_SEQ  or Obj._type == TYPE_CHOICE:
            if Obj.get_refchain is not None:
                n = name_to_golang(Obj.get_refchain()[-1]._name,  True)
                self.markTypeUsed(n)
                tags = self.getTags(Obj)
                fd.write("*{0} {1}".format(n,  formatTags(tags)))
            else: 
                self.markTypeUsed(objType)
                tags = self.getTags(Obj)
                fd.write("*{0} {1}".format(objType,  formatTags(tags)))
        elif Obj._type == TYPE_SEQ_OF:
            if Obj.get_cont() is not None:
                ref = Obj.get_cont()._typeref.called[-1]
                gref = name_to_golang(ref,  True)
                if gref in self.simpleTypes:
                    self.simpleTypes[gref].Used = True
                n = name_to_golang(ref,  True)
                tags = self.getTags(Obj)
                if "range" in tags:
                    tags["length"] = tags["range"]
                    del tags["range"]
                self.markTypeUsed(n)
                self.markGenStruct(n)
                fd.write("[]*{0} {1}".format(n,  formatTags(tags)))
            else:
                n = name_to_golang(Obj.get_refchain()[0]._name,  True)
                self.markTypeUsed(n)
                fd.write("[]*{0}".format(n))
                self.markGenStruct(n)
        elif Obj._type == TYPE_INT:
            if objType not in self.defined:
                objType = "int"
            tags =self.getTags(Obj)
            tag = formatTags(tags)
            fd.write("{0} {1}".format(objType,  tag.strip()))
        elif Obj._type == TYPE_OID:
            tags =self.getTags(Obj)
            if "range" in tags:
                tags["length"] = tags["range"]
                del tags["range"]
            fd.write("[]byte {0}".format(formatTags(tags)))
        elif Obj._type == TYPE_OPEN:
            tags =self.getTags(Obj)
            tag = formatTags(tags)
            fd.write("interface{{}} {0}".format(tag))
        elif Obj._type == TYPE_BIT_STR:
            tags = self.getTags(Obj)
            if "range" in tags:
                tags["length"] = tags["range"]
                del tags["range"]
            fd.write("*AsnBITSTRING {0}".format(formatTags(tags)))
        elif Obj._type == TYPE_SEQ_OF:
            tags = self.getTags(Obj)
            if "range" in tags:
                tags["length"] = tags["range"]
                del tags["range"]
            n = name_to_golang(Obj.get_typeref()._name, True)
            self.markTypeUsed(n)
            fd.write("[]*{0} {1}".format(n,  formatTags(tags)))
            self.markGenStruct(n)
        elif Obj._type == TYPE_OCT_STR:
            tags = self.getTags(Obj)
            if "range" in tags:
                tags["length"] = tags["range"]
                del tags["range"]
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
        self.registerStruct(name_to_golang(Obj._name,  True))
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
        self.registerStruct(name_to_golang(Obj._name,  True))
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
        
    def getLowestNonClassType(self,  Obj):
        type = None
        if Obj._typeref is not None:
            type = name_to_golang(Obj._typeref.called[-1],  True)
        return type

    def writeSequenceOf(self,  fd,  Obj):
        self.registerStruct(name_to_golang(Obj._name,  True))
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
                self.markTypeUsed(childType)
            else:
                self.markTypeUsed(childType)
                childType = "*" + childType
            fd.write("\tItem  []{0}".format(childType))
            tags = self.getTags(Obj)
            if "range" in tags:
                tags["length"] = tags["range"]
                del tags["range"]
            # No constraints on octet string still requires array definition
            if "length" not in tags:  
                tags["length"] = "x"
            fd.write(" {0}".format(formatTags(tags)))
            fd.write("\n")
            self.gen_const_table(child)
        if ext != "":
            fd.write("\tAsnEXTENSION\n")
        fd.write("}\n")
        
    def setSimpleType(self,  st):
        if st.name == "E_RAB_ID":
            pass
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
    
    def writeCSV(self, fd, prefix,  Obj):
        r = Obj._ref
        if r is not None:
            s = ""
            for a in r:
                s += a.called[-1] + ", "
            r = s
        fd.write("\"{0}{1}\"\t\"{2}\"\t\"{3}\"\t\"{4}\"\t\"{5}\"\t\"{6}\"\t\"{7}\"\t\"{8}\"\n".format(prefix, 
            Obj._name,  
            Obj.TYPE, 
            Obj._mode,   
            Obj._typeref, 
            clean(Obj.get_classref()), 
            clean(Obj.get_param() is not None), 
            clean(Obj.get_refchain()), 
            clean(r)
        ))
        
    def registerStruct(self,  structName):
        self.structs[structName] = True

    # Does the Obj have a field that references the clsName?
    def findBaseClassObject(self,  Obj,  clsName):
        cont = getCList(Obj)
        for a in cont:
            b = cont[a]
            if hasattr(b,  "get_classref"):
                if b.get_classref() is not None:
                    if b.get_classref()._name == clsName:
                        # Child contains class, return parent
                        return Obj
            x = self.findBaseClassObject(b,  clsName)
            if x != None:
                return x
        return None
            

    def gen(self):
        self.tables = {}
        self.defined = {}  # Types already defined
        self.structs = {}  # For type registration
        self.simpleTypes = {}
        self.sets = {} # List of sets for the given class
        self.setToStruct = {} # For the set name, which structs are using it

        fd = open(self.dest + "/obj.csv", 'w')
        fd.write("_name\tType\tMode\t_typeref\tget_classref()\t_getparam()\tget_refchain()\t_ref\n")
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.currentModule = mod_name
            self._mod_name = mod_name
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                if Obj._param is not None and Obj._mode == MODE_TYPE:
                    name = "###" + Obj._name
                    if name in self.sets:
                        panic
                    self.sets[name] = Obj
                str = self.gen_const_table(Obj)

                if Obj._type == TYPE_INT or Obj._type == TYPE_CLASS:
                    continue
                self.writeCSV(fd, "",  Obj)
                const = getCList(Obj)
                for a in const:
                    c = const[a]
                    if not hasattr(c, "_name"):
                        continue
                    self.writeCSV(fd, "--->",  c)
                
        fd.close()

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
                            if "range" in tags:
                                tags["length"] = tags["range"]
                                del tags["range"]
                            if "length" not in tags:
                                tags["length"] = "x"
                            str += "type {0} struct {{\n\tValue []byte {1}\n}}\n\n".format(goName,  formatTags(tags))
                        elif Obj._type == TYPE_BIT_STR:
                            stype = GoField(Obj._text_def)
                            stype.name = goName
                            stype.tags.update(constraint)
                            if "range" in stype.tags:
                                stype.tags["length"] = stype.tags["range"]
                                del stype.tags["range"]
                            stype.type = "*AsnBITSTRING"
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
        
        '''
        Build lookup tables
        Lookup tables are built for objects that have a refernece to an ASN1RefSet type
        Each table entry has:
            TableName   One or more entries to group the IDs.  This is a combination of the module and struct referencing the set
            IndexID         Combined with TableName for the unique lookup, these are in the SET 
            Value             Instance of value with default values, if any.
            
            For each set, a group of default values are specified.  Some of these may not map to the current reference object.
        '''
        fd = open(self.dest + "/tables.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write('import (')
        fd.write('\t. "asn2gort"')
        fd.write(')\n\n')
        fd.write("// const ASNGORVER string = \"{0}\"\n".format(self.revision))
        fd.write('// Table lookups\n')
        fd.write('func init() {\n')        
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            Mod = GLOBAL.MOD[mod_name]
            obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
            for obj_name in obj_names:
                Obj = Mod[obj_name]
                if Obj._type == TYPE_ENUM or Obj._type == TYPE_CLASS:
                    continue
                # Now we get the required fields
                validFields = {}
                openTypeFieldName = None
                openTypeTypeName = None
                # Look for reference to ASN1RefSet. Set hasSet to the set name.
                hasSet = None
                # Is this a class reference?
                isClassRef = False
                for r in Obj._ref:
                    if isinstance(r,  ASN1RefClassField):
                        isClassRef = True
                        break
                
                newObj = None
                if not isClassRef:
                    cont = getCList(Obj)
                    for a in cont:
                        c = cont[a]
                        if not hasattr(c,  "_ref"):
                            continue
                        for r in c._ref:
                            if isinstance(r,  ASN1RefSet):
                                hasSet = r.called
                                break
                        if hasSet is not None:
                            n = None
                            # New obj to parse is the reftype
                            if isinstance(c.get_cont(),  ASN1Dict):
                                for b in c._ref:
                                    if isinstance(b,  ASN1RefType):
                                        n = b.called
                                        break
                            else:
                                n = c.get_cont()._typeref.called
                            newObj = GLOBAL.MOD[n[0]][n[1]]
                            break
                    
                if newObj is None:       
                    cont = getCList(Obj)
                else:
                    cont = getCList(newObj)                    
                for a in cont:
                    c = cont[a]
                    # c must be the base class of fields
                    if not hasattr(c,  "_ref"):
                        continue
                    for b in c._ref:
                        if isinstance(b,  ASN1RefSet):
                            hasSet = b.called
                    # If the field has an "at" is using another field for indexing into the table
                    constraint = c.get_const()
                    if len(constraint) > 0:
                        at = findInList(constraint,  "at")
                        if at == None:
                            validFields[c._name] = True
                        else:
                            validFields[c._name] = False
                    else:
                        validFields[c._name] = False
                    if c._type == TYPE_OPEN:
                        openTypeFieldName = c._name
                        # If the child does not have anythin in refchain, then we cannot use this Obj
                        if len(c.get_refchain()) == 0:
                            hasSet = None
                            break
                        openTypeTypeName = c.get_refchain()[0]._name
                        
                if hasSet is None:
                    continue
                setName = hasSet[1]  + "." + hasSet[0]
                # Get the reference object
                setO = GLOBAL.MOD[hasSet[0]][hasSet[1]]
                if setO._type != TYPE_SET and setO._type != TYPE_CLASS:
                    continue
                setObj = setO.get_val()
                # If nothing in set, save something so no reference errors occur
                if len(setObj["root"]) == 0:
                    tableName = obj_name + "/" + setName
                    o = GoTable()
                    o.table = tableName
                    o.itable = not isClassRef
                    o.indexFieldName = None
                    self.tables[o.table] = o
                    fd.write("AddTableRef(\"{0}\", -1, nil)\n".format(tableName))
                    #print("Empty table Obj:{0}, openField:{1}, openType:{2}, fields:{3}".format(tableName, openTypeFieldName,  openTypeTypeName,  validFields))
                    
                # Run through each entry in the set
                for a in setObj["root"]:
                    instName = ""
                    openTypeSet  = False
                    idFieldName = None
                    struct = ""
                    for b in a:
                        bb = a[b]
                        if b == openTypeTypeName:
                            # Extract the type
                            if bb._typeref is not None:
                                instName = name_to_golang(bb._typeref.called[-1],  True)
                            else:
                                instName = name_to_golang(bb._type,  True)
                            openTypeSet = True
                        if b not in validFields:
                            continue
                        if validFields[b]:
                            tblID = bb
                            idFieldName = b
                        if len(struct) > 0:
                            struct += " ,"
                        if newObj is not None:
                             if newObj._cont[b]._type == TYPE_ENUM:
                                bb = "{0}_{1}".format(name_to_golang(b,  True),  name_to_golang(bb,  True))
                        elif Obj._cont[b]._type == TYPE_ENUM:
                            bb = "{0}_{1}".format(name_to_golang(b,  True),  name_to_golang(bb,  True))
                        struct += "{0}:{1}".format(name_to_golang(b, True),  bb)
                    if not openTypeSet:
                        continue
                    if isClassRef:
                        struct = "{0}{{{1}, {2}:{3}{{}}}}".format(openTypeTypeName,  struct, name_to_golang(openTypeFieldName,  True), instName)
                        tableName = openTypeTypeName + "." + mod_name
                        self.markGenStruct(name_to_golang(openTypeFieldName,  True))
                        # Since we are popluating a class field with the lookup by type, we will include the type in the table name
                        tableName = openTypeTypeName + "/" + setName
                    else:
                        struct = "{0}{{{1}, {2}:{3}{{}}}}".format(name_to_golang(newObj._name,  True),  struct,  name_to_golang(openTypeFieldName,  True),  name_to_golang(instName,  True))
                        tableName = obj_name + "/" + setName
                        self.markGenStruct(instName)
                    #print("{0} {1},{2} has set {3}".format(tableName, openTypeFieldName,  openTypeTypeName,  struct))
                    if Obj._name == "UplinkNASTransport":
                        pass
                    fd.write("AddTableRef(\"{0}\", {1}, {2})\n".format(tableName,  tblID,  struct))
                    o = GoTable()
                    o.table = tableName
                    o.itable = not isClassRef
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
        fd.write("// const ASNGORVER string = \"{0}\"\n".format(self.revision))
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
                        fd.write("\n}\n")

        # Simple type with constraint are not simple type because they require tags
        for s in self.simpleTypes:
            stype = self.simpleTypes[s]
            if not stype.saveAsStruct:
                continue
            if s in const:
                #print("Deleting const {0}".format(s))
                del const[s]
            fd.write(self.commentCode(stype))
            self.registerStruct(s)
            fd.write("type {0} struct {{\n\tValue {1} {2}\n}}\n\n".format(s,  stype.type,  formatTags(stype.tags)))
        fd.close()

        fd = open(self.dest + "/types.go", 'w')
        fd.write("package {0}\n\n".format(self.pkg))
        fd.write("import (\n\t\"asn2gort\"\n\t\"reflect\"\n)\n\n")
        fd.write("// const ASNGORVER string = \"{0}\"\n".format(self.revision))
        # For preloading
        fd.write("\nfunc init() {\n")
        for s in self.structs:
            fd.write("\tasn2gort.LoadAsnStructures(reflect.TypeOf({0}{{}}))\n".format(s))
        fd.write("}\n\n")
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
        fd.write("import (\n\t\"asn2gort\"\n\t\"reflect\"\n)\n\n")
        fd.write("const ASNGORVER string = \"{0}\"\n".format(self.revision))
        # For preloading
        fd.write("\nfunc init() {\n")
        for c in const:
            s = const[c]
            p = s.find(" struct")
            if p != -1:
                sName = s[5:p]
                fd.write("\tasn2gort.LoadAsnStructures(reflect.TypeOf({0}{{}}))\n".format(sName))
        fd.write("}\n\n")
        for c in const:
            fd.write(const[c] + "\n")
        fd.close()

def clean(s):
    if s is None:
        return s
    s = "{0}".format(s)
    return s.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
