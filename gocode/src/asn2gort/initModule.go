package asn2gort

import (
	"fmt"
	"log"
	"strings"
)

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
	/*
		for _, o := range mod.getObj() {
			f := mod.getField(goName(o))
			if f != nil {
				GLOB.Mod[name][o] = []interface{}{f}
			}
		}
	*/
	//spew.Dump(mod)
	gen_mod(mod)
}

func gen_mod(mod AsnI) {
	for _, Obj := range mod.getAll() {
		var asn *Asn
		asn = nil
		if o, ok := Obj.(*AsnOPEN); ok {
			asn = &o.Asn
			asn.Type = "AsnOPEN"
		} else if o, ok := Obj.(*AsnCHOICE); ok {
			asn = &o.Asn
			asn.Type = "AsnCHOICE"
		}
		if asn == nil {
			log.Panic("Missing type handler for", Obj)
		}
		fmt.Println("AsnOPEN", asn.Name, asn.Type)
		mapParents(asn)
		if asn.Type == "AsnCHOICE" || asn.Type == "AsnSEQUENCE" || asn.Type == "AsnSET" || asn.Type == "AsnCLASS" {
			if asn.Type == "AsnCHOICE" {
				var ext []string
				asn._root = make([]string, 0)
				if asn.ExtFlag {
					ext = asn.Ext
				}
				for a, _ := range asn.Children.Data {
					if asn.ExtFlag {
						if inStrArray(ext, a) {
							break
						}
					}
					asn._root = append(asn._root, a)
				}
				asn._bitsNeeded = byte(bitsNeeded(uint64(len(asn.Children.Data))))
				if !asn.ExtFlag {
					//asn._const_ind = ASN1Set{RR: []ASN1Ref{ASN1RangeInt{LL: 0, UL: len(ty.Asn._root) - 1}}}
				} else if len(asn.Ext) == 0 {
					//asn._const_ind = ASN1Set{RR: []ASN1RangeInt{ASN1RangeInt{ll: 0, ul: len(ty.Asn._root) - 1}, EV: make([]ASN1RangeInt, 0)}}
				}
			} else {
				//var ext []string
				asn._root = make([]string, 0)
				/*
					asn._root_mand = make([]string, 0)
					asn._root_opt = make([]string, 9)
					if asn.ExtFlag {
						ext = asn.Ext
					}
					for name, comp := range asn.Children.Data {
						if inStrArray(ext, name) {
							break
						}
						if comp.getOptional() || comp.getDefault() != "" {
							asn._root_opt = append(asn._root, name)
						} else {
							asn._root_mand = append(asn._root, name)

						}
						asn._root = append(asn._root, name)
					}
				*/
			}

			if asn.Type != "AsnCLASS" {
				if asn.Ext != nil {
					/*
						asn.Ext_ident = interface{}
						asn.Ext_group = interface{}
						for name,_ := range asn._ext {
								Comp := asn.Children.getByString(name)
								if Comp.getGroup() != nil {
										asn._ext_ident[name] = Comp._group
										//if Comp._group not in asn._ext_group {
										//		Obj._ext_group[Comp._group] = []
										//}
										Comp._ext_group[Comp._group].append(name)

								}
						}*/
					log.Panic("Unhandled!")
				}
			}
			if (asn.Type == "AsnSEQUENCE" || asn.Type == "AsnSET") && len(asn.Ext) != 0 {
				/*
					for _, ident := range asn.Ext {
						if x, ok := asn.ExtIdent[ident]; ok {
							log.Panic("Unhandled!")
							// ident is in a group
							g_idents := asn.ExtGroup[x]
							if strings.Index(g_idents, ident) == 0 {
								// 1st component
								asn.ExtNest = append(asn.ExtNest, ident)
							} else {
								asn.ExtNest = append(asn.ExtNest, ident)
							}
						} else {
							asn.ExtNest = append(asn.ExtNest, ident)
						}
					}

					for gid, idents := range asn.ExtGroup {
						log.Panic("Unhandled!", gid, idents)
					}
				*/
			}
		} else if asn.Type == "AsnOID" && asn.Mode == "MODE_VALUE" {
			/*
				obj := Obj.(AsnOID)
				key := fmt.Sprintf("%v", obj.Val)
				if x, ok := GLOB.OID[key]; ok {
					if x != asn.Name {
						log.Panicf("init_modules: different OID objects (%s, %s) with same OID value %v\n", asn.Name, x, key)
					}
				} else if obj.Val != nil {
					GLOB.OID[key] = asn.Name
				}
			*/
		} else if asn.Type == "AsnCLASS" && asn.Mode == "MODE_SET" {
			buildClassSetDict(Obj.(*AsnCLASS))
		} else {
			log.Panic("Unhandled type in InitModule.gen_mod " + asn.Type)
		}
	}
}

func getTypeRef(Obj interface{}) interface{} {
	/*
		var tr interface{}
		if ref, ok := Obj.(ASN1RefType); ok {
			tr = getAsnObj(ref)
		}
	*/
	return nil
}

func buildClassSetDict(obj *AsnCLASS) {
	//key := nil
	//tr := getTypeRef(obj)
}

func mapParents(asn *Asn) {
	for a, b := range asn.getChildren().Data {
		b.(AsnI).setParent(asn)
		fmt.Printf("Mapping %s to parent %s\n", a, asn.Name)
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
