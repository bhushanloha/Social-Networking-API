from django.contrib.auth.models import BaseUserManager

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, password2=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth, age, name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,  
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,   
            password=password,
            **extra_fields
            
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user