package main

import (
	. "asn2gort"
	"fmt"
	"s1ap"
)

func main() {
	x := &s1ap.S1AP_PDU{}
	if err := PreLoad(x); err != nil {
		fmt.Print(err)
		return
	}
	d := NewPERDecoderFromString("0011003F000004003B00080000F11000070800003C400A0380617269632D654E42004000190300030000F1100002C000F11000028000F11000024000F1100089000100", true)
	err := d.Unmarshal(x)
	if err != nil {
		fmt.Print(err, DumpDebugInfo())
	}
}
