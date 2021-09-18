package pagination

import (
	"reflect"
	"testing"
)

func TestCountSlidePagination(t *testing.T) {
	type args struct {
		size        int
		currentPage int
		perPage     int
		totalFound  int
	}
	tests := []struct {
		name string
		args args
		want Pagination
	}{
		{
			"one page",
			args{size: 10, currentPage: 1, perPage: 40, totalFound: 12},
			Pagination{nil, 0, 0},
		},
		{
			"two pages at the first page",
			args{size: 10, currentPage: 1, perPage: 40, totalFound: 45},
			Pagination{[]int{1, 2}, 0, 2},
		},
		{
			"two pages at the second page",
			args{size: 10, currentPage: 2, perPage: 40, totalFound: 45},
			Pagination{[]int{1, 2}, 1, 0},
		},
		{
			"100 pages at the first page",
			args{size: 10, currentPage: 1, perPage: 40, totalFound: 4000},
			Pagination{[]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 0, 2},
		},
		{
			"100 pages at the 25 page",
			args{size: 10, currentPage: 25, perPage: 40, totalFound: 4000},
			Pagination{[]int{21, 22, 23, 24, 25, 26, 27, 28, 29, 30}, 24, 26},
		},
		{
			"100 pages at the 98 page",
			args{size: 10, currentPage: 98, perPage: 40, totalFound: 4000},
			Pagination{[]int{91, 92, 93, 94, 95, 96, 97, 98, 99, 100}, 97, 99},
		},
		{
			"100 pages at the last page",
			args{size: 10, currentPage: 100, perPage: 40, totalFound: 4000},
			Pagination{[]int{91, 92, 93, 94, 95, 96, 97, 98, 99, 100}, 99, 0},
		},
		{
			"8 pages at the 5 page",
			args{size: 10, currentPage: 5, perPage: 40, totalFound: 310},
			Pagination{[]int{1, 2, 3, 4, 5, 6, 7, 8}, 4, 6},
		},

		{
			"out of range current page",
			args{size: 10, currentPage: 100500, perPage: 40, totalFound: 310},
			Pagination{[]int{1, 2, 3, 4, 5, 6, 7, 8}, 0, 0},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var got = CountSlidePagination(tt.args.size, tt.args.currentPage, tt.args.perPage, tt.args.totalFound)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("CountSlidePagination() = %v, want %v", got, tt.want)
			}
		})
	}
}
