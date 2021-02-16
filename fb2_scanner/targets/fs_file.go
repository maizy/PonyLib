package targets

import (
	"fmt"
	"sync"

	"dev.maizy.ru/ponylib/fb2_scanner"
)

type FileTarget struct {
	Path string
}

func (f *FileTarget) Spec() string {
	return fmt.Sprintf("file:%s", f.Path)
}

func (f *FileTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.FsFile
}

func (f *FileTarget) Scan(ctx fb2_scanner.ScannerContext) <-chan fb2_scanner.ScannerResult {
	resultChan := make(chan fb2_scanner.ScannerResult)
	wg := sync.WaitGroup{}
	scanRegularFile(ctx, f.Path, resultChan, &wg)
	go func() {
		wg.Wait()
		close(resultChan)
	}()
	return resultChan
}
