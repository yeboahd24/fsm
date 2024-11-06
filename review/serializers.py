# serializers.py
from django import forms
from .models import Review, ReviewChangeLog, ReviewState


class ReviewSerializer(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["stage", "title", "text", "comment"]
        read_only_fields = ["stage"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "stage": instance.stage,
            "stage_display": instance.get_stage_display(),
            "author": instance.author.username,
            "approver": instance.approver.username if instance.approver else None,
            "published": instance.published,
            "title": instance.title,
            "text": instance.text,
            "comment": instance.comment,
        }


class ReviewChangeLogSerializer(forms.ModelForm):
    class Meta:
        model = ReviewChangeLog
        fields = [
            "id",
            "review",
            "changed",
            "source",
            "target",
            "author",
            "ip_address",
            "diff",
        ]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "review": instance.review.id,
            "changed": instance.changed,
            "source": ReviewState(instance.source).label,
            "target": ReviewState(instance.target).label,
            "author": instance.author.username,
            "ip_address": instance.ip_address,
            "diff": instance.diff,
        }
