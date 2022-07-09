from django.db import models

class Code_ASM(models.Model):
	code = models.CharField("code", max_length=1500)
	line_count = models.IntegerField("lines")

class Code_BIN(models.Model):
	asm = models.ForeignKey(Code_ASM, on_delete=models.CASCADE)
	code = models.CharField("code", max_length=1500)
