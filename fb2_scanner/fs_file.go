package fb2_scanner

import (
	"fmt"
	"sync"
)

type FileTarget struct {
	Path string
}

func (f *FileTarget) Spec() string {
	return fmt.Sprintf("file:%s", f.Path)
}

func (f *FileTarget) Type() TargetType {
	return FsFile
}

func (f *FileTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	resultChan := make(chan ScannerResult, 1)
	wg := sync.WaitGroup{}
	wg.Add(1)
	scanRegularFile(ctx, f.Path, resultChan, &wg)
	go func() {
		wg.Wait()
		close(resultChan)
	}()
	return resultChan
}
