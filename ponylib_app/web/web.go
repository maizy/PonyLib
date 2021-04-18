package web

import (
	"embed"
	"html/template"

	"github.com/gin-gonic/gin"

	"dev.maizy.ru/ponylib/ponylib_app"
)

func serverHeader(c *gin.Context) {
	c.Header("Server", "Ponylib/"+ponylib_app.GetVersion())
}

func SetupMiddlewares(engine *gin.Engine) {
	engine.Use(serverHeader)
}

//go:embed templates/*
var templates embed.FS

func SetupTemplates(engine *gin.Engine) {
	template := template.Must(template.New("").ParseFS(templates, "templates/*.tmpl"))
	engine.SetHTMLTemplate(template)
}
