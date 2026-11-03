package fb2_scanner

import "github.com/gabriel-vasile/mimetype"

type SupportedArchive string

const (
	ZipArchive SupportedArchive = "zip"
)

func DetectSupportedArchive(path string) *SupportedArchive {
	if mime, err := mimetype.DetectFile(path); err == nil {
		switch mime.String() {
		case "application/zip":
			return new(ZipArchive)
		default:
			return nil
		}
	}
	return nil
}
