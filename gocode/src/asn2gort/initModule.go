package asn2gort

import (
	"fmt"
	"strings"
)

type GLOBAL struct {
	Mod map[string]map[string][]interface{}
}

var GLOB GLOBAL

func init() {
	GLOB = GLOBAL{Mod: make(map[string]map[string][]interface{})}
}

func InitModule(name string, mod AsnI, i interface{}) {
	fmt.Printf("Init module %s\n", name)
	GLOB.Mod[name] = make(map[string][]interface{})
	GLOB.Mod[name]["_obj_"] = str2int(mod.getObj())
	if name[0] != ' ' {
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
