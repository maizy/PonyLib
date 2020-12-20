package u

func StrPtr(value string) *string {
	return &value
}

func IntPtr(value int) *int {
	return &value
}

func ErrPtr(error error) *error {
	return &error
}
