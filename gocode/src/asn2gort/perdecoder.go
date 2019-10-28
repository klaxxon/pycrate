package asn2gort

import (
	"encoding/hex"
	"fmt"
	"log"
	"strings"
)

type PERDecoder struct {
	data        []byte
	aper        bool
	currentByte uint
	currentBit  byte
}

func NewPERDecoder(data []byte, aligned bool) *PERDecoder {
	return &PERDecoder{data: data, currentByte: 0, currentBit: 0, aper: aligned}
}

// String must be 2 character hexes optionally separated by spaces
func NewPERDecoderFromString(data string, aligned bool) *PERDecoder {
	d, err := hex.DecodeString(strings.Replace(data, " ", "", -1))
	if err != nil {
		log.Fatal("Hex conversion in NewPERFromString: " + err.Error())
	}
	return NewPERDecoder([]byte(d), aligned)
}

func (per *PERDecoder) GetPosition() int {
	return int(per.currentByte)
}

func (per *PERDecoder) LenBytes() int {
	return len(per.data)
}

func (per *PERDecoder) Flush(cnt int) error {
	if (len(per.data) - cnt - int(per.currentByte)) < 0 {
		return fmt.Errorf("Flush %d bytes exceeds remaining data", cnt)
	}
	per.currentBit = 0
	per.currentByte += uint(cnt)
	return nil
}

func (per *PERDecoder) SeekBit(pos int) {
	per.currentByte = uint(pos >> 3)
	per.currentBit = byte(pos & 7)
}

func (per *PERDecoder) GetBit(p *byte) error {
	if per.bitsLeft() == 0 {
		return fmt.Errorf("Not enough bits left for GetBit")
	}
	x := (per.data[per.currentByte] >> (7 - per.currentBit)) & 1
	per.currentBit++
	if per.currentBit == 8 {
		per.currentBit = 0
		per.currentByte++
	}
	*p = x
	return nil
}

func (per *PERDecoder) GetBitAt(pos int, p *byte) error {
	posbyte := pos >> 3
	if posbyte >= len(per.data) {
		return fmt.Errorf("Not enough bits left for GetUintVal")
	}
	posbit := byte(pos & 7)
	*p = (per.data[posbyte] >> (7 - posbit)) & 1
	return nil
}

func (per *PERDecoder) GetUintVal(bits int, p *uint64) error {
	if per.bitsLeft() < bits {
		return fmt.Errorf("Not enough bits left for GetUintVal")
	}
	var x uint64 = 0
	var z byte
	for a := 0; a < bits; a++ {
		x <<= 1
		if err := per.GetBit(&z); err != nil {
			return err
		}
		x |= uint64(z)
	}
	*p = x
	return nil
}

func (per *PERDecoder) GetByte(p *byte) error {
	if per.bitsLeft() < 8 {
		return fmt.Errorf("Not enough bits left for GetByte")
	}
	c := byte(0)
	var z byte
	for a := 0; a < 8; a++ {
		c <<= 1
		if err := per.GetBit(&z); err != nil {
			return err
		}
		c |= z
	}
	*p = c
	return nil
}

func (per *PERDecoder) Align() {
	var p byte
	for {
		if per.currentBit == 0 {
			return
		}
		per.GetBit(&p)
	}
}

func (per *PERDecoder) GetLength(p *int) error {
	if per.aper {
		per.Align()
	}
	var b byte
	if err := per.GetByte(&b); err != nil {
		return err
	}
	if (b & 0x80) == 0 {
		*p = int(b & 0x7f)
		return nil
	}
	l := int(b & 0x7f)
	length := 0
	for a := 0; a < l; a++ {
		length <<= 8
		var c byte
		if err := per.GetByte(&c); err != nil {
			return err
		}
		length |= int(c)
	}
	*p = length
	return nil
}

func (per *PERDecoder) bitsLeft() int {
	return 8*(len(per.data)-int(per.currentByte)) - int(per.currentBit)
}
