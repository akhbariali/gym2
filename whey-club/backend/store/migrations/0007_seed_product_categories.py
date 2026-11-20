from django.db import migrations

def seed(apps,schema_editor):
    Category=apps.get_model('store','Category');Route=apps.get_model('store','CategoryRoute');Product=apps.get_model('store','Product')
    whey=Category.objects.create(name='پروتئین وی',slug='whey-protein',position=0)
    for index,(slug,name) in enumerate([('isolate','وی ایزوله'),('concentrate','وی کنسانتره'),('blend','وی ترکیبی')]):
        category=Category.objects.create(name=name,slug=slug,parent=whey,position=index)
        Route.objects.create(category=category,path='/shop/whey-protein/'+slug+'/')
        Product.objects.filter(protein_type=slug,category_node__isnull=True).update(category_node=category)
    Route.objects.create(category=whey,path='/shop/whey-protein/')
    for index,(slug,name,kind) in enumerate([('creatine','کراتین','creatine'),('accessories','لوازم جانبی','shaker')],1):
        category=Category.objects.create(name=name,slug=slug,position=index)
        Route.objects.create(category=category,path='/shop/'+slug+'/')
        Product.objects.filter(protein_type=kind,category_node__isnull=True).update(category_node=category)

class Migration(migrations.Migration):
    dependencies=[('store','0006_category_product_category_node_categoryroute')]
    operations=[migrations.RunPython(seed,migrations.RunPython.noop)]
