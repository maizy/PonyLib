package pagination

import (
	"math"
)

type Pagination struct {
	NavigationPages []int
	PreviousPage    int
	NextPage        int
}

func CountSlidePagination(size int, currentPage int, perPage int, totalFound int) Pagination {
	var navigationPages []int = nil
	var nextPage int
	var previousPage int

	if totalFound > perPage {
		lastPage := int(math.Ceil(float64(totalFound) / float64(perPage)))
		var firstNavPage = 1
		var lastNavPage = lastPage
		// 1 2 3 [4] 5 6 7 8
		if lastPage >= size+1 {
			half := int(math.Ceil(float64(size-1) / 2))
			rightWing := half
			leftWing := size - 1 - rightWing

			// 2 3 4 5 6 7 [8] 9 10 11
			if currentPage+rightWing > lastPage {
				rightWing = lastPage - currentPage
				leftWing = size - 1 - rightWing
			}
			if currentPage < half {
				leftWing = currentPage - 1
				rightWing = size - 1 - leftWing
			}
			firstNavPage = max(currentPage-leftWing, 1)
			lastNavPage = min(currentPage+rightWing, lastNavPage)
		}
		for i := firstNavPage; i <= lastNavPage; i++ {
			navigationPages = append(navigationPages, i)
		}
		if currentPage < lastPage {
			nextPage = currentPage + 1
		}
		if currentPage > 1 && currentPage <= lastPage {
			previousPage = currentPage - 1
		}
	}

	return Pagination{navigationPages, previousPage, nextPage}
}
