Adding GoGenerate to generate Go code. Work in progress.....

```
package main

import (
	"asn2gort"
	pdu "s1ap"
)

func main() {
	per := asn2gort.NewPERDecoderFromString("0011003F000004003B00080000F11000070800003C400A0380617269632D654E42004000190300030000F1100002C000F11000028000F11000024000F1100089000100", false)
	x := &S1ap_Pdu{}
	per.Unmarshal(x)
}
```

License
=======

The whole library is licensed under LGPL v2.1 and is compatible with more recent 
version of the LGPL: all licensed files have an header making it self-explanatory.
For more details, please report to the 
[license.txt](https://github.com/p1sec/pycrate/license.txt) file.


Wiki
====

Pycrate has a growing [wiki](https://github.com/p1sec/pycrate/wiki/The-pycrate-wiki).

