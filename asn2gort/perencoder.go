package asn2gort

import (
	"encoding/hex"
	"math"
)

type PEREncoder struct {
	data        []byte
	aper        bool
	currentByte byte
	currentBit  byte
}

func NewPEREncoder(aligned bool) *PEREncoder {
	return &PEREncoder{data: make([]byte, 0), aper: aligned}
}

func (p *PEREncoder) GetData() []byte {
	return p.data
}

func (p *PEREncoder) Align() {
	if p.currentBit != 0 {
		if p.currentBit != 0 {
			p.currentByte <<= (8 - p.currentBit)
		}
		p.data = append(p.data, p.currentByte)
	}
	p.currentByte = 0
	p.currentBit = 0
}

func (p *PEREncoder) AddBit(bit byte) {
	if bit != 0 {
		bit = 1
	}
	p.currentByte <<= 1
	p.currentByte |= bit
	p.currentBit++
	if p.currentBit >= 8 {
		p.data = append(p.data, p.currentByte)
		p.currentByte = 0
		p.currentBit = 0
	}
}

func (p *PEREncoder) GetDataString() string {
	return hex.EncodeToString(p.data)
}

func (p *PEREncoder) AddByte(i byte) {
	for a := 0; a < 8; a++ {
		p.AddBit(i & 0x80)
		i <<= 1
	}
}

func bitsNeeded(i uint64) int {
	f := math.Log2(float64(i))
	bits := int(f)
	if (f - float64(bits)) == 0 {
		return bits
	}
	return bits + 1
}

func (p *PEREncoder) AddLength(i int) {
	if p.aper {
		p.Align()
	}
	if i < 128 {
		p.AddByte(byte(i))
		return
	}
	bits := bitsNeeded(uint64(i))
	bytes := (bits + 7) / 8
	p.AddByte(0x80 | byte(bytes))
	for a := bytes - 1; a >= 0; a-- {
		p.AddByte(byte((i >> uint(a*8)) & 0xff))
	}
}

func (p *PEREncoder) Close() {
	if p.currentBit == 0 {
		return
	}
	p.data = append(p.data, p.currentByte<<(8-p.currentBit))
}
