package fb2_scanner

import (
	"runtime"
)

type ScannerContext struct {
	openFileSemaphore chan struct{}
}

func (c *ScannerContext) AcquireFileSemaphore() {
	c.openFileSemaphore <- struct{}{}
}

func (c *ScannerContext) ReleaseFileSemaphore() {
	<-c.openFileSemaphore
}

func NewScannerContext() ScannerContext {
	return ScannerContext{make(chan struct{}, max(runtime.NumCPU(), 4))}
}
