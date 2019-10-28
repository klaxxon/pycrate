package asn2gort

type InterfaceMap struct {
}

func (a *InterfaceMap) Add(s string, i interface{}) {

}

type AsnENUM struct {
	Name           string
	Mode           string
	Tag            string
	Opt            bool
	Cont           InterfaceMap
	Typeref        interface{}
	Default        string
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
	Ext            []string
}

type AsnCHOICE struct {
	Name           string
	Mode           string
	Tag            string
	Opt            bool
	Cont           InterfaceMap
	Typeref        interface{}
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
	Ext            []string
}

type AsnCLASS struct {
	Name        string
	Mode        string
	Tag         string
	Cont        InterfaceMap
	Typeref     interface{}
	Val         ASN1Set
	A_const_tab interface{}
	A_val       interface{}
}

type AsnOPEN struct {
	Name           string
	Mode           string
	Tag            string
	Opt            bool
	Typeref        interface{}
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnSEQ struct {
	Name    string
	Mode    string
	Tag     string
	Opt     bool
	Param   bool
	Typeref ASN1RefType
	A_cont  InterfaceMap
}

type AsnSEQ_OF struct {
	Name       string
	Mode       string
	Tag        string
	Opt        bool
	Typeref    interface{}
	Param      interface{}
	A_cont     InterfaceMap
	A_const_sz interface{}
}

type AsnOCT_STR struct {
	Name       string
	Mode       string
	Tag        string
	Opt        bool
	Typeref    interface{}
	A_const_sz interface{}
}

type AsnBIT_STR struct {
	Name       string
	Mode       string
	Tag        string
	Opt        bool
	Typeref    interface{}
	A_const_sz interface{}
}

type AsnSTR_PRINT struct {
	Name       string
	Mode       string
	Tag        string
	Typeref    interface{}
	A_const_sz interface{}
	Cont       InterfaceMap
}

type AsnNULL struct {
	Name string
	Mode string
	Tag  string
}

type AsnINT struct {
	Name           string
	Mode           string
	Tag            string
	Typeref        interface{}
	Uniq           bool
	Opt            bool
	Cont           InterfaceMap
	_val           int64
	A_val          interface{}
	A_const_val    ASN1Set
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type ASN1RangeInt struct {
	lb int64
	ub int64
}

type AsnOID struct {
	Name string
	Mode string
	Tag  string
}

type ASN1Ref struct {
	Name string
	Obj  interface{}
}

type ASN1Set struct {
	RR []ASN1Ref
	RV []ASN1Ref
	EV []ASN1Ref
	ER []ASN1Ref
}

type ASN1RefType struct {
	Mod string
	Obj string
}

type AsnReference struct {
	Mod string
	Obj string
}

type ASN1RefClassField struct {
	Ref AsnReference
	Obj string
}

type ASN1Dict struct {
	Ref []ASN1Ref
}
