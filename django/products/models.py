from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

PROTECTED_MEDIA_ROOT = settings.PROTECTED_MEDIA_ROOT
protected_storage = FileSystemStorage(location=str(PROTECTED_MEDIA_ROOT))
# Create your models here.
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    # stripe_product_id = 
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    name = models.CharField(max_length=120)
    handle = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    og_price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    # stripe_price_id = 
    stripe_price = models.IntegerField() # 100 * price
    price_changed_timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.price != self.og_price:

            # tracking price changed
            self.og_price = self.price
            # trigger an API request for the price
            self.stripe_price = int(self.price * 100)
            self.price_changed_timestamp = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/products/{self.handle}/"
    
def handle_product_attachment_upload(instance, filename):
    return f"products/{instance.product.handle}/attachments/{filename}"

        
class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to=handle_product_attachment_upload, storage=protected_storage)
    handle = models.SlugField(unique=True)
    download_available = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)