from django.db import models

# NOTE: Para poder utilizar el modelo "user" que viene por defecto en Django,
# Debemos importarlo previamente:

from django.contrib.auth.models import User
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields import BigAutoField, CharField

# Create your models here.


class Comic(models.Model):
    '''
    Esta clase hereda de Django models.Model y crea una tabla llamada
    e_commerce_comic. Las columnas toman el nombre especificado de cada objeto.
    '''
    id = models.BigAutoField(db_column='ID', primary_key=True)
    marvel_id = models.PositiveIntegerField(
        verbose_name='marvel ids', default=1, unique=True)
    title = models.CharField(
        verbose_name='titles', max_length=120, default='')
    description = models.TextField(
        verbose_name='descriptions', default='')
    price = models.FloatField(
        verbose_name='prices', max_length=5, default=0.00)
    stock_qty = models.PositiveIntegerField(
        verbose_name='stock qty', default=0)
    picture = models.URLField(
        verbose_name='pictures', default='')

    class Meta:
        '''
        Con "class Meta" podemos definir atributos de nuestras entidades como el nombre de la tabla.
        '''
        db_table = 'e_commerce_comics'

    def __str__(self):
        '''
        La función __str__ cumple la misma función que __repr__ en SQL Alchemy, 
        es lo que retorna cuando llamamos al objeto.
        '''
        return f'{self.id}'


class WishList(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    user_id = models.ForeignKey(User,
                                verbose_name='User',
                                on_delete=models.DO_NOTHING,
                                default=1, blank=True
                                )
    comic_id = models.ForeignKey(Comic,
                                 verbose_name='Comic',
                                 on_delete=models.DO_NOTHING,
                                 default=1, blank=True
                                 )
    favorite = models.BooleanField(
        verbose_name='Favorite', default=False)
    cart = models.BooleanField(
        verbose_name='carts', default=False)
    wished_qty = models.PositiveIntegerField(
        verbose_name='wished qty', default=0)
    buied_qty = models.PositiveIntegerField(
        verbose_name='buied qty', default=0)

    class Meta:
        db_table = 'e_commerce_wish_list'

    def __str__(self):
        return f'{self.id}'


class UserDetail(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    user = models.ForeignKey(User, verbose_name='User', on_delete=DO_NOTHING, default=1, blank=True)
    country = models.CharField(verbose_name='Country', max_length=100, default='')
    state = models.CharField(verbose_name='Province/State', max_length=100, default='')
    city = models.CharField(verbose_name='City', max_length=100, default='')
    postal_code = models.CharField(verbose_name='Postal Code', max_length=15, default='0000')
    cell_phone_number = models.CharField(verbose_name='Cell Phone Number', max_length=20, default='00-0000-0000')

    class Meta:
        db_table = 'e_commerce_user_detail'

    def __str__(self):
        return f'{self.id}'



