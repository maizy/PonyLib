package web

import (
	"dev.maizy.ru/ponylib/ponylib_app"
	"github.com/gin-gonic/gin"
)

func WithCommonVars(c *gin.Context, vars gin.H) gin.H {
	result := gin.H{
		"lang":    "en",
		"version": ponylib_app.GetVersion(),
	}

	for key, value := range vars {
		result[key] = value
	}
	return result
}
