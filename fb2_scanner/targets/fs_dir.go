package targets

import (
	"errors"
	"fmt"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner"
)

type DirectoryTarget struct {
	Path              string
	AllowedExtensions []string
}

func (f *DirectoryTarget) Spec() string {
	return fmt.Sprintf("dir:%s", f.Path)
}

func (f *DirectoryTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.FsDir
}

func (f *DirectoryTarget) Scan(ctx fb2_scanner.ScannerContext) <-chan fb2_scanner.ScannerResult {
	// FIXME: implements
	resultChan := make(chan fb2_scanner.ScannerResult)
	go func() {
		defer close(resultChan)
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.FileSource{f.Path + "/fake-file1.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: "title1"}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 150_000_000, ParseTimeNs: 20_000_000},
		}

		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.FileSource{f.Path + "/subdir/fake-file2.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: "title2"}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 10_000_000, ParseTimeNs: 300_000_000},
		}

		err := errors.New("test error")
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.FileSource{f.Path + "/fake-file3.fb2"},
			Metadata: nil,
			Error:    &err,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 15_000_000, ParseTimeNs: 0},
		}
	}()
	return resultChan
}
