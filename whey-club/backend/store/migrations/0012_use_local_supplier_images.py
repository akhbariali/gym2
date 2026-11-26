from django.db import migrations

IMAGES = {'fa-ice-creatine-300g': 'https://fasklep.pl/3471-large_default/ice-creatine-300-g.jpg', 'zoomad-one-raw-creatine-strawberry-300g': 'https://en.vitamin360.com/img/42678/2350097000/ZOOMAD-LABS-RAW-ONE-CREATINE-ULTRA-PURE-200-MESH-300g-Strawberry_SUPP.jpg?time=1762333680', 'trufuel-creatine-monohydrate-300g': 'https://mytruefuel.com/wp-content/uploads/2026/01/01.png', 'cellucor-cor-performance-creatine-300g': 'https://images.tcdn.com.br/img/img_prod/738187/creatina_monohidratada_300g_cellucor_3967_1_4d98501844dc1eefc60ea18ea99829c2.jpg', 'weider-pure-creatine-250g': 'https://www.weider.de/cdn/shop/files/WEIDER_31722_PURE_CREATINE_250g_VS.webp?v=1773831260&width=1250', 'nutrend-creatine-monohydrate-300g': 'https://nutrendcdn.com/cdn-cgi/imagedelivery/v_g237akqysjqDvfyOsFkg/73209798-3e3d-48fb-3b07-79680f1ae400/public', 'allmax-creatine-monohydrate-400g': 'https://www.allmaxnutrition.com/cdn/shop/files/allmax-creatine-unflavored-400g_1.webp?v=1782153992&width=1080', 'muscletech-platinum-creatine-450g': 'https://www.med7online.com/cdn/shop/files/MuscleTech_Platinum_Creatine_Monohydrate_450G_Unflavored_Serv_90.webp?v=1792748273&width=1500'}

def use_local_images(apps,schema_editor):
    Product=apps.get_model('store','Product')
    for slug,original in IMAGES.items():
        Product.objects.filter(slug=slug,image_url=original).update(image_url='https://wheyclub.ir/assets/products/'+slug+'.jpg')

class Migration(migrations.Migration):
    dependencies=[('store','0011_archive_demo_products')]
    operations=[migrations.RunPython(use_local_images,migrations.RunPython.noop)]
