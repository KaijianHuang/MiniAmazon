from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.exceptions import ObjectDoesNotExist

def create_user(name,uEmail,pw):
    from django.contrib.auth.models import User 
    try:
        User.objects.get(username=name)
    except ObjectDoesNotExist:
        user = User.objects.create(
            username=name,
            email=uEmail,
            is_superuser=False
        )
        user.set_password(pw)
        user.save()

def create_category(names):
    from users.models import Category
    if Category.objects.all().count()==0:
        for name in names:
            Category.objects.create(category=name)

def create_product(descriptions,categories,prices):
    from users.models import Product,Category
    assert len(descriptions)==len(prices) and len(descriptions)==len(categories)
    length = len(descriptions)
    if Product.objects.all().count()==0:
        for i in range(length):
            cat = Category.objects.get(category=categories[i])
            Product.objects.create(description=descriptions[i],
                category = cat,
                price = prices[i]
            )

def create_warehouse(xs,ys):
    from users.models import Warehouse
    assert len(xs)==len(ys)
    if Warehouse.objects.all().count()==0:
        for i in range(len(xs)):
            Warehouse.objects.create(address_x=xs[i],address_y=ys[i])

def init_database(sender, **kwargs):
    create_user("admin","kh492@duke.edu","adminadmin123")
    create_user("test1","test1@duke.edu","testtest123")
    create_user("test2","test2@duke.edu","testtest123")
    create_category(["electronics","foods","games"])
    create_product(["macbookpro","biscuit","LastOfUs"],["electronics","foods","games"],[2499,1.99,30])
    create_warehouse([1,2,3,4,5,6,7,8,9,10],[1,2,3,4,5,6,7,8,9,10])

class UsersConfig(AppConfig):
    name = 'users'
    def ready(self):
        post_migrate.connect(init_database, sender=self)