from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
#from .player_models import Player
#from .denomination_models import Denomination
#from .nation_models import Nation
#from .company_models import Company

class ItemSection(models.Model):
    TABLE_CHOICES = [
        (1, "Table 1"),
        (2, "Table 2"),
        (3, "Table 3"),
        (4, "Table 4"),
        (5, "Table 5"),
    ]

    name = models.CharField(max_length=100)
    table_number = models.PositiveSmallIntegerField(
        choices=TABLE_CHOICES,
        default=1,
        db_index=True,
    )
    ordering = models.PositiveIntegerField(
        default=0,
        db_index=True,
    )

    class Meta:
        ordering = ["table_number", "ordering", "id"]
        verbose_name = "Item Ordering Section"
        verbose_name_plural = "Item Ordering Sections"

    def __str__(self):
        return f"{self.name}"

# --------------------------------------------------------------------
class Item(models.Model):
    FIXED_PRICE = 'fixed_price'
    MARKET_RATE = 'market_rate'
    SECTION_DIVIDER = 'section_divider'

    PRICE_TYPE_CHOICES = [
        (FIXED_PRICE, 'Fixed Price'),
        (MARKET_RATE, 'Market Rate'),
        (SECTION_DIVIDER, 'Section Divider'),
    ]

    name = models.CharField(max_length=100, unique=True)
    price_type = models.CharField(max_length=15, choices=PRICE_TYPE_CHOICES)
    description = models.CharField(blank=True)
    note = models.CharField(max_length=255, blank=True, help_text="Used for short note about an oddity with the item")  # Optional note field
    image_name = models.CharField(max_length=255, blank=True, help_text="Image name and used for Minecraft Wiki link")
    special_image_name = models.CharField(max_length=255, blank=True, help_text="Overrided image_name for the image, use for when the wiki link does not match the image name")
    section = models.ForeignKey(ItemSection, on_delete=models.PROTECT, related_name="items", null=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)  # Field for manual ordering
    # Precalculated values:
    market_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))
    
    class Meta:
        ordering = ["ordering", "id"]

    def __str__(self):
        return f'{self.name}  ({self.ordering})'
    

    def _total_diamond_value(self, processed_items=None):
        if processed_items is None:
            processed_items = set()
        if self.id in processed_items:
            return Decimal('0')
        processed_items.add(self.id)

        total = Decimal('0')
        for component in self.price_components.all():
            if component.denomination:
                total += Decimal(component.quantity) * Decimal(component.denomination.diamond_equivalent)
            elif component.referenced_item:
                referenced_item = component.referenced_item
                if referenced_item.price_type == self.FIXED_PRICE:
                    # Recursively calculate the price
                    referenced_item_price = referenced_item._total_diamond_value(processed_items)
                elif referenced_item.price_type == self.MARKET_RATE:
                    # Use the market price
                    referenced_item_price = referenced_item.market_price
                else:
                    # If the price type is SECTION_DIVIDER or undefined, treat price as zero
                    referenced_item_price = Decimal('0')
                
                # Apply the percentage, which may be negative
                percentage = Decimal(component.percentage_of_item)
                total += (percentage / Decimal('100')) * referenced_item_price
        return total
    
    @property
    def total_diamond_value(self):
        return self._total_diamond_value()
    
    @property
    def price_breakdown(self):
        return self.price_components.all()
    
    @property
    def market_price(self):
        if self.price_type == self.FIXED_PRICE:
            return self.total_diamond_value
        elif self.price_type == self.MARKET_RATE:
            evaluations = self.item_evaluations.all()
            if not evaluations.exists():
                return Decimal('0')
            _total_value = sum(evaluation.total_diamond_value for evaluation in evaluations)
            market_rate = _total_value / evaluations.count()
            return market_rate.quantize(Decimal('0.000001'))
        return Decimal('0')


# --------------------------------------------------------------------
class ItemEvaluation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_evaluations', limit_choices_to={'price_type': 'market_rate'})
    evaluator = models.ForeignKey('Player', on_delete=models.CASCADE, limit_choices_to={'un_rep': True})
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'evaluator')  # A player can only evaluate an item once


    def __str__(self):
        return f'{self.item.name} evaluation by {self.evaluator.username}'
    
    @property
    def total_diamond_value(self):
        total = Decimal('0')
        for component in self.evaluation_components.all():
            total += Decimal(component.quantity) * Decimal(component.denomination.diamond_equivalent)
        return total
    
# --------------------------------------------------------------------
class ItemEvaluationComponent(models.Model):
    evaluation = models.ForeignKey(ItemEvaluation, on_delete=models.CASCADE, related_name='evaluation_components')
    denomination = models.ForeignKey('Denomination', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('evaluation', 'denomination')

    def __str__(self):
        return f'{self.quantity} x {self.denomination.name} x {self.evaluation}'

    
# --------------------------------------------------------------------
class ItemCount(models.Model):
    nation = models.ForeignKey('Nation', on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=20, decimal_places=3)
    # Precalculated Values:
    total_value = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal('0'))

    class Meta:
        # Ensure the combination of nation/company and item is unique
        constraints = [
            models.UniqueConstraint(fields=['nation', 'item'], name='unique_nation_item'),
            models.UniqueConstraint(fields=['company', 'item'], name='unique_company_item'),
            models.CheckConstraint(
                check=(
                    models.Q(nation__isnull=False, company__isnull=True) |
                    models.Q(nation__isnull=True, company__isnull=False)
                ),
                name='nation_or_company_not_both'
            )
        ]

    def __str__(self):
        if self.nation:
            return f'{self.item.name} - {self.nation.name} x {self.count}'
        elif self.company:
            return f'{self.item.name} - {self.company.name} x {self.count}'
        return f'{self.item.name} x {self.count}'
    
# --------------------------------------------------------------------
class ItemFixedPriceComponent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='price_components')
    denomination = models.ForeignKey('Denomination', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    referenced_item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name='referenced_in_components')
    percentage_of_item = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, help_text="Percentage of the referenced item's price to use (Ex: 50 = 50%)")

    class Meta:
        # Ensure that an item can have multiple price components but unique combinations of item, denomination, or referenced item
        constraints = [
            models.UniqueConstraint(fields=['item', 'denomination', 'referenced_item'], name='unique_price_component'),
        ]


    def clean(self):
        # Ensure that either denomination or referenced_item is provided, but not both
        if not self.denomination and not self.referenced_item:
            raise ValidationError("A price component must have either a denomination or a referenced item.")
        if self.denomination and self.referenced_item:
            raise ValidationError("A price component cannot have both a denomination and a referenced item.")
        
        # Ensure that if referenced_item is provided, percentage_of_item must also be provided
        if self.referenced_item and not self.percentage_of_item:
            raise ValidationError("When using a referenced item, a percentage of that item’s price must be specified.")
        
        # Ensure the item is a fixed-price item
        if self.item.price_type != Item.FIXED_PRICE:
            raise ValidationError(f"Item '{self.item.name}' must be a fixed-price item to have a fixed price component.")
        
        if self.denomination:
            if self.quantity is None:
                raise ValidationError("Quantity must be specified when using a denomination.")
        elif self.referenced_item:
            if self.percentage_of_item is None:
                raise ValidationError("Percentage of item must be specified when referencing another item.")

    def save(self, *args, **kwargs):
        # Call the clean method to validate before saving
        self.clean()
        super().save(*args, **kwargs)


    def __str__(self):
            if self.denomination:
                return f'{self.quantity} x {self.denomination.name} for {self.item.name}'
            elif self.referenced_item:
                return f'{self.percentage_of_item}% of {self.referenced_item.name} for {self.item.name}'
            return f'Component for {self.item.name}'
    
    @property
    def related_item_counts(self):
        """Get all ItemCount instances related to this component's item."""
        return ItemCount.objects.filter(item=self.item)
    
    # --------------------------------------------------------------------
