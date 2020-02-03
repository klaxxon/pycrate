Adding GoGenerate to generate tagged Go structs. Work in progress.....
Takes ASN.1 files for imput and creates a set of go files contained tagged structs for reflection based encoding/decoding.

```
/* ProtocolIE-FieldPair, Mode TYPE, TYPE SEQUENCE, Param   */
/*
SEQUENCE {
 id S1AP-PROTOCOL-IES-PAIR.&id ({IEsSetParam}),
 firstCriticality S1AP-PROTOCOL-IES-PAIR.&firstCriticality ({IEsSetParam}{@id}),
 firstValue S1AP-PROTOCOL-IES-PAIR.&FirstValue ({IEsSetParam}{@id}),
 secondCriticality S1AP-PROTOCOL-IES-PAIR.&secondCriticality ({IEsSetParam}{@id}),
 secondValue S1AP-PROTOCOL-IES-PAIR.&SecondValue ({IEsSetParam}{@id}) 
}
*/
type ProtocolIE_FieldPair struct {
	Asn
	Id  int `tableIdx:"true" range:"0..65535"`
	FirstCriticality  Criticality `type:"enum(Reject, Ignore, Notify)"`
	FirstValue  interface{} 
	SecondCriticality  Criticality `type:"enum(Reject, Ignore, Notify)"`
	SecondValue  interface{} 
}


/* S1AP-PDU, Mode TYPE, TYPE CHOICE, Param   */
/*
CHOICE {
 initiatingMessage InitiatingMessage,
 successfulOutcome SuccessfulOutcome,
 unsuccessfulOutcome UnsuccessfulOutcome,
 ... 
}
*/
type S1AP_PDU struct {
	AsnCHOICE
	InitiatingMessage  *InitiatingMessage 
	SuccessfulOutcome  *SuccessfulOutcome 
	UnsuccessfulOutcome  *UnsuccessfulOutcome 
	AsnEXTENSION
}

/* InitiatingMessage, Mode TYPE, TYPE SEQUENCE, Param   */
/*
SEQUENCE {
 procedureCode S1AP-ELEMENTARY-PROCEDURE.&procedureCode ({S1AP-ELEMENTARY-PROCEDURES}),
 criticality S1AP-ELEMENTARY-PROCEDURE.&criticality ({S1AP-ELEMENTARY-PROCEDURES}{@procedureCode}),
 value S1AP-ELEMENTARY-PROCEDURE.&InitiatingMessage ({S1AP-ELEMENTARY-PROCEDURES}{@procedureCode}) 
}
*/
type InitiatingMessage struct {
	Asn
	ProcedureCode   ProcedureCode `tableIdx:"true" range:"0..255" table:"InitiatingMessage/S1AP-ELEMENTARY-PROCEDURES.S1AP-PDU-Descriptions"`
	Criticality   Criticality `table:"InitiatingMessage/S1AP-ELEMENTARY-PROCEDURES.S1AP-PDU-Descriptions" type:"enum(Reject, Ignore, Notify)"`
	Value  interface{} `table:"InitiatingMessage/S1AP-ELEMENTARY-PROCEDURES.S1AP-PDU-Descriptions"`
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

