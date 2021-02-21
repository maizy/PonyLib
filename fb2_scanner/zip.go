package fb2_scanner

import (
	"errors"
	"fmt"

	"dev.maizy.ru/ponylib/fb2_parser"
)

type ZipArchiveTarget struct {
	Path              string
	AllowedExtensions []string
}

func (z *ZipArchiveTarget) Spec() string {
	return fmt.Sprintf("zip:%s", z.Path)
}

func (z *ZipArchiveTarget) Type() TargetType {
	return ZipArchive
}

func (z *ZipArchiveTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	// FIXME: implements
	resultChan := make(chan ScannerResult)
	go func() {
		defer close(resultChan)
		resultChan <- ScannerResult{
			Source:   &ZipArchiveFileSource{z.Path, "fake-file1.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: "title1"}},
			Error:    nil,
			Timers:   ParseTimers{ExtractTimeNs: 150_000_000, ParseTimeNs: 20_000_000},
		}

		resultChan <- ScannerResult{
			Source:   &ZipArchiveFileSource{z.Path, "subdir/fake-file2.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: "title2"}},
			Error:    nil,
			Timers:   ParseTimers{ExtractTimeNs: 10_000_000, ParseTimeNs: 300_000_000},
		}

		err := errors.New("test error")
		resultChan <- ScannerResult{
			Source:   &ZipArchiveFileSource{z.Path, "fake-file3.fb2"},
			Metadata: nil,
			Error:    &err,
			Timers:   ParseTimers{ExtractTimeNs: 15_000_000, ParseTimeNs: 0},
		}
	}()
	return resultChan
}
