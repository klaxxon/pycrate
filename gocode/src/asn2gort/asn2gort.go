package asn2gort

import "reflect"

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
	Children   InterfaceMap
	_root      []string
	_const_ind ASN1Set
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
	getChildren() *InterfaceMap
	getParent() *Asn
	Decode(*PERDecoder) error
	//Encode(*PERDecoder) error
}

func (a *Asn) getField(s string) interface{} {
	v := reflect.ValueOf(a)
	i := v.FieldByName(s)
	if i.CanInterface() {
		return i.Interface()
	}
	return nil
}

func (a *Asn) getObj() []string {
	return a.Obj_
}

func (a *Asn) getType() []string {
	return a.Type_
}

func (a *Asn) getSet() []string {
	return a.Set_
}

func (a *Asn) getVal() []string {
	return a.Val_
}

func (a *Asn) getClass() []string {
	return a.Class_
}

func (a *Asn) getParam() []string {
	return a.Param_
}

func (a *Asn) getChildren() *InterfaceMap {
	return &a.Children
}

func (a *Asn) getMode() string {
	return a.Mode
}

type ContentI interface {
	setParent(*Asn)
}

type Child struct {
	Parent *Asn
}

func (c *Child) setParent(a *Asn) {
	c.Parent = a
}

type InterfaceMap struct {
	Data map[string]ContentI
}

func (a *InterfaceMap) Add(s string, i ContentI) {
	a.Data[s] = i
}

func (a *InterfaceMap) Get(i int) ContentI {
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
	Child
	Val            uint64
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnCHOICE struct {
	Asn
	Child
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
	breq := bitsNeeded(uint64(len(a.Children.Data)))
	var idx uint64
	if err := p.GetUintVal(breq, &idx); err != nil {
		return err
	}
	x := a.getChildren().Get(int(idx))
	return x.(AsnI).Decode(p)
}

type AsnCLASS struct {
	Asn
	Child
	Val         ASN1Set
	A_const_tab interface{}
	A_val       interface{}
}

type AsnOPEN struct {
	Asn
	Child
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnSEQ struct {
	Asn
	Child
}

func (a AsnSEQ) Decode(p *PERDecoder) error {
	return nil
}

type AsnSEQ_OF struct {
	Asn
	Child
	A_const_sz interface{}
}

type AsnOCT_STR struct {
	Asn
	Child
	A_const_sz interface{}
}

type AsnBIT_STR struct {
	Asn
	Child
	A_const_sz interface{}
}

type AsnSTR_PRINT struct {
	Asn
	Child
	A_const_sz interface{}
}

type AsnNULL struct {
	Asn
	Child
}

type AsnINT struct {
	Asn
	Child
	Val            int64
	A_val          interface{}
	A_const_val    ASN1Set
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type ASN1RangeInt struct {
	Lb uint64
	Ub uint64
}

type AsnOID struct {
	Asn
	Child
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
