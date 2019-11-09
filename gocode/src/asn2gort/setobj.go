package asn2gort

type ASN1RangeInt struct {
	typestr string
	lb      int
	lb_incl bool
	ub      int
	ub_incl bool
}

func NewASN1RangeInt(lb, ub int) *ASN1RangeInt {
	return &ASN1RangeInt{lb: lb, ub: ub}
}

type ASN1Set struct {
	RR []*ASN1Ref
	RV []*ASN1Ref
	EV []*ASN1Ref
	ER []*ASN1Ref
}

type ASN1RangeStr struct {
}

type ASN1RangeReal struct {
}
