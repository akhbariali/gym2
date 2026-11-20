"""A category's URL always follows its current ancestors; old URLs remain redirects."""
from django.db import models, transaction
from django.core.exceptions import ValidationError

class Category(models.Model):
    name=models.CharField('نام دسته',max_length=120)
    slug=models.SlugField('بخش انگلیسی نشانی',max_length=80)
    parent=models.ForeignKey('self',on_delete=models.PROTECT,null=True,blank=True,related_name='children',verbose_name='دسته بالادست')
    position=models.PositiveIntegerField('ترتیب نمایش',default=0)
    class Meta:
        app_label='store'
        ordering=['position','id']
        verbose_name='دسته محصول'
        verbose_name_plural='دسته‌های محصولات'
    def __str__(self):return self.name
    def ancestors(self):
        result=[self];seen={self.pk}
        parent=self.parent
        while parent:
            if parent.pk in seen:raise ValidationError('دسته نمی‌تواند زیرمجموعه خودش باشد.')
            seen.add(parent.pk);result.insert(0,parent);parent=parent.parent
        return result
    def get_absolute_url(self):return '/shop/'+'/'.join(c.slug for c in self.ancestors())+'/'
    def clean(self):
        super().clean()
        self.ancestors()
        if Category.objects.filter(parent_id=self.parent_id,slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({'slug':'این نشانی در دسته بالادست استفاده شده است.'})
        if self.pk:
            # Check the entire moved subtree against reserved historical URLs.
            for category in Category.objects.all():
                chain=category.ancestors()
                if self.pk in [c.pk for c in chain]:
                    index=next(i for i,c in enumerate(chain) if c.pk==self.pk)
                    path='/shop/'+'/'.join(c.slug for c in self.ancestors()+chain[index+1:])+'/'
                    if CategoryRoute.objects.filter(path=path).exclude(category_id=category.pk).exists():
                        raise ValidationError('این نشانی قبلاً به دسته دیگری تعلق داشته است.')
        elif CategoryRoute.objects.filter(path=self.get_absolute_url()).exists():
            raise ValidationError({'slug':'این نشانی قبلاً استفاده شده است.'})
    def save(self,*args,**kwargs):
        with transaction.atomic():
            # Serialize category edits, including edits to different ancestors.
            list(Category.objects.select_for_update().values_list('pk',flat=True))
            self.full_clean()
            super().save(*args,**kwargs)
            for category in Category.objects.all():
                route,created=CategoryRoute.objects.get_or_create(path=category.get_absolute_url(),defaults={'category':category})
                if route.category_id!=category.pk:raise ValidationError('نشانی دسته تکراری است.')

class CategoryRoute(models.Model):
    path=models.CharField(max_length=1000,unique=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='routes')
    class Meta:app_label='store'
