from django.contrib import admin
from .models import (
    Review,
    ReviewState,
    ReviewChangeLog,
    ReviewStateTransition,
)


admin.site.register(Review)
admin.site.register(ReviewState)
admin.site.register(ReviewChangeLog)
admin.site.register(ReviewStateTransition)
