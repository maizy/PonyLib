package fs

import (
	"errors"
	"fmt"
	"os"
	"sync"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_parser/metadata"
	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/u"
)

type FileSource struct {
	Path string
}

func (s *FileSource) Spec() string {
	return fmt.Sprintf("file[%s]", s.Path)
}

type FileTarget struct {
	Path string
}

func (f *FileTarget) Spec() string {
	return fmt.Sprintf("file[%s]", f.Path)
}

func (f *FileTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.FsFile
}

func (f *FileTarget) Scan(openFileSemaphore chan struct{}) <-chan fb2_scanner.ScannerResult {
	resultChan := make(chan fb2_scanner.ScannerResult)
	wg := sync.WaitGroup{}
	scanRegularFile(f.Path, resultChan, &wg, openFileSemaphore)
	go func() {
		wg.Wait()
		close(resultChan)
	}()
	return resultChan
}

type DirectoryTarget struct {
	Path string
}

func (f *DirectoryTarget) Spec() string {
	return fmt.Sprintf("dir[%s]", f.Path)
}

func (f *DirectoryTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.FsDir
}

func (f *DirectoryTarget) Scan(openFileSemaphore chan struct{}) <-chan fb2_scanner.ScannerResult {
	resultChan := make(chan fb2_scanner.ScannerResult)
	go func() {
		defer close(resultChan)
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &FileSource{f.Path + "/fake-file1.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: u.StrPtr("title1")}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 150_000_000, ParseTimeNs: 20_000_000},
		}

		resultChan <- fb2_scanner.ScannerResult{
			Source:   &FileSource{f.Path + "/subdir/fake-file2.fb2"},
			Metadata: &fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: u.StrPtr("title2")}},
			Error:    nil,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 10_000_000, ParseTimeNs: 300_000_000},
		}

		err := errors.New("test error")
		resultChan <- fb2_scanner.ScannerResult{
			Source:   &FileSource{f.Path + "/fake-file3.fb2"},
			Metadata: nil,
			Error:    &err,
			Timers:   fb2_scanner.ParseTimers{ExtractTimeNs: 15_000_000, ParseTimeNs: 0},
		}
	}()
	return resultChan
}

func scanRegularFile(
	path string, resultChan chan<- fb2_scanner.ScannerResult, wg *sync.WaitGroup, openFileSemaphore chan struct{}) {

	source := &FileSource{path}
	stat, err := os.Stat(path)
	wg.Add(1)
	if err != nil {
		resultChan <- fb2_scanner.ScannerResult{
			Source:   source,
			Metadata: nil,
			Error:    u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
		}
		wg.Done()
		return
	}
	if !stat.Mode().IsRegular() {
		resultChan <- fb2_scanner.ScannerResult{
			Source:   source,
			Metadata: nil,
			Error:    u.ErrPtr(fmt.Errorf("%s isn't a regular file", path)),
		}
		wg.Done()
		return
	}
	openFileSemaphore <- struct{}{}
	go func() {
		fp, err := os.Open(path)
		defer func() {
			_ = fp.Close()
		}()
		defer wg.Done()

		if err != nil {
			resultChan <- fb2_scanner.ScannerResult{
				Source:   source,
				Metadata: nil,
				Error:    u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
			}
			return
		}

		parseStart := time.Now()
		parseMetadata, err := metadata.ParseMetadata(fp)
		timers := fb2_scanner.ParseTimers{ParseTimeNs: time.Since(parseStart).Nanoseconds()}

		if err != nil {
			resultChan <- fb2_scanner.ScannerResult{
				Source:   source,
				Metadata: nil,
				Error:    u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
				Timers:   timers,
			}
			return
		}

		resultChan <- fb2_scanner.ScannerResult{
			Source:   source,
			Metadata: parseMetadata,
			Error:    nil,
			Timers:   timers,
		}
		<-openFileSemaphore
	}()
}
