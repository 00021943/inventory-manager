from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = serializers.JSONField(
        write_only=True,
        required=False,
        help_text='JSON array of items. Format: [{"product": 1, "quantity": 2}, {"product": 2, "quantity": 1}]'
    )
    total_price = serializers.ReadOnlyField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'customer_name', 'status', 'created_at', 'updated_at', 'total_price', 'items', 'items_data']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def validate_items_data(self, value):
        """Validate that order has at least one item"""
        # Handle both list and JSON string
        if isinstance(value, str):
            import json
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for items_data.")
        
        if not isinstance(value, list):
            raise serializers.ValidationError("items_data must be a list/array.")
        
        if not value or len(value) == 0:
            raise serializers.ValidationError("Order must have at least one item.")
        
        # Validate structure of each item
        validated_items = []
        for idx, item_data in enumerate(value):
            if not isinstance(item_data, dict):
                raise serializers.ValidationError(f"Item {idx + 1} must be an object/dictionary.")
            
            product_id = item_data.get('product')
            quantity = item_data.get('quantity')
            
            if not product_id:
                raise serializers.ValidationError(f"Item {idx + 1} must have a 'product' field.")
            
            if not quantity or quantity <= 0:
                raise serializers.ValidationError(f"Item {idx + 1} must have a 'quantity' greater than 0.")
            
            # Get product object
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")
            
            # Check stock availability
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {quantity}."
                )
            
            validated_items.append({
                'product': product,
                'quantity': quantity
            })
        
        return validated_items
    
    def validate(self, data):
        """Validate items and stock availability"""
        items_data = data.get('items_data', [])
        
        if not items_data:
            raise serializers.ValidationError({"items_data": "Order must have at least one item."})
        
        return data
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items_data', [])
        
        if not items_data:
            raise serializers.ValidationError({"items_data": "Order must have at least one item."})
        
        # Set user if not provided
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create order items and update stock
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            
            # Get current price from product
            price = product.price
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            # Update stock
            product.stock_quantity = max(0, product.stock_quantity - quantity)
            product.save()
        
        return order
    
    def update(self, instance, validated_data):
        """Update order - only allow status changes"""
        items_data = validated_data.pop('items_data', None)
        
        # Only allow status updates through API
        if items_data is not None:
            raise serializers.ValidationError({
                "items_data": "Cannot modify order items after creation. Only status can be updated."
            })
        
        # Update status if provided
        if 'status' in validated_data:
            instance.status = validated_data['status']
            instance.save()
        
        return instance
