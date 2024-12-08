from django.db import models, transaction
import os
from django.utils import timezone



    

class Styles(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Radios(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Moteurs(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Taux(models.Model):
    taux_buy = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.taux_buy)




class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    surname  = models.CharField(max_length=100)
    telephone  = models.CharField(max_length=100)
    email  = models.EmailField()
    date_of_birth  = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    

    def __str__(self):
        return self.name




class Car(models.Model):
    id = models.AutoField(primary_key=True)
    id_car = models.CharField(max_length=200,default='None') 
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cars/')
    is_active = models.BooleanField(default=False)
    air_condition = models.BooleanField(default=False)
    power_steering = models.BooleanField(default=False)
    central_locking = models.CharField(max_length=100,default='None') 
    doors = models.IntegerField(default=0)
    moteur  =  models.CharField(max_length=100)
    is_owner_car = models.BooleanField(default=False)
    passengers = models.IntegerField(default=0) 
    car_model = models.CharField(max_length=100,default='None') 
    is_auto = models.BooleanField(default=False)
    radio = models.BooleanField(default=False)
    

    def __str__(self):
        return self.title
    def delete_img(self):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
                
    def delete(self, *args, **kwargs):
    # Delete the image file if it exists
        self.delete_img()
        
        # Call the parent class delete method
        super().delete(*args, **kwargs)

class Accessoire(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_per_day  = models.BooleanField(default=False)
    price  = models.DecimalField(max_digits=10, decimal_places=2)
    description  = models.CharField(max_length=200 , default='None')
    is_multiple  = models.BooleanField(default=False)
    nbr_choices = models.IntegerField(default=0)
    
    
    def __str__(self):
        return self.name


class Detail_accessoire(models.Model):
    id = models.AutoField(primary_key=True)
    acc = models.ForeignKey(Accessoire, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    
    
    def __str__(self):
        return str(self.id)



class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    ass_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500 , default='None') 
    is_confirmed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    date_created =models.CharField(max_length=15 , default='None') 
    accessoire = models.ManyToManyField(Detail_accessoire,  blank=True)
    pickupdate = models.CharField(max_length=500 , default='None') 
    dropoffdate = models.CharField(max_length=500 , default='None') 
    location = models.CharField(max_length=500 , default='None') 
    nbr_days = models.IntegerField(default=0)
    id_booking = models.CharField(max_length=20, unique=True, blank=True)
    date_part = models.DateField(editable=False, blank=True, null=True)
    selected_return_location = models.CharField(max_length=500 , default='None') 
    taux_buy = models.DecimalField(max_digits=10, decimal_places=2)
    car_price = models.DecimalField(max_digits=10, decimal_places=2)
    hoteldropname = models.CharField(max_length=500 , default='None') 
    hotelname = models.CharField(max_length=500 , default='None') 





    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):
        if not self.id_booking:
            # Ensure date_created is set
            if not self.date_created:
                self.date_created = timezone.now()

            # Ensure date_part is set
            self.date_part = self.date_created

            with transaction.atomic():
                super().save(*args, **kwargs)
                # Get the count of bookings for today
                from datetime import datetime
                cc = Booking.objects.filter(date_part=self.date_part).count()
                count_today = cc 
                date_obj = datetime.strptime(self.date_part, '%Y-%m-%d')
                # Format the datetime object to the desired format
                formatted_date = date_obj.strftime('%Y%m%d')
                self.id_booking = f'{formatted_date}_{count_today}T'
                    # Save again to update the id_booking field
        super().save(*args, **kwargs)






class Contactclient(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.CharField(max_length=300)
    date_created = models.CharField(max_length=15 , default='None')

    def __str__(self):
        return self.name








