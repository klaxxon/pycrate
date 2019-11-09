package asn2gort

// InterfaceMap - Dictionary of interfaces{}
type InterfaceMap struct {
	Data map[string]interface{}
}

// NewDict creates a new dictionary of interfaces
func NewDict() *InterfaceMap {
	return &InterfaceMap{Data: make(map[string]interface{})}
}

// Add named interface.  If it exists, overwrite
func (a *InterfaceMap) Add(s string, i interface{}) {
	a.Data[s] = i
}

// Get interface from name
func (a *InterfaceMap) Get(i int) interface{} {
	for _, b := range a.Data {
		if i == 0 {
			return b
		}
		i--
	}
	return nil
}
