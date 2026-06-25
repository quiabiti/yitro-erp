from django.db import models

class Instituicao(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # Ex: escola-nome-a
    logotipo = models.ImageField(upload_to='escolas/logos/')
    endereco = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome