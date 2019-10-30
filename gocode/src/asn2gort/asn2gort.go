package asn2gort

type Asn struct {
	AsnI
	Mode       string
	Name       string
	Tag        string
	Opt        bool
	Uniq       bool
	Default    string
	Param      bool
	ExtFlag    bool
	Ext        []string
	Typeref    interface{}
	Cont       InterfaceMap
	_root      []string
	_const_ind ASN1Set
	_parent    AsnI
	Obj_       []string
	Type_      []string
	Set_       []string
	Val_       []string
	Class_     []string
	Param_     []string
}

type AsnI interface {
	getObj() []string
	getType() []string
	getSet() []string
	getVal() []string
	getClass() []string
	getParam() []string
	getField(s string) interface{}
	getMode() string
	getObjects() []interface{}
	getCont() *InterfaceMap
	setParent(AsnI)
	getParent() AsnI
	Decode(*PERDecoder) error
	//Encode(*PERDecoder) error
}

func (a *Asn) getObj() []string {
	return a.Obj_
}

func (a *Asn) setParent(aparent AsnI) {
	a._parent = aparent
}

func (a *Asn) getParent() AsnI {
	return a._parent
}

func (a *Asn) getCont() *InterfaceMap {
	return &a.Cont
}

func (a *Asn) getMode() string {
	return a.Mode
}

type InterfaceMap struct {
	Data map[string]interface{}
}

func (a *InterfaceMap) Add(s string, i interface{}) {
	a.Data[s] = i
}

func (a *InterfaceMap) Get(i int) interface{} {
	for _, b := range a.Data {
		if i == 0 {
			return b
		}
		i--
	}
	return nil
}

/*
type InterfaceSet struct {
	Data []interface{}
}

func (a *InterfaceSet) Add(s string, i interface{}) {
	a.Data = append(a.Data, i)
}

func (a *InterfaceSet) Get(i int) interface{} {
	return a.Data[i]
}
*/

type AsnENUM struct {
	Asn
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnCHOICE struct {
	Asn
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
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
	x := a.getCont().Get(int(idx))
	return x.(AsnI).Decode(p)
}

type AsnCLASS struct {
	Asn
	Val         ASN1Set
	A_const_tab interface{}
	A_val       interface{}
}

type AsnOPEN struct {
	Asn
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnSEQ struct {
	Asn
}

func (a AsnSEQ) Decode(p *PERDecoder) error {
	return nil
}

type AsnSEQ_OF struct {
	Asn
	A_const_sz interface{}
}

type AsnOCT_STR struct {
	Asn
	A_const_sz interface{}
}

type AsnBIT_STR struct {
	Asn
	A_const_sz interface{}
}

type AsnSTR_PRINT struct {
	Asn
	A_const_sz interface{}
}

type AsnNULL struct {
	Asn
}

type AsnINT struct {
	Asn
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
	Asn
}

type ASN1Ref struct {
	Mod string
	Obj interface{}
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
