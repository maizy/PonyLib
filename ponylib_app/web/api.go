package web

import (
	"net/http"

	"dev.maizy.ru/ponylib/ponylib_app"
	"github.com/gin-gonic/gin"
)

func BuildVersionHandler() func(c *gin.Context) {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"version": ponylib_app.GetVersion(),
		})
	}
}
