package fb2_scanner

import (
	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
)

type ScannerSource interface {
	RId() resource.RId
}

type ParseTimers struct {
	ExtractTimeNs int64
	ParseTimeNs   int64
}

func (t *ParseTimers) Add(other *ParseTimers) {
	if other != nil {
		t.ExtractTimeNs += other.ExtractTimeNs
		t.ParseTimeNs += other.ParseTimeNs
	}
}

type ScannerResult struct {
	Source   ScannerSource
	Metadata *fb2_parser.Fb2Metadata
	Error    *error
	Timers   ParseTimers
}

func (r *ScannerResult) IsSuccess() bool {
	return r.Error == nil && r.Metadata != nil
}
