from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from un_app.models import Nation

class ExecutiveOrder(models.Model):
    number = models.PositiveIntegerField()
    charter = models.PositiveIntegerField()
    date = models.DateField()
    ordered_by = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='ordered_executive_order')
    body = models.TextField()
    void = models.BooleanField(default=False, blank=True)
    repealed = models.BooleanField(default=False, blank=True)
    invalidation_date = models.DateField(null=True, default=None, blank=True, help_text="Date the resolution was considered void or repealed")
    
    class Meta:
        unique_together = ('number', 'charter')
        
    def get_absolute_url(self):
        return reverse('executive_order_detail',kwargs={'charter': self.charter, 'number': self.number,})
    
    def clean(self):
        # Ensure that invalidation_date is only set when void or repealed is True
        if (self.void or self.repealed) and not self.invalidation_date:
            raise ValidationError("Invalidation date must be set if the resolution is void or repealed.")
        
        # Ensure that invalidation_date is None if neither void nor repealed is True
        if not (self.void or self.repealed) and self.invalidation_date:
            raise ValidationError("Invalidation date cannot be set unless the resolution is void or repealed.")

    def __str__(self):
        return f"Executive Order No. {self.number} ({self.date}) Charter {self.charter}"