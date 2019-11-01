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
	_parent    *Asn
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
	Decode(*PERDecoder) error
	setParent(*Asn)
	getParent() *Asn
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

func (c *Asn) setParent(a *Asn) {
	c._parent = a
}

func (c *Asn) getParent() *Asn {
	return c._parent
}

type InterfaceMap struct {
	Data map[string]AsnI
}

func (a *InterfaceMap) Add(s string, i AsnI) {
	a.Data[s] = i
}

func (a *InterfaceMap) Get(i int) AsnI {
	for _, b := range a.Data {
		if i == 0 {
			return b
		}
		i--
	}
	return nil
}

type BitsNeeded interface {
	getBitsNeeded() int
}

type AsnENUM struct {
	Asn
	Val            uint64
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

type AsnCHOICE struct {
	Asn
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
	_bitsneeded    byte
}

func (a *AsnCHOICE) getBitsNeeded() byte {
	return a._bitsneeded
}

func (a *AsnCHOICE) setBitsNeeded(i byte) {
	a._bitsneeded = i
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
	return x.Decode(p)
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
