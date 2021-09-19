package web

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"strings"
)

const passwordCookieName = "password"

func BasicUnsafeAuth(authUrl, staticPrefix string) gin.HandlerFunc {
	password := os.Getenv("PASSWORD")
	if password == "" {
		return func(c *gin.Context) {
			c.Next()
		}
	} else {
		return func(c *gin.Context) {
			if c.Request.URL.Path == authUrl {
				if c.Request.Method == "POST" {
					formPassword := c.PostForm("password")
					secured := c.Request.URL.Scheme == "https"
					if formPassword == password {
						c.SetCookie(passwordCookieName, password, 60*60*24*90, "/", c.Request.Host, secured, true)
						c.Redirect(http.StatusFound, "/")
						return
					} else {
						c.SetCookie(passwordCookieName, "", 0, "/", c.Request.Host, secured, true)
						c.Redirect(http.StatusFound, "/auth?wrong-password=true")
						return
					}
				}
				c.Next()
			} else if strings.HasPrefix(c.Request.URL.Path, staticPrefix) {
				c.Next()
			} else {
				passwordCookie, err := c.Cookie(passwordCookieName)
				if err == nil && passwordCookie == password {
					c.Next()
				} else {
					c.Redirect(http.StatusFound, "/auth")
					return
				}
			}
		}
	}
}
