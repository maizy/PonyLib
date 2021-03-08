package u

func FormatNum(amount int, one string, many string) string {
	if amount == 1 {
		return one
	}
	return many
}
