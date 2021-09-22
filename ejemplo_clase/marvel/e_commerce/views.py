
# Importamos vistas genericas:
from django.views.generic import TemplateView, ListView

# Importamos los modelos que vamos a usar:
from django.contrib.auth.models import User
from e_commerce.models import *


# Formulario de registro:
from django import forms
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm

# Utilidades:
from marvel.settings import VERDE, AMARILLO
from datetime import datetime

# NOTE: Páginas del sitio **********************************************************

class BaseView(TemplateView):
    '''
    Template base que vamos a extender para el resto de las páginas del sitio.
    '''
    template_name = 'e-commerce/base.html'


class LoginUserView(TemplateView):
    '''
    Formulario de inicio de sesión.
    '''
    template_name = 'e-commerce/login.html'

class UserForm(UserCreationForm):
    '''
    Formulario de creación de usuario.
    Utilizamos un formulario que viene por defecto en Django y que cumple con todos los
    requisitos para agregar un nuevo usuario a la base de datos.
    También tiene los métodos para validar todos sus campos.
    '''
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'password1', 'password2')


def register(request):
    '''
    Función que complementa el formulario de registro de usuario.
    Al completar el formulario, se envía la información a esta función que espera
    una petición de tipo `POST`, si la información enviada no es valida o la petición no es POST, 
    se redirige nuevamente a la página de registro. Si el registro fue exitoso,
    el usuario será redirigido a la página de logueo.
    '''
    if request.method == 'POST':
        # Si la petición es de tipo POST, analizamos los datos del formulario:
        # Creamos un objeto de tipo UserForm (la clase que creamos mas arriba)
        # Pasandole los datos del request:
        form = UserForm(request.POST)
        # Luego, utilizamos el método que viene en en la clase UserCreationForm
        # para validar los datos del formulario: 
        [print(VERDE+'',item) for item in form] # NOTE: Imprimimos para ver el contenido del formulario COMPLETO
        if form.is_valid():
            # Si los datos son validos, el formulario guarda los datos en la base de datos.
            # Al heredar de UserCreationForm, aplica las codificaciónes en el password y todo
            # lo necesario:
            form.save()
            # Con todo terminado, redirigimos a la página de inicio de sesión,
            # porque por defecto, registrar un usuario no es iniciar una sesión.
            return redirect('/e-commerce/login')
    else:
        # Si el método no es de tipo POST, se crea un objeto de tipo formulario
        # Y luego se envía al contexto de renderización. 
        form = UserForm()
    # Si los datos del POST son invalidos o si el método es distinto a POST
    # retornamos el render de la página de registro, con el formulario de registro en el contexto.
    [print(AMARILLO+'',item) for item in form] # NOTE: Imprimimos para ver el contenido del formulario vacío
    return render(request, 'e-commerce/signup.html', {'form': form})

class IndexView(ListView):
    '''
    Página principal del sitio.
    Utilizamos `ListView` para poder aprovechar sus funciones de paginado.
    Para ello tenemos que utilizar sus atributos:
    \n
    '''
    queryset = Comic.objects.all().order_by('-id')
    # NOTE: Este queryset incorporará una lista de elementos a la que le asignará
    # Automáticamente el nombre de comic_list
    template_name = 'e-commerce/index.html'
    paginate_by = 10

    # NOTE: Examinamos qué incluye nuestro contexto:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        [print(AMARILLO+f'{element}\n') for element in context.items()]
        return context


class DetailsView(TemplateView):
    template_name = 'e-commerce/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            comic_obj = Comic.objects.get(
                marvel_id=self.request.GET.get('marvel_id'))
            context["comic"] = comic_obj
            context['comic_picture_full'] = str(
                comic_obj.picture).replace('/standard_xlarge', '')
            context['comic_desc'] = str(
                comic_obj.description).replace('<br>', '\n')
            username = self.request.user
            if username != None:
                user_obj = User.objects.filter(username=username)
                if user_obj.first() != None:
                    wish_obj = WishList.objects.filter(
                        user_id=user_obj[0].id, comic_id=comic_obj)
                    if wish_obj.first() != None:
                        context["favorite"] = wish_obj.first().favorite
                        context["cart"] = wish_obj.first().cart
                        context["wished_qty"] = wish_obj.first().wished_qty
                    else:
                        context["favorite"] = False
                        context["cart"] = False
                        context["wished_qty"] = 0
        except:
            return context
        return context


def check_button(request):
    '''
    Esta función tiene como objetivo el cambio de estado de los botones de favoritos y carrito.
    '''
    if request.method == 'POST':
        print(request.path)
        # NOTE: Obtenemos los datos necesarios:
        username = request.POST.get('username')
        marvel_id = request.POST.get('marvel_id')
        user_authenticated = request.POST.get('user_authenticated')
        type_button = request.POST.get('type_button')
        actual_value = request.POST.get('actual_value')
        path = request.POST.get('path')

        # Validamos los datos y les damos formato:
        username = username if username != '' else None
        marvel_id = marvel_id if marvel_id != '' else None
        user_authenticated = True if user_authenticated == 'True' else False
        type_button = type_button if type_button != '' else None
        actual_value = True if actual_value == 'True' else False
        path = path if path != None else 'index'

        if user_authenticated and username != None:
            # Si el usuario está autenticado, traemos su "wishlist"
            
            user_obj = User.objects.get(username=username)
            comic_obj = Comic.objects.get(marvel_id=marvel_id)
            wish_obj = WishList.objects.filter(
                user_id=user_obj, comic_id=comic_obj).first()
            if not wish_obj:
                # Si no tiene "wishlist" creamos una
                wish_obj = WishList.objects.create(
                    user_id=user_obj, comic_id=comic_obj)

            # Remplazamos el estado del botón seleccionado:
            if type_button == "cart":
                wish_obj.cart = not actual_value

                # Si saco el comic del carrito de compras se pone
                # a 0 la cantidad de unidades del respectivo comic.
                if wish_obj.cart is False:
                    wish_obj.wished_qty = 0
                
                wish_obj.save()
                print('wish_obj.cart :', wish_obj.cart)
            elif type_button == "favorite":
                wish_obj.favorite = not actual_value
                print('wish_obj.favorite :', wish_obj.favorite)
                wish_obj.save()
            else:
                pass
            # Componemos los endpoints segun la página:
            if 'detail' in path:
                path += f'?marvel_id={marvel_id}'
            
            # Una vez terminada la modificación, volvemos a la misma página.
            return redirect(path)
        else:
            # Si el usuario no está autenticado, lo redirigimos a la página de logueo.
            return redirect('login')
    else:
        # Si por error quisieron acceder al recurso con otro método que no sea POST, lo redirigimos al index
        return redirect('index')


class CartView(TemplateView):
    '''
    Vista de carrito de compras.
    Aquí se listará el total de elementos del carrito del usuario, 
    luego en el template se colocará un formulario en cada elemento del carrito
    para darlo de baja, y un boton general para concretar el pedido.
    '''
    template_name = 'e-commerce/cart.html'

    def get_context_data(self, **kwargs):
        '''
        En el contexto, devolvemos la lista total de elementos en el carrito de compras, 
        y el precio total calculado para la compra.
        '''
        context = super().get_context_data(**kwargs)
        username = self.request.user
        user_obj = User.objects.get(username=username)
        wish_obj = WishList.objects.filter(user_id=user_obj, cart=True)
        #cart_items = [obj.comic_id for obj in wish_obj]
        #context['cart_items'] = cart_items
        #context['total_price'] = round((sum([float(comic.price) for comic in cart_items])), 2)
        #print(context['cart_items'])

        # Creo una lista que contiene los id de los comics que están
        # en la wish_list del usuario.
        ids = [id[0] for id in wish_obj.values_list('comic_id')]
        
        # Creo una lista ordenada por el 'id' del comic 
        # donde cada elemento es un diccionario con las propiedades de cada comic.
        d_comics = Comic.objects.filter(id__in=ids).order_by('id').values()

        # Creo una lista ordenada por el id del comic 
        # con la cantidad de unidades de cada comic que el usuario piensa comprar.
        # El ordenamiento se hace para que cada elemento de cada lista coincidan.
        list_wished_qty = [qty[0] for qty in wish_obj.order_by('comic_id').values_list('wished_qty')]

        context['total_price'] = 0.00

        # Almaceno en el diccionario de comics la key wished_qty de lista creada.
        # Calculo el precio total de la compra.
        for (d, qty) in zip(d_comics, list_wished_qty):
            d['wished_qty_act'] = qty
            d['wished_qty_restant'] = d['stock_qty'] - qty

            if qty != 0:
                context['total_price']+= float(d['price']) * qty              

        context['total_price'] = round(context['total_price'], 2)
        context['cart_items'] = d_comics
        return context

def update_qty_wish (request):
    if request.method == 'POST':
        comic_id = request.POST.get('comic_id')
        qty = int(request.POST.get('quantity'))
        
        # Creo un objeto del tipo "comic" para obtener el stock
        # actual de dicho comic.
        comic_obj = Comic.objects.get(id=comic_id)
        stock_act = comic_obj.stock_qty

        # Si por alguna razón la cantidad a comprar supera
        # el stock actual, la cantidad se pone a 0.
        if qty > stock_act:
            qty = 0

        # Obtengo la cant. de unidades de ese comic que hay en el
        # carrito actualmente, y, a ese valor le sumo la cantidad
        # que el usuario agregó.
        wish_obj = WishList.objects.filter(comic_id=comic_id)
        wished_act = wish_obj.first().wished_qty
        aux = wished_act + qty

        # En caso de que la cantidad de comics que el
        # usuario desea comprar supere al stock actual
        # el wish_act no se modifica.
        if aux <= stock_act:
            wished_act = aux

        # Actualizo la cantidad de wished_qty.
        wish_obj.update(wished_qty=wished_act)

    return redirect('cart')


class WishView(TemplateView):
    '''
    En esta vista vamos a traer todos los comics favoritos de un usuario en particular.
    Luego en el Template vamos a colocar un formulario por cada favorito, 
    para eliminarlo de la lista de favoritos.
    '''
    template_name = 'e-commerce/wish.html'

    def get_context_data(self, **kwargs):
        '''
        Preparamos en nuestro contexto la lista de comics del usuario registrado.
        '''
        context = super().get_context_data(**kwargs)
        username = self.request.user
        user_obj = User.objects.get(username=username)
        wish_obj = WishList.objects.filter(user_id=user_obj, favorite=True)
        cart_items = [obj.comic_id for obj in wish_obj]
        context['fav_items'] = cart_items
        print(context['fav_items'])
        return context


class ThanksView(TemplateView):
    '''
    Página de agradecimiento. Esta es la página de respuesta una vez realizado el pedido.
    El Template tiene que tener un botón de redireccionamiento al index.
    '''
    template_name = 'e-commerce/thanks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtengo una lista con los comics que el usuario compró.
        user_obj = User.objects.get(username=self.request.user)
        wish_list = WishList.objects.filter(user_id=user_obj, cart=True, wished_qty__gt=0)
        comics = [obj.comic_id for obj in wish_list]

        context['comics'] = comics

        # Si hay contenido en la wish_list muestro
        # la fecha y hora de la compra de los comics.
        if wish_list:
            now = datetime.now()
            context['date'] = now.strftime('%Y-%m-%d')
            context['time'] = now.strftime('%H:%M:%S')


        # Una vez realizada la compra el estado de "cart" vuelve a ser False y la
        # cantidad de stock disponible se resta de la cantidad de unidades de cada
        # comic compradas.
        for (comic, wish_obj) in zip(comics, wish_list):
            comic.stock_qty = comic.stock_qty - wish_obj.wished_qty
            comic.save()
            wish_obj.buied_qty += wish_obj.wished_qty
            wish_obj.wished_qty = 0
            wish_obj.cart = False
            wish_obj.save()

        print(comics)
        print(context['comics'])

        return context


class UpdateUserView(TemplateView):
    '''
    Esta vista tiene como objetivo, proporcionar un formulario de actualización de los campos de usuario.
    '''
    template_name = 'e-commerce/update-user.html'

    def get_context_data(self, **kwargs):
        # TODO: Realizar la lógica de actualización de los datos de usuario.
        context =  super().get_context_data(**kwargs)

        user_obj = UserDetail.objects.filter(user_id=self.request.user.pk)
        data_user = user_obj.values().first()
        
        data_user['name'] = self.request.user.first_name
        data_user['surname'] = self.request.user.last_name
        data_user['username'] = self.request.user.username
        data_user['email'] = self.request.user.email
        
        context['data_user'] = data_user
        return context


def update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        country = request.POST.get('country') 
        state = request.POST.get('state')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        cell_phone_number = request.POST.get('cell_phone_number')

        # Actualizo los campos del modelo User
        user_obj = User.objects.filter(id=request.user.pk)
        user_obj.update(first_name=name, last_name=surname, 
                            username=username, email=email)

        # Actualizo los compos del modelo UserDetail
        userdetail_obj = UserDetail.objects.filter(user_id=request.user.pk)
        userdetail_obj.update(country=country, state=state, 
                                city=city, postal_code=postal_code, 
                                cell_phone_number=cell_phone_number)
    
    return redirect('/e-commerce/user')


class UserView(TemplateView):
    '''Vista con el detalle de los datos personales del usuario'''

    template_name = 'e-commerce/user.html'

    def get_context_data(self, **kwargs):
        # TODO: Realizar la lógica que lista los datos del usuario, 
        # incluyendo los datos de la tabla de datos adicionales de usuario.
        context = super().get_context_data(**kwargs)

        # Creo una lista de tuplas con keys y values.
        list_user=[('name', self.request.user.first_name),
            ('surname', self.request.user.last_name),
            ('username', self.request.user.username),
            ('email', self.request.user.email)
            ]

        # Obtengo una queryset con las 'keys' declaradas en el método "values".
        user_detail_obj = UserDetail.objects.filter(user_id=self.request.user.pk).values('country', 'state', 
                                                    'city', 'postal_code', 'cell_phone_number')

        # Obtengo el 1er elemento de la queryset y la itero ya que es un diccionario.
        # Le concateno una tupla a list_user
        for (k, v) in user_detail_obj.first().items():
            list_user.append((k, v))

        context['user_detail'] = list_user      # Le cargo en el contexto la lista "list_user".

        return context



# NOTE: Vistas con Bootstrap:

class BootstrapLoginUserView(TemplateView):
    '''
    Vista para Template de login con estilo de bootstrap.
    '''
    template_name = 'e-commerce/bootstrap-login.html'

class BootstrapSignupView(TemplateView):
    '''
    Vista para Template de registro de usuario con estilo de bootstrap.
    '''
    template_name = 'e-commerce/bootstrap-signup.html'