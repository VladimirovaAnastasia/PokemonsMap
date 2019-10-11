from django.db import models


class Pokemon(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    photo = models.ImageField('Фото')
    description = models.CharField('Описание', max_length=600)
    title_en = models.CharField('Заголовок EN', max_length=200)
    title_jp = models.CharField('Заголовок JP', max_length=200)
    evolution_from = models.ForeignKey('self', verbose_name='Эволюционирует от', null=True, blank=True, related_name='child', on_delete=models.CASCADE)

    def __str__(self):
        if self.title:
            return self.title
        return f'{self.title} (empty)'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, verbose_name='Покемон', on_delete=models.CASCADE)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    appeared_at = models.DateTimeField('Появится', null=True, blank=True)
    disappeared_at = models.DateTimeField('Исчезнет', null=True, blank=True)
    level = models.IntegerField('Уровень', null=True, blank=True)
    health = models.IntegerField('Здоровье', null=True, blank=True)
    attack = models.IntegerField('Атака', null=True, blank=True)
    protection = models.IntegerField('Защита', null=True, blank=True)
    stamina = models.IntegerField('Выносливость', null=True, blank=True)

    def __str__(self):
        return self.pokemon.title

