from rest_framework import serializers
from stocks.models import (
    CREATED,
    DELETED,
    Stocks,
    User,
    UserStockAlerts
)


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128 
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so lets just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token',)

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is that
        # we don't need to specify anything else about the field. The
        # password field needed the `min_length` and 
        # `max_length` properties, but that isn't the case for the token
        # field.
        read_only_fields = ('token',)


    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # Django provides a function that handles hashing and
        # salting passwords. That means
        # we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance
    

class StocksSerializer(serializers.ModelSerializer):
    """Handles serialization of Stock objects."""

    class Meta:
        model = Stocks
        fields = ('stock_id', 'symbol', 'name', 'current_price', 'updated_at')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is that
        # we don't need to specify anything else about the field. The
        # password field needed the `min_length` and 
        # `max_length` properties, but that isn't the case for the token
        # field.
        read_only_fields = ('current_price',)


class UserStockAlertsSerializer(serializers.ModelSerializer):
    """Handles de-serialization of UserStockAlert objects."""

    class Meta:
        model = UserStockAlerts
        fields = ('id', 'user', 'stock', 'desired_price')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        status = CREATED
        validated_data.pop('status', None)
        validated_data['status'] = status
        return super().create(validated_data)
