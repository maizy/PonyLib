package targets

import (
	"fmt"
	"os"
	"sync"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/u"
)

func scanRegularFile(
	ctx fb2_scanner.ScannerContext, path string, resultChan chan<- fb2_scanner.ScannerResult, wg *sync.WaitGroup) {

	source := &fb2_scanner.FileSource{path}
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
	ctx.AquireFileSemaphore()
	go func() {
		fp, err := os.Open(path)
		defer func() {
			_ = fp.Close()
			ctx.ReleaseFileSemaphore()
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
	}()
}
