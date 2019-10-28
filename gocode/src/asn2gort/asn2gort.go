package asn2gort

type AsnI interface {
	getObj() []string
	getType() []string
	getSet() []string
	getVal() []string
	getClass() []string
	getParam() []string
	getField(s string) interface{}
	Decode(*PERDecoder) error
	//Encode(*PERDecoder) error
}

type InterfaceMap struct {
	Data map[string]interface{}
}

func (a *InterfaceMap) Add(s string, i interface{}) {
	a.Data[s] = i
}

type InterfaceSet struct {
	Data []interface{}
}

func (a *InterfaceSet) Add(s string, i interface{}) {
	a.Data = append(a.Data, i)
}

func (a *InterfaceSet) Get(i int) interface{} {
	return a.Data[i]
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
	ExtFlag        bool
	Ext            []string
}

type AsnCHOICE struct {
	Name           string
	Mode           string
	Tag            string
	Opt            bool
	Cont           InterfaceSet
	Typeref        interface{}
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
	ExtFlag        bool
	Ext            []string
}

func (a *AsnCHOICE) Decode(p *PERDecoder) error {
	var ext byte
	a.Ext = nil
	if a.ExtFlag {
		if err := p.GetBit(&ext); err != nil {
			return err
		}
	}
	breq := bitsNeeded(uint64(len(a.Cont.Data)))
	var idx uint64
	if err := p.GetUintVal(breq, &idx); err != nil {
		return err
	}
	x := a.Cont.Get(int(idx))
	return x.(AsnI).Decode(p)
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
	Cont    InterfaceSet
	ExtFlag bool
	Ext     []string
}

func (a AsnSEQ) Decode(p *PERDecoder) error {
	return nil
}

type AsnSEQ_OF struct {
	Name       string
	Mode       string
	Tag        string
	Opt        bool
	Typeref    interface{}
	Param      interface{}
	Cont       InterfaceSet
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
