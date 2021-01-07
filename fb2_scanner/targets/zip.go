package targets

import (
	"errors"
	"fmt"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/u"
)

type ZipArchiveTarget struct {
	Path              string
	AllowedExtensions []string
}

func (z *ZipArchiveTarget) Spec() string {
	return fmt.Sprintf("zip:%s", z.Path)
}

func (z *ZipArchiveTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.ZipArchive
}

func (z *ZipArchiveTarget) Scan(ctx fb2_scanner.ScannerContext) <-chan fb2_scanner.ScannerResult {
	// FIXME: implements
	resultChan := make(chan fb2_scanner.ScannerResult)
	go func() {
		defer close(resultChan)
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.ZipArchiveFileSource{z.Path, "fake-file1.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: u.StrPtr("title1")}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 150_000_000, ParseTimeNs: 20_000_000},
		}

		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.ZipArchiveFileSource{z.Path, "subdir/fake-file2.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: u.StrPtr("title2")}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 10_000_000, ParseTimeNs: 300_000_000},
		}

		err := errors.New("test error")
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &fb2_scanner.ZipArchiveFileSource{z.Path, "fake-file3.fb2"},
			Metadata: nil,
			Error:    &err,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 15_000_000, ParseTimeNs: 0},
		}
	}()
	return resultChan
}
