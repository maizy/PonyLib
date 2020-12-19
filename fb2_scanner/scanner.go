package fb2_scanner

import (
	"sync"
)

type Fb2Scanner struct {
	Results       <-chan ScannerResult
	resultChannel chan<- ScannerResult
	wg            sync.WaitGroup
}

func NewFb2Scanner() Fb2Scanner {
	channel := make(chan ScannerResult)
	return Fb2Scanner{channel, channel, sync.WaitGroup{}}
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
	Scan() <-chan ScannerResult
}

func (s *Fb2Scanner) Scan(target ScanTarget) {
	resultsChannel := target.Scan()
	s.wg.Add(1)
	go func() {
		defer s.wg.Done()
		for res := range resultsChannel {
			s.resultChannel <- res
		}
	}()
}

func (s *Fb2Scanner) Wait() {
	s.wg.Wait()
	close(s.resultChannel)
}
