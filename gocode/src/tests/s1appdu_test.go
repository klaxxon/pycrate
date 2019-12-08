package tests

import (
	"asn2gort"
	pdu "s1ap"
	"testing"
)

var enums = map[string]map[string]string{"a": {"aa": "aaa"}}

func TestS1APPdu(t *testing.T) {
	pdu1 := pdu.S1apPdu{}
	enc := pdu1.Encode()
	per := asn2gort.NewPERDecoderFromString(enc, false)
	pdu2 := pdu.S1apPdu{}.S1AP_PDU
	pdu2.Decode(per)
}
