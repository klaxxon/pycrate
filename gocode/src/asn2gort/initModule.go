package asn2gort

import (
	"fmt"
	"reflect"
	"strings"
)

type GLOBAL struct {
	Mod map[string]map[string][]interface{}
}

var GLOB GLOBAL

func init() {
	GLOB = GLOBAL{Mod: make(map[string]map[string][]interface{})}
}

func InitModule(name string, mod AsnI) {
	fmt.Printf("Init module %s\n", name)
	GLOB.Mod[name] = make(map[string][]interface{})
	GLOB.Mod[name]["_obj_"] = str2int(mod.getObj())
	if name[0] != '_' {
		GLOB.Mod[name]["_type_"] = str2int(mod.getType())
		GLOB.Mod[name]["_set_"] = str2int(mod.getSet())
		GLOB.Mod[name]["_val_"] = str2int(mod.getVal())
		GLOB.Mod[name]["_class_"] = str2int(mod.getClass())
		GLOB.Mod[name]["_param_"] = str2int(mod.getParam())
	}
	for _, o := range mod.getObj() {
		f := mod.getField(goName(o))
		if f != nil {
			GLOB.Mod[name][o] = []interface{}{f}
		}
	}
	//spew.Dump(mod)
	gen_mod(mod)
}

func gen_mod(mod AsnI) {
	v := reflect.ValueOf(mod)
	vnum := v.Elem().NumField()
	for a := 0; a < vnum; a++ {
		ve := v.Elem().Field(a)
		for ve.Kind() == reflect.Ptr {
			if ve.IsNil() {
				break
			}
			//addr := ve.Pointer()
			ve = ve.Elem()
			if ve.Kind() == reflect.Interface {
				if ve.IsNil() {
					break
				}
				ve = ve.Elem()
			}
		}
		if ve.CanInterface() {
			var i interface{}
			t := ve.Type().String()
			fmt.Println(t)
			if len(t) > 10 && t[0:9] == "asn2gort." && t != "asn2gort.Asn" {
				t = t[9:]
				if ve.IsValid() {
					i = ve.Interface()
					switch t {
					case "AsnCHOICE", "AsnSEQ", "AsnSET", "AsnCLASS":
						if t == "AsnCHOICE" {
							asn := i.(AsnCHOICE).Asn
							mapParents(i.(AsnCHOICE).AsnI)
							var ext []string
							asn._root = make([]string, 0)
							if asn.ExtFlag {
								ext = asn.Ext
							}
							for a, _ := range asn.Cont.Data {
								if asn.ExtFlag {
									if inStrArray(ext, a) {
										break
									}
								}
								asn._root = append(asn._root, a)
							}
							if !asn.ExtFlag {
								//asn._const_ind = ASN1Set{RR: []ASN1Ref{ASN1RangeInt{LL: 0, UL: len(ty.Asn._root) - 1}}}
							} else if len(asn.Ext) == 0 {
								//asn._const_ind = ASN1Set{RR: []ASN1RangeInt{ASN1RangeInt{ll: 0, ul: len(ty.Asn._root) - 1}, EV: make([]ASN1RangeInt, 0)}}
							}
						}
					}
				}
			}
		}
	}
	/*
		switch t[0]:
		if mode == "MODE_TYPE" {
			gen_type(i)
		} else if mode == "MODE_SET" {
			gen_set(i)
		} else if mode == "MODE_VALUE" {
			gen_val(i)
		}
	*/
}

func mapParents(asn AsnI) {
	for _, a := range asn.getCont().Data {
		a.(AsnI).setParent(asn)
	}
}

func inStrArray(arr []string, s string) bool {
	for _, a := range arr {
		if a == s {
			return true
		}
	}
	return false
}

func gen_type(i interface{}) {

}

func gen_set(i interface{}) {

}
func gen_val(i interface{}) {

}

func str2int(m []string) []interface{} {
	z := make([]interface{}, 0)
	for _, a := range m {
		z = append(z, a)
	}
	return z
}

func goName(s string) string {
	s = strings.Replace(s, " ", "_", -1)
	return strings.Replace(s, "-", "_", -1)
}
