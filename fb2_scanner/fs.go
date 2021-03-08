package fb2_scanner

import (
	"fmt"
	"os"
	"sync"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
	"dev.maizy.ru/ponylib/internal/u"
)

func scanRegularFile(
	ctx ScannerContext, path string, resultChan chan<- ScannerResult, done *sync.WaitGroup, target ScanTarget) {

	source := &FileSource{path}
	stat, err := os.Stat(path)
	if err != nil {
		resultChan <- ScannerResult{
			Source:     source,
			Metadata:   nil,
			Error:      u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
			FromTarget: target,
		}
		done.Done()
		return
	}
	if !stat.Mode().IsRegular() {
		resultChan <- ScannerResult{
			Source:     source,
			Metadata:   nil,
			Error:      u.ErrPtr(fmt.Errorf("%s isn't a regular file", path)),
			FromTarget: target,
		}
		done.Done()
		return
	}
	ctx.AcquireFileSemaphore()
	go func() {
		fp, err := os.Open(path)
		defer func() {
			_ = fp.Close()
			ctx.ReleaseFileSemaphore()
			done.Done()
		}()

		if err != nil {
			resultChan <- ScannerResult{
				Source:     source,
				Metadata:   nil,
				Error:      u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
				FromTarget: target,
			}
			return
		}

		parseStart := time.Now()
		parseMetadata, err := metadata.ParseMetadata(fp)
		timers := ParseTimers{ParseTimeNs: time.Since(parseStart).Nanoseconds()}

		if err != nil {
			resultChan <- ScannerResult{
				Source:     source,
				Metadata:   nil,
				Error:      u.ErrPtr(fmt.Errorf("unable to open %s: %w", path, err)),
				Timers:     timers,
				FromTarget: target,
			}
			return
		}

		resultChan <- ScannerResult{
			Source:     source,
			Metadata:   parseMetadata,
			Error:      nil,
			Timers:     timers,
			FromTarget: target,
		}
	}()
}
