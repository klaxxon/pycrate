package main

import (
	. "asn2gort"
	"fmt"
	"s1ap"
)

func main() {
	x := &s1ap.S1AP_PDU{}
	if err := PreLoad(x); err != nil {
		fmt.Print(err, DumpDebugInfo())
		return
	}
	d := NewPERDecoderFromString("0011002d000004003b00080009f107000019b0003c400a0380737273656e62303100400007000001c009f1070089400140", true)
	err := d.Unmarshal(x)
	if err != nil {
		fmt.Print(err)
	}
	fmt.Print(DumpDebugInfo())
	fmt.Println(DumpStruct(x))
}
