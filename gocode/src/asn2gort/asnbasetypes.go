package asn2gort

import (
	"fmt"
	"strings"
)

// AsnI Is needed by all ASN usable structs
type AsnI interface {
	PERDecode(*PERDecoder) error
	PEREncode(*PEREncoder) error
}

// ListElement ??
type ListElement interface {
	SetSize(int)
	Put(*PERDecoder)
	Get() []byte
	Size() int
}

// AsnChoice Is an interface{} to the chosen struct
type AsnChoice interface{}

// AsnBITSTRING is a string of bits saved as bytes
type AsnBITSTRING struct {
	data []byte
	size int
}

// Size returns the number of bits in bitstring
func (o *AsnBITSTRING) Size() int {
	return o.size
}

// NewBitString return a new bitstring of specified size decoded from *p stream
func NewBitString(p *PERDecoder, size int) (*AsnBITSTRING, error) {
	bytes := size / 8
	if size&7 > 0 {
		bytes++
	}
	var bit byte
	bytepos := 0
	bitpos := 0
	var byteval byte
	bs := &AsnBITSTRING{data: make([]byte, bytes), size: size}
	for a := 0; a < size; a++ {
		byteval <<= 1
		err := p.GetBit(&bit)
		if err != nil {
			return nil, err
		}
		byteval |= bit
		bitpos++
		if bitpos == 8 {
			bs.data[bytepos] = byteval
			bytepos++
			bitpos = 0
			byteval = 0
		}
	}
	// Store and padding if necessary
	if bitpos > 0 {
		for {
			if bitpos == 8 {
				break
			}
			byteval <<= 1
			bitpos++
		}
		bs.data[bytepos] = byteval
	}
	return bs, nil
}

// VisibleString is a string of visible characters
type VisibleString struct {
	width int
	Value string
}

// Size length of VisibleString
func (o *VisibleString) Size() int {
	return o.width
}

// SetSize sets the size of the VisibleString
func (o *VisibleString) SetSize(width int) {
	o.width = width
}

// String returns the VisibleString
func (o *VisibleString) String() string {
	return o.Value
}

// LoadVisibleStrings loads zero or more strings
func LoadVisibleStrings(per *PERDecoder, vs *[]VisibleString, width int) error {
	per.Align()
	var len int
	err := per.GetLength(&len)
	if err != nil {
		return err
	}
	var byt byte
	for a := 0; a < len; a++ {
		z := ""
		for b := 0; b < width; b++ {
			if err := per.GetByte(&byt); err != nil {
				return err
			}
			c := byt
			z += string(c)
		}
		*vs = append(*vs, VisibleString{width: width, Value: z})
	}
	return nil
}

// Decode decodes
func (o *VisibleString) Decode(per *PERDecoder) error {
	var len int
	per.Align()
	o.Value = ""
	if err := per.GetLength(&len); err != nil {
		return err
	}
	var c byte
	for b := 0; b < len; b++ {
		if err := per.GetByte(&c); err != nil {
			return err
		}
		o.Value += string(c)
	}
	return nil
}

// VisibleStringTestFromString tests the visiblestring
func VisibleStringTestFromString(s, pat string) error {
	for a := 0; a < len(s); a++ {
		if !strings.Contains(pat, string(s[a])) {
			return fmt.Errorf("Error, VisibleString contains invalid character '%c'", s[a])
		}
	}
	return nil
}

// AsnDATETIME ???
type AsnDATETIME struct {
}

// Decode for ASNDateTime
func (o *AsnDATETIME) Decode(per *PERDecoder) {

}

// AsnINTEGER integer
type AsnINTEGER struct {
	AsnI
	FieldName  string
	MinValue   int64
	MaxValue   int64
	BitsNeeded int
	Value      int64
}

func (a *AsnINTEGER) PERDecode(p *PERDecoder) error {
	var bits int
	if a.BitsNeeded == 0 {
		if err := p.GetLength(&bits); err != nil {
			return err
		}
		bits *= 8
	} else {
		bits = a.BitsNeeded
	}
	var val uint64
	if err := p.GetUintVal(bits, &val); err != nil {
		return err
	}
	a.Value = int64(val + uint64(a.MinValue))
	return nil
}

func (i *AsnINTEGER) SetRange(min, max, bits int64) {
	i.MinValue = min
	i.MaxValue = max
	i.BitsNeeded = int(bits)
}

func (i *AsnINTEGER) GetValue() int64 {
	return i.Value
}

func (i *AsnINTEGER) Init() {
}

type AsnIA5String struct {
}

type AsnOBJECTIDENTIFIER struct {
	AsnI
	FieldName string
	Value     int64
}

func (a *AsnOBJECTIDENTIFIER) PERDecode(p *PERDecoder) error {
	return nil
}

// AsnBOOLEAN boolean value
//
type AsnBOOLEAN struct {
	Value bool
}

func (a *AsnBOOLEAN) PERDecode(p *PERDecoder) error {
	var bit byte
	if err := p.GetBit(&bit); err != nil {
		return err
	}
	a.Value = bit == 1
	return nil
}
