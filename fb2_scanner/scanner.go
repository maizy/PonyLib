package fb2_scanner

import (
	"runtime"
	"sync"

	"dev.maizy.ru/ponylib/internal/u"
)

type Fb2Scanner struct {
	Results           <-chan ScannerResult
	resultChannel     chan<- ScannerResult
	wg                sync.WaitGroup
	openFileSemaphore chan struct{}
}

func NewFb2Scanner() Fb2Scanner {
	channel := make(chan ScannerResult)
	return Fb2Scanner{channel, channel, sync.WaitGroup{}, make(chan struct{}, u.IntMax(runtime.NumCPU(), 4))}
}

type TargetType string

const (
	FsDir  TargetType = "Directory"
	FsFile            = "File"
	//ZipArchive = "Zip Archive"
	//GzFile = "Gzip File"
)

type ScanTarget interface {
	Type() TargetType
	Spec() string
	Scan(openFileSemaphore chan struct{}) <-chan ScannerResult
}

func (s *Fb2Scanner) Scan(target ScanTarget) {
	resultsChannel := target.Scan(s.openFileSemaphore)
	s.wg.Add(1)
	go func() {
		for res := range resultsChannel {
			s.resultChannel <- res
		}
		s.wg.Done()
	}()
}

func (s *Fb2Scanner) Wait() {
	s.wg.Wait()
	close(s.resultChannel)
}
