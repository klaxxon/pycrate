package asn2gort

import "reflect"

type Asn struct {
	AsnI
	Mode        string
	Name        string
	Tag         string
	Type        string
	Oid         []int
	Opt         bool
	Uniq        bool
	Default     string
	Param       bool
	ExtFlag     bool
	Ext         []string
	Typeref     interface{}
	All         []interface{}
	Children    *InterfaceMap
	_root       []string
	_const_ind  ASN1Set
	_parent     *Asn
	_bitsNeeded byte
	Obj_        []string
	Type_       []string
	Set_        []string
	Val_        []string
	Class_      []string
	Param_      []string
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
	getAll() []interface{}
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

func (a *Asn) getAll() []interface{} {
	return a.All
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
	return a.Children
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

type AsnENUM struct {
	Asn
	Val            uint64
	A_const_tab    interface{}
	A_const_tab_at interface{}
	A_const_tab_id string
}

func NewAsnENUM(val uint64) *AsnENUM {
	return &AsnENUM{Val: val}
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
	var ext byte
	a.Ext = nil
	if a.ExtFlag {
		if err := p.GetBit(&ext); err != nil {
			return err
		}
	}
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

type AsnOID struct {
	Asn
}

type ASN1Dict struct {
	Ref []ASN1Ref
}
