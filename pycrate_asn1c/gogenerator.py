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

from .utils  import *
from .glob   import *
from .setobj import *
from .refobj import *
from .asnobj import get_asnobj, ASN1Obj, INT, OID
from .stringlist import *
import os

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
        if not os.path.isdir(self.dir + "/" + pmod):
          os.mkdir(self.dir + "/" + pmod)
        self.files = []
        self.gen()

    def openFile(self, fn):
        self.files[fn] = StringList(fn + "_def")
        self.files[fn] = StringList(fn + "_set")

    def wdl(self, s):
        self.definition.write(s)
    
    def wil(self, s):
        pass
        #self.init.write(s)

    def save(self, mod):
        print('Saving ' + self.dir + "/" + self.pkg + "/" + mod + ".go")
        if not os.path.isdir(self.dir + "/" + self.pkg + "/" + mod):
            os,mkdir(self.dir + "/" + self.pkg + "/" + mod)
        self.fd = open(self.dir + "/" + self.pkg + "/" + mod + ".go", 'w')
        for a in self.definition.items():
          self.fd.write('{0}\n'.format(a))
        self.fd.write("\n\n// Initialization section\n")
        for a in self.init.items():
          self.fd.write('{0}\n'.format(a))
        self.fd.close()

    def gen(self):
        pass

#------------------------------------------------------------------------------#
# Python source code generator
#------------------------------------------------------------------------------#
# generate Python source code for the ASN1 runtime of pycrate
# (located in pycrate_asn1rt/ directory)

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

def value_to_defin(v, Obj=None, Gen=None, ind=None):
    if Obj.TYPE == TYPE_NULL:
        # '0'
        return '0'
    elif Obj.TYPE == TYPE_BOOL:
        # bool
        return qrepr(v)
    elif Obj.TYPE == TYPE_INT:
        # int (/long)
        rv = repr(v)
        if rv[-1] == 'L':
            # python2 useless long notation
            return rv[:-1]
        else:
            return rv
    elif Obj.TYPE == TYPE_REAL:
        # list of 3 int -> convert to 3-tuple
        mant, ex = qrepr(v[0]), qrepr(v[2])
        if mant[-1] == 'L':
            # again, python2 useless long notation
            mant = mant[:-1]
        if ex[-1] == 'L':
            ex = ex[:-1]
        return '{%s, %r, %s}' % (mant, v[1], ex)
    elif Obj.TYPE == TYPE_ENUM:
        # string
        return qrepr(v)
    elif Obj.TYPE == TYPE_BIT_STR:
        # list of 2 int -> convert to tuple
        vv, vl = qrepr(v[0]), qrepr(v[1])
        if vv[-1] == 'L':
            vv = vv[:-1]
        if vl[-1] == 'L':
            vl = vl[:-1]
        return '{%s, %s}' % (vv, vl)
    elif Obj.TYPE == TYPE_OCT_STR:
        # byte-string
        if python_version > 2:
            return qrepr(v)
        else:
            return 'b%s' % qrepr(v)
    elif Obj.TYPE == TYPE_OID:
        # list of int -> convert to tuple
        return qrepr(tuple(v))
    elif Obj.TYPE == TYPE_REL_OID:
        # list of int -> convert to tuple
        return qrepr(tuple(v))
    elif Obj.TYPE in TYPE_STRINGS:
        # char string
        return qrepr(v)
    elif Obj.TYPE in (TYPE_TIME_UTC, TYPE_TIME_GEN):
        # tuple of {int, None}
        return qrepr(v)
    elif Obj.TYPE == TYPE_CHOICE:
        # list of name and single value -> convert to tuple
        return '{' + qrepr(v[0]) + ', ' + value_to_defin(v[1], Obj.get_cont()[v[0]], Gen) + '}'
    elif Obj.TYPE in (TYPE_SEQ_OF, TYPE_SET_OF):
        # list of single value
        return '[' + ', '.join([value_to_defin(i, Obj.get_cont(), Gen) for i in v]) + ']'
    elif Obj.TYPE in (TYPE_SEQ, TYPE_SET):
        # Python dict of {name: single value}
        #return 'ASN1Dict([' + \
        return '' + \
               ', '.join(['{{{0}, {1}}}'.format(qrepr(name), value_to_defin(val, Obj.get_cont()[name], Gen)) \
                          for (name, val) in v.items()]) + \
               ''
    elif Obj.TYPE == TYPE_CLASS:
        # Python dict of {name: single value or set of values or type object}
        r = []
        for (name, value) in v.items():
            ObjVal = Obj.get_cont()[name]
            if not hasattr(ObjVal, '_pyname'):
                ObjVal._pyname = '_{0}_{1}'.format(Obj._pyname, name_to_defin(ObjVal._name))
            if ObjVal._mode == MODE_VALUE:
                if ObjVal.TYPE == TYPE_OPEN and isinstance(ObjVal._typeref, ASN1RefClassIntern):
                    # get the typeref object defined in v, and use it to define the ObjVal value
                    ObjValTr = v[ObjVal._typeref.ced_path[0]]
                    for p in ObjVal._typeref.ced_path[1:]:
                        ObjValTr = ObjValTr.get_cont()[p]
                    r.append((qrepr(name), value_to_defin(value, ObjValTr, Gen)))
                else:
                    r.append((qrepr(name), value_to_defin(value, ObjVal, Gen)))
            elif ObjVal._mode == MODE_SET:
                if ObjVal.TYPE == TYPE_OPEN and isinstance(ObjVal._typeref, ASN1RefClassIntern):
                    # get the typeref object defined in v, and use it to define the ObjVal value
                    ObjValTr = v[ObjVal._typeref.ced_path[0]]
                    for p in ObjVal._typeref.ced_path[1:]:
                        ObjValTr = ObjValTr.get_cont()[p]
                    r.append((qrepr(name), set_to_defin(value, ObjValTr, Gen)))
                else:
                    r.append((qrepr(name), set_to_defin(ASN1Set(value), ObjVal, Gen)))
            else:
                #ObjVal._mode == MODE_TYPE
                # value is an ASN1 object, create it first
                # WNG: no name unicity for value, use ind for this purpose
                if ind is not None:
                    value._pyname = '_{0}_val_{1}_{2!r}'.format(Obj._pyname, name_to_defin(value._name), ind)
                else:
                    value._pyname = '_{0}_val_{1}'.format(Obj._pyname, name_to_defin(value._name))
                Gen.gen_type(value, compts=False)
                # object to be linked in the ASN1Dict value 
                r.append((qrepr(name), "p."+value._pyname))
        #return 'ASN1Dict([' + ', '.join(r) + '])'
        #return '' + ', '.join(r) + ''
        return r
    elif Obj.TYPE in (TYPE_OPEN, TYPE_ANY):
        # list with [object definition, single value]
        # changing it to a 2-tuple
        v[0]._pyname = '_{0}_val'.format(name_to_defin(v[0]._name))
        Gen.gen_type(v[0], compts=False)
        return '({0}, {1})'.format(v[0]._pyname, value_to_defin(v[1], v[0], Gen))
    elif Obj.TYPE == TYPE_EXT:
        # TODO
        assert()
    elif Obj.TYPE == TYPE_EMB_PDV:
        # TODO
        assert()
    elif Obj.TYPE == TYPE_CHAR_STR:
        # TODO
        assert()
    else:
        assert()

def range_to_defin(r, Obj=None):
    # ASN1Range only applied to TYPE_INT, TYPE_REAL and TYPE_STR_*
    if Obj.TYPE == TYPE_INT:
        return 'asn2gort.NewASN1RangeInt({0}, {1})'\
               .format(value_to_defin(r.lb, Obj), value_to_defin(r.ub, Obj))
    elif Obj.TYPE == TYPE_REAL:
        return 'asn2gort.ASN1RangeReal{{Lb:{0}, Ub:{1}, Lb_incl:{2!r}, Ub_incl:{3!r}}}'\
                .format(value_to_defin(r.lb, Obj), value_to_defin(r.ub, Obj), r.lb_incl, r.ub_incl)
    elif Obj.TYPE in ASN1Range._TYPE_STR:
        return 'asn2gort.ASN1RangeStr{{Lb:{0!r}, Ub:{1!r}}}'.format(r.lb, r.ub)
    else:
        assert()

def set_to_defin(S, Obj=None, Gen=None):
    # ASN1Set(rv, rr, ev, er)
    # ind: value index, required especially for distinguishing sets of CLASS values
    s = 'asn2gort.ASN1Set{RV:[]*asn2gort.ASN1Ref{'
    ind = 0
    # root part
    for v in S._rv:
        #rv.append(value_to_defin(v, Obj, Gen, ind))
        for y in value_to_defin(v, Obj, Gen, ind):
          if len(y)==1:
            s += 'asn2gort.NewASN1Ref({0}),'.format(y)
          elif len(y)==2:
            s += 'asn2gort.NewASN1RefWithMod({0}, {1}),'.format(y[0],y[1])
          else:
            s += 'asn2gort.NewASN1Ref({0}),'.format(y[1:len(y)-1])
        ind += 1
    s +=  '}, RR:[]*asn2gort.ASN1Ref{'
    for vr in S._rr:
        #rr.append( range_to_defin(vr, Obj) )
        y = range_to_defin(vr, Obj)
        s += 'asn2gort.NewASN1Ref({0}),'.format(y)
    s +=  '}, '
    # extension part
    if S._ev is None:
        ev, er = '', ''
    else:
        s += 'EV:[]*asn2gort.ASN1Ref{'
        for v in S._ev:
            #ev.append( value_to_defin(v, Obj, Gen, ind) )
            for y in value_to_defin(v, Obj, Gen, ind):
              if len(y)==1:
                s += 'asn2gort.NewASN1Ref({0}),'.format(y)
              elif len(y)==2:
                s += 'asn2gort.NewASN1RefWithMod({0},{1}),'.format(y[0],y[1])
              else:
                s += 'asn2gort.NewASN1Ref({0}),'.format(y[1:len(y)-1])
            ind += 1
        s += '}, ER:[]*asn2gort.ASN1Ref{'
        for vr in S._er:
            #er.append( range_to_defin(vr, Obj) )
            for y in range_to_defin(vr, Obj):
              er += 'asn2gort.NewASN1Ref({0}),'.format(y[1:len(y)-1])
        s +='} '
    #
    return s + '}' 

def tag_to_defin(t):
    return '{{{0!r}, {1}, {2}}}'.format(t[0], _tag_lut[t[1]], _tag_lut[t[2]])

def typeref_to_defin(Obj):
    if isinstance(Obj._typeref, ASN1RefClassIntern):
        return 'asn2gort.ASN1RefClassIntern(None, {0!r})'.format(Obj._typeref.ced_path)
    elif hasattr(Obj._typeref, 'called') and \
    Obj._typeref.called[1] in ('TYPE-IDENTIFIER', 'ABSTRACT-SYNTAX'):
        # special process for those types which are injected in all modules by proc.py
        return '{0}({1!r}, {2!r})'.format(Obj._typeref.__class__.__name__,
                                          Obj._typeref.called,
                                          Obj._typeref.ced_path)
    # otherwise, we ensure to provide the correct module name (and not the imported one,
    # which be misleading due to IMPORTS chain)
    else:
        (modname, objname) = Obj._typeref.called
        while objname in GLOBAL.MOD[modname]['_imp_']:
            modname = GLOBAL.MOD[modname]['_imp_'][objname]
        if isinstance(Obj._typeref, ASN1RefType):
            return 'asn2gort.NewASN1RefType(\"{0}\", \"{1}\")'.format(modname, objname)
        elif isinstance(Obj._typeref, ASN1RefClassField):
            return 'asn2gort.NewASN1RefClassField(asn2gort.NewASN1RefType(\"{0}\", \"{1}\"), {2})'.format(modname, objname, goarr(Obj._typeref.ced_path))
        elif isinstance(Obj._typeref, ASN1RefClassValField):
            return 'asn2gort.ASN1RefClassValField{Ref:asn2gort.NewAsnRefWithMod(\"{0}\", \"{1}\"), Obj:{2}}'.format(modname, objname, goArr(Obj._typeref.ced_path))
        elif isinstance(Obj._typeref, ASN1RefChoiceComp):
            return 'asn2gort.ASN1RefChoiceComp{asn2gort.NewAsnRefWithMod(\"{0}\", \"{1}\"), {2}}'.format(modname, objname, Obj._typeref.ced_path)
        elif isinstance(Obj._typeref, ASN1RefInstOf):
            return 'asn2gort.ASN1RefInstOf(\"{0}\", \"{1}\")'.format(modname, objname)
        else:
            assert()


class GoGenerator(_Generator):
    """
    PycrateGenerator generates GO source code to be loaded into the pycrate
    ASN.1 runtime, located in pycrate_asn1rt
    """
    _impl = 0
    dparms = ["_mod", "_name", "TYPE", "_ext", "_flag"]

    enums = dict()
    def saveEnum(self, pkg, name, val):
        if pkg not in self.enums:
            self.enums[pkg] = dict()
        self.enums[pkg][name] = val

    def dumpConstraint(self, i):
        self.dumpfd.write("Constraint type: {0}\n".format(i["type"]))
        pass

    def dumpObj(self, indent, i):
        if hasattr(i, "_name"):
            if i._name == "ProcedureCode":
                print("Here")
        self.dumpfd.write(indent + "Object ")
        for a in self.dparms:
            if hasattr(i, a):
                self.dumpfd.write("{0}:{1}, ".format(a, getattr(i, a)))
        self.dumpfd.write("\n")

        if hasattr(i, "_text_def"):
            if i._text_def != "":
                self.dumpfd.write(indent + "TEXT:" + i._text_def + "\n")

        indent += "\t"
        if hasattr(i, "_ref"):
            if isinstance(i._ref, set):
                for a in i._ref:
                    self.dumpfd.write(indent + "Reference: {0}\n".format(a))

        if hasattr(i, "_root") and i.TYPE != "ENUMERATED":
            if isinstance(i._root, list):
                for a in i._root:
                    self.dumpfd.write(indent + "Root: {0}\n".format(a))

        if hasattr(i, "_cont"):
            if isinstance(i._cont, ASN1Dict):
                for a in i._cont:
                    val = i._cont[a]
                    if isinstance(val, int):
                        self.dumpfd.write(indent + "Cont: {0} = {1}\n".format(a, val))
                    else:
                        self.dumpObj(indent+"\t", val)

        if hasattr(i, "_const"):
            for a in i._const:
                self.dumpfd.write(indent)
                self.dumpConstraint(a)
        pass

    def checkBasicType(self, part, structName):
        if part.TYPE == 'OCTET STRING':
            ename = name_to_golang(structName, True)
            self.basicTypes[ename] = "string"
            return True
        elif part.TYPE == 'INTEGER':
            ename = name_to_golang(structName, True)
            self.basicTypes[ename] = "int64"
            return True
        return False

    def gen(self):
        #
        #pkg = self.dest
        #
        modlist = []
        #
        self.basicTypes = dict()
        self.dumpfd = None
        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            modName = name_to_defin(mod_name).lower()
            if self.dumpfd != None:
                self.dumpfd.close()
            self.dumpfd = open(modName + "_dump.txt","w")
            #if not os.path.isdir(self.dest + "/" + modName):
            #    os.mkdir(self.dest + "/" + modName)

            self.dumpfd.write("\n\n***********************************************\nModule {0}\n***********************************************".format(modName))
            constEnums = None

            # Create structs for all containers: CHOICE, SEQ, SET, CLASS
            asnStructs = GLOBAL.MOD[mod_name]
            for structName in asnStructs:
                if structName[:1] == '_':
                    continue
                part = asnStructs[structName]
                self.dumpObj("", part)

                if self.checkBasicType(part, structName):
                    continue

                if part.TYPE == 'ENUMERATED':
                  ename = name_to_golang(structName, True)
                  for c in part._cont:
                    val = str(part._cont[c])
                    self.saveEnum(ename, name_to_golang(c, True), val)
                elif part.TYPE == 'SEQUENCE':
                    structName = name_to_golang(structName, True)
                    self.fd = open(self.dest + "/" + structName + ".go", 'w')
                    self.fd.write("package " + self.pkg + "\n\n")
                    self.genSequence(structName, part)
                    self.fd.close()
                elif part.TYPE == 'CHOICE':
                    structName = name_to_golang(structName,True)
                    self.fd = open(self.dest + "/" + structName + ".go", 'w')
                    self.fd.write("package " + self.pkg + "\n\n")
                    self.fd.write("type " + structName + " struct {\n")
                    self.fd.write("\tChoice\tinterface{}\n")
                    self.fd.write("}\n")
                    self.fd.close()
                elif part.TYPE == 'CLASS' and isinstance(part._val, dict):
                    structName = name_to_golang(structName,True)
                    self.fd = open(self.dest + "/"  + structName + ".go", 'w')
                    self.fd.write("package " + self.pkg + "\n\n")
                    '''
                    for c in part._val["root"]:
                        item = part._val["root"][c]
                        itemName = name_to_golang(c)
                        self.fd.write("type " + itemName + " struct {\n")
                        self.fd.write("\t" + itemName + "\t*" + itemName + "\n")
                        self.fd.write("}\n")
                    '''
                    self.fd.close()


        self.fd = open(self.dest + "/enums.go", 'w')
        self.fd.write("package " + self.pkg + '''

import (
    "fmt"
    "strconv"
)

var enums = map[string]map[string]string{
''')
        for a in self.enums:
            enums = self.enums[a]
            self.fd.write("\t\"{0}\":{{\n".format(a))
            for b in enums:
                val = self.enums[a][b]
                self.fd.write("\t\t\"{0}\":\"{1}\",\n".format(b, val))
            self.fd.write("\t},\n")

        self.fd.write('''}

        // GetStrEnum returns string enum value for given type and name or "" when not found
        func GetStrEnum(typ, name string) string {
          if elst, ok := enums[typ]; ok {
            if val, ok := elst[name]; ok {
              return val
            }
            return ""
          }
          return ""
        }

        // GetIntEnum returns int64 enum value for given type and name or error when not found
        func GetIntEnum(typ, name string) (int64, error) {
          val := GetStrEnum(typ, name)
          if val == "" {
             return 0, fmt.Errorf("Enum not found")
          }
          i, err := strconv.ParseInt(val, 10, 64)
          if err {
            return 0, err
          }
          return i, nil
        }
        ''')
        self.fd.close()

        self.fd = open(self.dest + "/basicTypes.go", 'w')
        self.fd.write("package " + self.pkg + "\n\n")
        for a in self.basicTypes:
            self.fd.write("type {0} {1}\n".format(a, self.basicTypes[a]))
        self.fd.close()


        for mod_name in [mn for mn in GLOBAL.MOD if mn[:1] != '_']:
            self.open()
            self.wdl('package ' + self.pkg)
            self.wdl('// -*- coding: UTF-8 -*-')
            self.wdl('// Code automatically generated by pycrate_asn1c')
            self.wdl('')
            self.wdl('import (')
            self.wdl('//\t"fmt"')
            self.wdl('\t"../asn2gort"')
            self.wdl('//\t"reflect"')   
            self.wdl(')')
            self.wdl('')
            self._mod_name = mod_name
            Mod = GLOBAL.MOD[mod_name]
            pymodname = name_to_defin(mod_name)
            #
            self.wil('func (p *{0})Init() {{'.format(pymodname))
            self.wdl('type {0} struct {{'.format(pymodname))
            self.wdl('\tasn2gort.Asn\n')
            #
            self.wil('p.Name = {0}'.format(qrepr(Mod['_name_'])))
            strr = 'p.Oid = []int{'
            for x in Mod['_oid_']:
                strr += '{0}, '.format(x)
            strr += '}'
            self.wil(strr)
            self.wil('p.Tag = "{0}"'.format(_tag_lut[Mod['_tag_']]))
            for attr in ('_obj_', '_type_', '_set_', '_val_', '_class_', '_param_'):
                #self.wdl('{0} []string'.format(attr))
                name = attr[1:]
                name = name[0].upper() + name[1:]
                self.wil('p.{0} = []string{{'.format(name))
                for name in Mod[attr]:
                    self.wil('"{0}",'.format(name))
                self.wil('}//388')
            self.wil('')
            #
            self._all_ = []
            self._allobj_ = {}
            self.gen_mod(GLOBAL.MOD[mod_name])
            strr = 'p.All = []interface{}{'
            for pyobjname in self._all_:
                obj = self._allobj_.get(pyobjname)
                if obj.TYPE != "ENUMERATED":
                    str += 'p.{0},'.format(pyobjname)
            str += '}'
            self.wil(str)
            modlist.append(pymodname)
            #
            self.wdl('}\n')
            self.wil('}\n\n')
            self.save(pymodname)

        #
        # create the _IMPL_ class if required
        if self._impl:
            self.wrl('type _IMPL_ struct {{\n')
            self.indent = 2
            #
            #self.wrl('_name_ = \"_IMPL_\""')
            #self.wrl('_oid_  = []')
            #self.wrl('_obj_  = {0!r}'.format(GLOBAL.MOD['_IMPL_']['_obj_']))
            #self.wrl('')
            #
            self._all_ = []
            self._allobj_ = {}
            self.gen_mod(GLOBAL.MOD['_IMPL_'])
            #self.wrl('_all_ = [')
            #for pyobjname in self._all_:
            #    self.wrl('    {0},'.format(pyobjname))
            #self.wrl(']')
            modlist.append('_IMPL_')
            #
            self.indent = 0
            self.wrl('}//424')
            self.wrl('')
        #
        # Instantiation
        self.open()
        self.wil('package ' + self.pkg)
        self.wil('import "../asn2gort"')
        self.wil('type _' + self.pkg + ' struct {')
        for x in modlist:
          self.wil('\t{0} *{0}'.format(x))        
        self.wil('}')

        emod = 'Base'+self.pkg
        self.wil('\nvar ' + emod + " _" + self.pkg)
    
        self.wil('\n\nfunc init() {')
        self.wil('\t' + emod + " = _" + self.pkg + "{}")
        for x in modlist:
          self.wil('\t{0}.{1} = &{1}{{}}'.format(emod,x))
          self.wil('\t{0}.{1}.Init()'.format(emod,x))
          self.wil('\tasn2gort.InitModule("{0}",{1}.{0})'.format(x,emod))        
        self.wil('}')
        self.save("Init")

    def genSequence(self, structName, part):
        self.fd.write("// " + part._text_def + "\n")
        self.fd.write("type " + structName + " struct {\n")
        for c in part._cont:
            item = part._cont[c]
            itemName = name_to_golang(c, True)
            if self.checkBasicType(item, structName):
                continue
            self.fd.write("\t" + itemName + "\t*" + itemName + "\n")
        self.fd.write("}\n")


    def gen_mod(self, Mod):
        obj_names = [obj_name for obj_name in Mod.keys() if obj_name[0:1] != '_']
        for obj_name in obj_names:
            Obj = Mod[obj_name]
            self.wdl('//-----< {0} >-----'.format(Obj._name))
            if Obj._mode == MODE_TYPE:
                self.gen_type(Obj)
            elif Obj._mode == MODE_SET:
                self.gen_set(Obj)
            elif Obj._mode == MODE_VALUE:
                self.gen_val(Obj)
            # delete potential table constraints caches
            if hasattr(self, '_const_tabs'):
                del self._const_tabs
            self.wdl('')
    
    def _handle_dup(self, Obj):
        if Obj._pyname in self._all_:
            # a similar object was already generated (this is mainly due to a 
            # certain usage of parameterization)
            ObjDef = self._allobj_[Obj._pyname]
            if Obj == ObjDef or \
            Obj._name == ObjDef._name and Obj._type == ObjDef._type and \
            Obj._mode == ObjDef._mode and Obj._typeref == ObjDef._typeref and \
            Obj._cont == ObjDef._cont and Obj._const == ObjDef._const and \
            Obj._tag == ObjDef._tag and Obj._flag == ObjDef._flag and \
            Obj._val == ObjDef._val:
                # new object seems broadly equal to the already defined one
                return True
            else:
                # change _pyname attribute, until an unused _pyname is found
                ext = 0
                Obj._pyname = Obj._pyname + '_{0!r}'.format(ext)
                while Obj._pyname in self._all_:
                    ObjDef = self._allobj_[Obj._pyname]
                    if Obj == ObjDef or \
                    Obj._name == ObjDef._name and Obj._type == ObjDef._type and \
                    Obj._mode == ObjDef._mode and Obj._typeref == ObjDef._typeref and \
                    Obj._cont == ObjDef._cont and Obj._const == ObjDef._const and \
                    Obj._tag == ObjDef._tag and Obj._flag == ObjDef._flag and \
                    Obj._val == ObjDef._val:
                        return True
                    else:
                        ext += 1
                        Obj._pyname = Obj._pyname[:-2] + '_{0!r}'.format(ext)
                return False
        else:
            return False
    
    def gen_type(self, Obj, compts=False):
        #
        # 1) create a python-compliant name if not already done
        if not hasattr(Obj, '_pyname'):
            Obj._pyname = name_to_defin(Obj._name)
        #
        # 2) check to not duplicate object
        if self._handle_dup(Obj):
            return
        #
        # 3) early process INSTANCE OF, as it translates to a special 
        # SEQUENCE object
        if Obj.TYPE == TYPE_INSTOF:
            InstSeq = Obj.get_typeref()
            if hasattr(Obj, '_pyname'):
                InstSeq._pyname = Obj._pyname
            self.gen_type(InstSeq)
            if Obj._const:
                # TODO
                assert()
            self.wrl('{0}.TAG = 8'.format(InstSeq._pyname))
            self._all_.append(InstSeq._pyname)
            self._allobj_[InstSeq._pyname] = InstSeq
            return
        #
        # 4) initialize the object Python instance
        # Skip Enums
        if Obj._pyname == "_S1AP_PROTOCOL_IES_criticality":
            print("HERE")
        if Obj.TYPE != "ENUMERATED":
            if Obj._mode == "VALUE" and Obj._val != None:
                self.wdl('\t{0} int'.format(Obj._pyname))
            else:
                self.wdl('{0}\t*asn2gort.Asn{1}'.format(Obj._pyname, Obj.__class__.__name__))
                self.wil('p.{0} = &asn2gort.Asn{1}{{{2}}}'.format(Obj._pyname,
                                                 Obj.__class__.__name__,
                                                 self._gen_type_init_attr(Obj, compts)))
        else:
            self.wdl('{0}\t*asn2gort.Asn{1}'.format(Obj._pyname, Obj.__class__.__name__))
        #
        # 5) check if the _IMPL_ module is required
        if Obj._typeref and isinstance(Obj._typeref.called, tuple) and \
        Obj._typeref.called[0] == '_IMPL_': 
            self._impl += 1
        #
        # 6) in case this is a parameterized object, no need to defined 
        # anything more
        if Obj._param:
            return
        #
        # 7) generate the content and specific constraints
        if Obj.TYPE == TYPE_NULL                        : pass
        elif Obj.TYPE == TYPE_BOOL                      : self.gen_type_bool(Obj)
        elif Obj.TYPE == TYPE_INT                       : self.gen_type_int(Obj)
        elif Obj.TYPE == TYPE_REAL                      : self.gen_type_real(Obj)
        elif Obj.TYPE == TYPE_ENUM                      : self.gen_type_enum(Obj)
        elif Obj.TYPE == TYPE_BIT_STR                   : self.gen_type_bitstr(Obj)
        elif Obj.TYPE == TYPE_OCT_STR                   : self.gen_type_octstr(Obj)
        elif Obj.TYPE in (TYPE_OID, TYPE_REL_OID)       : self.gen_type_oid(Obj)
        elif Obj.TYPE in TYPE_STRINGS                   : self.gen_type_str(Obj)
        elif Obj.TYPE in (TYPE_TIME_UTC, TYPE_TIME_GEN) : self.gen_type_time(Obj)
        elif Obj.TYPE == TYPE_CHOICE                    : self.gen_type_choice(Obj)
        elif Obj.TYPE in (TYPE_SEQ_OF, TYPE_SET_OF)     : self.gen_type_seqof(Obj)
        elif Obj.TYPE in (TYPE_SEQ, TYPE_SET)           : self.gen_type_seq(Obj)
        elif Obj.TYPE == TYPE_CLASS                     : self.gen_type_class(Obj)
        elif Obj.TYPE in (TYPE_OPEN, TYPE_ANY)          : self.gen_type_open(Obj)
        elif Obj.TYPE == TYPE_EXT                       : self.gen_type_ext(Obj)
        elif Obj.TYPE == TYPE_EMB_PDV                   : self.gen_type_embpdv(Obj)
        elif Obj.TYPE == TYPE_CHAR_STR                  : self.gen_type_charstr(Obj)
        else:
            raise(ASN1Err('{0}.{1}: unknown ASN.1 type, {2}'\
                  .format(self._mod_name, Obj._name, Obj.TYPE)))
        #
        # 8) generate the table constraint
        self.gen_const_table(Obj)
        #
        # 9) keep track of the generated object
        self._all_.append(Obj._pyname)
        self._allobj_[Obj._pyname] = Obj
    
    def gen_set(self, Obj):
        #
        # generate the type first
        self.gen_type(Obj, compts=False)
        #
        # in case this is a parameterized object, no need to defined anything more
        if Obj._param:
            return
        #
        # now generate the set of values
        s = 'p.{0} = {1}'.format(Obj._pyname, set_to_defin(ASN1Set(Obj._val), Obj, self))
        self.wil(s)
    
    def gen_val(self, Obj):
        #
        # generate the type first
        self.gen_type(Obj, compts=False)
        #
        # in case this is a parameterized object, no need to defined anything more
        if Obj._param:
            return
        #
        # now generate the set of values
        s = '[]ASN1Ref{'
        v = value_to_defin(Obj._val, Obj, self)
        if isinstance(v, str):
            if Obj.TYPE == 'INTEGER':
                if Obj._val != None:
                    self.wil('p.{0} = {1}'.format(Obj._pyname, v))
                else:
                    self.wil('p.{0}.Val = {1}'.format(Obj._pyname, v))
                return
            else:
                s += 'NewASN1Ref({0}),'.format(v)
        else:
            for y in v:
              if len(y)==2:
                s += 'NewASN1RefWithMod({0}, {1}),'.format(y[0], y[1])
              else:
                s += 'NewASN1Ref({0}),'.format(y[0])

        s += '}'
        s = 'p.{0}.A_val = {1}'.format(Obj._pyname, s)
        self.wil(s)
    
    def _gen_type_init_attr(self, Obj, compts):
        attr = ['Name:"{0}"'.format(Obj._name),
                'Mode:"{0}"'.format(_mode_lut[Obj._mode])]
        # WNG: tag or typeref at the root of the object definition could be parameterized too
        if Obj._tag and isinstance(Obj._tag[0], integer_types):
            attr.append('Tag:"{0}"'.format(tag_to_defin(Obj._tag)))
        if Obj._typeref and isinstance(Obj._typeref.called, tuple):
            attr.append('Typeref:{0}'.format(typeref_to_defin(Obj)))
        if Obj._param:
            attr.append('Param:true')
        if compts:
            # this is for constructed objects components only
            if Obj._flag and FLAG_OPT in Obj._flag:
                attr.append('Opt:true')
            elif Obj._flag and FLAG_DEF in Obj._flag:
                if Obj._mode == MODE_SET:
                    # this can happen with CLASS fields
                    attr.append('Default:{0}'.format(set_to_defin(ASN1Set(Obj._flag[FLAG_DEF]), Obj, self)))
                else:
                    if Obj._mode == MODE_TYPE:
                        par = Obj._parent
                        while par is not None:
                            if par.TYPE == TYPE_CLASS:
                                assert()
                            par = par._parent
                    attr.append('Default:{0}'.format(value_to_defin(Obj._flag[FLAG_DEF], Obj, self)))
            if Obj.TYPE == TYPE_ANY and Obj._flag and FLAG_DEFBY in Obj._flag:
                attr.append('Defby:{0!r}'.format(Obj._flag[FLAG_DEFBY]))
            if Obj._flag and FLAG_UNIQ in Obj._flag:
                attr.append('Uniq:true')
            if Obj._group is not None:
                attr.append('Group:{0!r}'.format(Obj._group))
        return 'Asn:asn2gort.Asn{' + ', '.join(attr) + '}'
    
    #--------------------------------------------------------------------------#
    # specific types
    #--------------------------------------------------------------------------#
    
    def gen_type_bool(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_int(self, Obj):
        # named integer values
        if Obj._cont:
            #self.wdl('type {0} int'.format(Obj._pyname))
            # Cont is an ASN1Dict with {str: int}
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            for a in Obj._cont.items():
                  r = extract_charstr(Obj._pyname)[0]
                  #self.wdl('const {0} {1} = {2}'.format(a[0],r,a[1]))
                  self.wil('// Integer value {0}.{1} = {2}'.format(Obj._pyname, r,a[1]))
                  self.wil('p.{0}.Children.Add({1}, &AsnINT{{ Val:{2} }})'.format(r, qrepr(a[0]), a[1]))
            #self.wil('{0}._cont = ASN1Dict({1!r})'.format(Obj._pyname, list(Obj._cont.items())))
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_real(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
        # TODO: apply CONST_COMPS if exists
    
    def gen_type_enum(self, Obj):
        # enum content
        #self.wdl('type {0} int'.format(Obj._pyname))
        #self.wdl('const (')
        if Obj._cont:
            self.wil('var {0} = struct {{'.format(Obj._pyname))
            for a in Obj._cont.items():
                  r = extract_charstr(a[0])[0]
                  #self.wdl('\t{0} {1} = {2}'.format(a[0], Obj._pyname, a[1]))
                  #self.wil('// ENUM {0}.{1} = {2}'.format(Obj._pyname, r,a[1]))
                  #self.wil('p.{0}.Children.Add("{1}", NewAsnENUM({2}))'.format(Obj._pyname, r,a[1]))
                  self.wil('\t{0} int'.format(name_to_golang_exported(r)))
            #self.wil('{0}._cont = ASN1Dict({1!r})'.format(Obj._pyname, list(Obj._cont.items())))
            self.wil('}{')
            for a in Obj._cont.items():
                  r = extract_charstr(a[0])[0]
                  #self.wdl('\t{0} {1} = {2}'.format(a[0], Obj._pyname, a[1]))
                  #self.wil('// ENUM {0}.{1} = {2}'.format(Obj._pyname, r,a[1]))
                  #self.wil('p.{0}.Children.Add("{1}", NewAsnENUM({2}))'.format(Obj._pyname, r,a[1]))
                  self.wil('\t{0}, // ENUM {1}.{2} = {0}'.format(a[1],Obj._pyname, r))
            #self.wil('{0}._cont = ASN1Dict({1!r})'.format(Obj._pyname, list(Obj._cont.items())))
            self.wil('}')
            if Obj._type != "ENUMERATED":
                    if Obj._ext is None:
                        self.wil('p.{0}.ExtFlag = false'.format(Obj._pyname))
                        pass
                    else:
                        self.wil('p.{0}.ExtFlag = true'.format(Obj._pyname))
                        if len(Obj._ext) > 0:
                          s = 'p.{0}.Ext = []string{{'.format(Obj._pyname)
                          for x in Obj._ext:
                            s += '{0},'.format(qrepr(x))
                          s += "}"
                          self.wil(s)
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_bitstr(self, Obj):
        # content: named bit offsets
        if Obj._cont:
            # Cont is an ASN1Dict with {str: int}
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            for a in Obj._cont.items():
                  r = extract_charstr(a[0])[0]
                  self.wil('// Bitstring {0}.{1}'.format(Obj._pyname, r))
                  self.wil('p.{0}.Children.Add("{1}",{2})'.format(Obj._pyname, r))
            #self.wil('{0}._cont = ASN1Dict({1!r})'.format(Obj._pyname, list(Obj._cont.items())))
        # value constraint
        self.gen_const_val(Obj)
        # size constraint
        self.gen_const_sz(Obj)
        # containing constraint
        self.gen_const_contain(Obj)
    
    def gen_type_octstr(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
        # size constraint
        self.gen_const_sz(Obj)
        # containing constraint
        self.gen_const_contain(Obj)
    
    def gen_type_oid(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_str(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
        # size constraint
        self.gen_const_sz(Obj)
        # alphabet constraint
        Consts_alpha = [C for C in Obj.get_const() if C['type'] == CONST_ALPHABET]
        if Consts_alpha:
            Salpha = reduce_setdicts(Consts_alpha)
            self.wrl('p.{0}._const_alpha = {1}'.format(Obj._pyname, set_to_defin(Salpha, Obj, self)))
    
    def gen_type_time(self, Obj):
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_choice(self, Obj):
        # content: ASN1Dict of {name: ASN1Obj}
        if Obj._cont is not None:
            # TODO: apply CONST_COMPS if exists
            # create all objects of the content first
            links = ASN1Dict()
            for name in Obj._cont:
                Cont = Obj._cont[name]
                Cont._pyname = '_{0}_{1}'.format(Obj._pyname, name_to_defin(Cont._name))
                self.gen_type(Cont, compts=True)
                links[name] = Cont._pyname
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            # now link all of them in an ASN1Dict into the Obj content
            for a in links:
                  self.wil('// CHOICE {0}.{1} = {2}'.format(Obj._pyname, qrepr(a), links[a]))
                  self.wil('p.{0}.Children.Add({1},p.{2})'.format(Obj._pyname, qrepr(a), links[a]))
            #self.wil('{0}._cont = ASN1Dict(['.format(Obj._pyname))
            #for name in links:
            #    self.wil('    ({0!r}, {1}),'.format(name, links[name]))
            #self.wil('    ])')
            # extension
            if Obj._type != "ENUMERATED":
                if Obj._ext is None:
                    self.wil('p.{0}.ExtFlag = false'.format(Obj._pyname))
                    pass
                else:
                    self.wil('p.{0}.ExtFlag = true'.format(Obj._pyname))
                    if len(Obj._ext) > 0:
                      s = 'p.{0}.Ext = []string{{'.format(Obj._pyname)
                      for x in Obj._ext:
                        s += '{0},'.format(qrepr(x))
                      s += "}"
                      self.wil(s)
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_seq(self, Obj):
        # content: ASN1Dict of {name: ASN1Obj}
        if Obj._cont is not None:
            # TODO: apply CONST_COMPS if exists
            # create all objects of the content first
            links = ASN1Dict()
            for name in Obj._cont:
                Cont = Obj._cont[name]
                Cont._pyname = '_{0}_{1}'.format(Obj._pyname, name_to_defin(Cont._name))
                self.gen_type(Cont, compts=True)
                links[name] = Cont._pyname
            # now link all of them in an ASN1Dict into the Obj content
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            for name in links:
                self.wil('// ASNDICT {0}.{1} = {2}'.format(Obj._pyname, name, links[name]))
                self.wil('p.{0}.Children.Add("{1}", p.{2})'.format(Obj._pyname, name, links[name]))
            # extension
            if Obj._type != "ENUMERATED":
                if Obj._ext is None:
                    self.wil('p.{0}.ExtFlag = false'.format(Obj._pyname))
                    pass
                else:
                    self.wil('p.{0}.ExtFlag = true'.format(Obj._pyname))
                    if len(Obj._ext) > 0:
                      s = 'p.{0}.Ext = []string{{'.format(Obj._pyname)
                      for x in Obj._ext:
                        s += '{0},'.format(qrepr(x))
                      s += "}"
                      self.wil(s)
        # value constraint
        self.gen_const_val(Obj)
    
    def gen_type_seqof(self, Obj):
        # content: ASN1Obj
        if Obj._cont is not None:
            # TODO: apply CONST_COMP if exists
            # create the object of the content first
            Cont = Obj._cont
            Cont._pyname = '_{0}_{1}'.format(Obj._pyname, name_to_defin(Cont._name))
            self.gen_type(Cont)
            # now link it to the Obj content
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            self.wil('// SEQ OF {0}.{1} = {2}'.format(Obj._pyname,  qrepr(Cont._pyname),Cont._pyname))
            self.wil('p.{0}.Children.Add({1}, p.{2})'.format(Obj._pyname, qrepr(Cont._pyname),Cont._pyname))
        # value constraint
        self.gen_const_val(Obj)
        # size constraint
        self.gen_const_sz(Obj)
    
    def gen_type_class(self, Obj):
        # content: ASN1Dict of {name: ASN1Obj}
        if Obj._cont is not None:
            # create all objects of the content first
            links = ASN1Dict()
            for name in Obj._cont:
                Cont = Obj._cont[name]
                Cont._pyname = '_{0}_{1}'.format(Obj._pyname, name_to_defin(Cont._name))
                self.gen_type(Cont, compts=True)
                links[name] = Cont._pyname
            # now link all of them in an ASN1Dict into the Obj content
            #self.wil('{0}._cont = ASN1Dict(['.format(Obj._pyname))
            self.wil('p.{0}.Children = asn2gort.NewDict()'.format(Obj._pyname))
            for name in links:
                self.wil('// CLASS {0}.{1} = {2}'.format(Obj._pyname, qrepr(name), links[name]))
                self.wil('p.{0}.Children.Add({1}, p.{2})'.format(Obj._pyname, qrepr(name), links[name]))
    
    def gen_type_open(self, Obj):
        if Obj._cont:
            assert()
        # value constraint for OPEN types are actually other ASN.1 types...
        Consts_val = [C for C in Obj._const if C['type'] == CONST_VAL]
        if Consts_val:
            if len(Consts_val) > 1:
                asnlog('WNG, {0}.{1}: multiple OPEN type value constraints, compiling only '\
                       'the first'.format(self._mod_name, Obj._name))
            Const = Consts_val[0]
            # process the root part of the constraint
            ind = 0
            if Const['root']:
                root = []
                for O in Const['root']:
                    O._pyname = '_{0}_val_{1!r}'.format(Obj._pyname, ind)
                    self.gen_type(O)
                    ind += 1
                    root.append(O._pyname)
                root = '[{0}]'.format(', '.join(root))
            else:
                root = '[]'
            # process the extended part of the constraint
            if Const['ext'] is not None:
                ext = []
                for O in Const['ext']:
                    O._pyname = '_{0}_val_{1!r}'.format(Obj._pyname, ind)
                    self.gen_type(O)
                    ind += 1
                    ext.append(O._pyname)
                ext = '[{0}]'.format(', '.join(ext))
            else:
                ext = 'None'
            # creates the ASN1Set which links to the object
            self.wrl('p.{0}.A_const_val = asn2gort.ASN1Set(rv={1}, ev={2})'.format(Obj._pyname, root, ext))
        if [C for C in Obj.get_const() if C['type'] not in \
        (CONST_TABLE, CONST_VAL, CONST_CONSTRAIN_BY)]:
            assert()
    
    def gen_type_ext(self, Obj):
        # TODO: apply CONST_COMPS if exists
        pass
    
    def gen_type_embpdv(self, Obj):
        # TODO: apply CONST_COMPS if exists
        pass
    
    def gen_type_charstr(self, Obj):
        # TODO: apply CONST_COMPS if exists
        pass
    
    #--------------------------------------------------------------------------#
    # specific constraints
    #--------------------------------------------------------------------------#
    
    def gen_const_sz(self, Obj):
        # if no local size constraint, just return
        if not [C for C in Obj._const if C['type'] == CONST_SIZE]:
            return
        # size constraint: reducing all size constraint to a single one
        Consts_size = [C for C in Obj.get_const() if C['type'] == CONST_SIZE]
        if Consts_size:
            # size is a set of INTEGER values
            SzProxy = INT()
            Ssz = reduce_setdicts(Consts_size)
            # SIZE has always an lb of 0 for range, even if they are defined as (MIN..XYZ)
            for rr in Ssz._rr:
                if rr.lb is None:
                    rr.lb = 0
            for er in Ssz._er:
                if er.lb is None:
                    er.lb = 0
            self.wil('p.{0}.A_const_sz = {1}'.format(Obj._pyname, set_to_defin(Ssz, SzProxy, self)))
    
    def gen_const_val(self, Obj):
        # if no local value constraint, just return
        if not [C for C in Obj._const if C['type'] == CONST_VAL]:
            return
        # value constraint: reducing all value constraint to a single one
        Consts_val = [C for C in Obj.get_const() if C['type'] == CONST_VAL]
        if Consts_val:
            Sval = reduce_setdicts(Consts_val)
            self.wil('p.{0}.A_const_val = {1}'.format(Obj._pyname, set_to_defin(Sval, Obj, self)))

    def gen_const_table(self, Obj):
        # table constraint: processing only a local and single constraint
        Consts_tab = [C for C in Obj._const if C['type'] == CONST_TABLE]
        if Consts_tab:
            if len(Consts_tab) > 1:
                asnlog('WNG, {0}.{1}: multiple table constraint, but compiling only the first'\
                       .format(self._mod_name, Obj._name))
            Const = Consts_tab[0]
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
            # now link it to the Obj constraint
            self.wil('p.{0}.A_const_tab = p.{1}'.format(Obj._pyname, link_name))
            # define the @ identifier
            if Const['at'] is None:
                self.wil('p.{0}.A_const_tab_at = nil'.format(Obj._pyname))
            else:
#                self.wil('{0}._const_tab_at = ASN1Ref{{"{1}","{2}"}}'.format(Obj._pyname, tuple(Const['at'])))
                self.wil('p.{0}.A_const_tab_at = asn2gort.NewASN1RefWithMod("{1}","{2}")'.format(Obj._pyname, Const['at'][0],Const['at'][1]))
             # define the table object identifier
            try:
                self.wil('p.{0}.A_const_tab_id = {1}'.format(Obj._pyname, qrepr(Obj._typeref.ced_path[-1])))
            except:
                asnlog('WNG, {0}.{1}: unavailable table constraint ident, not compiling it'\
                       .format(self._mod_name, Obj._name))
                self.wil('p.{0}.A_const_tab_id = nil')
    
    def gen_const_contain(self, Obj):
        # CONTAINING constraint: processing only a local and single constraint
        Consts_contain = [C for C in Obj._const if C['type'] == CONST_CONTAINING]
        if Consts_contain:
            if len(Consts_contain) > 1:
                asnlog('WNG, {0}.{1}: multiple CONTAINING constraint, compiling only '\
                       'the first'.format(self._mod_name, Obj._name))
            Const = Consts_contain[0]
            if Const['enc'] is not None:
                # Const['enc'] is an OID value
                EncProxy = OID()
                self.wrl('p.{0}._const_cont_enc = {1}'\
                         .format(Obj._pyname, value_to_defin(Const['enc'], EncProxy, self)))
            else:
                # create the contained object first
                Const['obj']._pyname = '_{0}_contain'.format(Obj._pyname)
                self.gen_type(Const['obj'])
                # now link it to the Obj constraint
                self.wrl('p.{0}._const_cont = {1}'.format(Obj._pyname, Const['obj']._pyname))

