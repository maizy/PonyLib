package u

import "math"

func TotalMs(totalNs int64) int64 {
	return totalNs / int64(math.Pow(10, 6))
}

func TotalSec(totalNs int64) float64 {
	return float64(totalNs) / math.Pow(10, 9)
}

func AvgMs(totalNs int64, items int) int64 {
	return int64(float64(totalNs) / float64(items) / math.Pow(10, 6))
}
