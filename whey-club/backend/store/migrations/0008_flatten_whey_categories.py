from django.db import migrations


def flatten(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Product = apps.get_model('store', 'Product')
    Route = apps.get_model('store', 'CategoryRoute')
    whey = Category.objects.filter(slug='whey-protein', parent__isnull=True).first()
    if not whey:
        return
    descendants = set()
    parents = {whey.pk}
    while parents:
        children = set(Category.objects.filter(parent_id__in=parents).values_list('pk', flat=True))
        descendants.update(children)
        parents = children
    Product.objects.filter(category_node_id__in=descendants).update(category_node_id=whey.pk)
    Route.objects.filter(category_id__in=descendants).update(category_id=whey.pk)
    while descendants:
        leaves = descendants - set(Category.objects.filter(pk__in=descendants).values_list('parent_id', flat=True))
        Category.objects.filter(pk__in=leaves).delete()
        descendants -= leaves


class Migration(migrations.Migration):
    dependencies = [('store', '0007_seed_product_categories')]
    operations = [migrations.RunPython(flatten, migrations.RunPython.noop)]
