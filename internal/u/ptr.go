package u

import "time"

func StrPtr(value string) *string {
	return &value
}

func IntPtr(value int) *int {
	return &value
}

func ErrPtr(error error) *error {
	return &error
}

func TimePtr(value time.Time) *time.Time {
	return &value
}
