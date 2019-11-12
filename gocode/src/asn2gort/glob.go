package asn2gort

type GLOBAL struct {
	Mod map[string]map[string][]interface{}
	OID map[string]string
}

var GLOB GLOBAL

func init() {
	GLOB = GLOBAL{Mod: make(map[string]map[string][]interface{})}

	GLOB.OID = make(map[string]string)
}

func getAsnObj(ref interface{}) interface{} {
	return nil
}
