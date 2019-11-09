package asn2gort

type ASN1Ref struct {
	called   string
	ced_path []interface{}
	items    map[string]interface{}
}

func NewASN1Ref(ced_path ...interface{}) *ASN1Ref {
	return &ASN1Ref{ced_path: ced_path}
}

func NewASN1RefWithMod(called string, ced_path []interface{}) *ASN1Ref {
	return &ASN1Ref{called: called, ced_path: ced_path}
}

type ASN1RefI interface {
	getItem(kw string) interface{}
	setItem(kw string, arg interface{})
	string() string
}

type ASN1RefType struct {
	Key string
	Val string
}

func NewASN1RefType(k, v string) *ASN1RefType {
	return &ASN1RefType{Key: k, Val: v}
}

type ASNRefChoiceComp struct {
	ASN1Ref
}

type ASN1RefInstOf struct {
	ASN1Ref
}

type ASN1RefClassField struct {
	ASN1Ref
}

type ASN1RefClassIntern struct {
	ASN1Ref
}

func (a *ASN1Ref) getItem(s string) []interface{} {
	if s == "called" {
		return []interface{}{a.called}
	} else if s == "ced_path" {
		return a.ced_path
	} else {
		return []interface{}{a.items[s]}
	}
}

func (a *ASN1Ref) setItem(s string, args []interface{}) {
	if s == "called" {
		a.called = args[0].(string)
	} else if s == "ced_path" {
		a.ced_path = args[1:]
	} else {
		a.items[s] = args[0]
	}
}
