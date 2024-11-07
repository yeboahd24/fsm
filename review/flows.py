import difflib
from django.db import transaction
from django.utils import timezone
from viewflow import fsm, this
from .models import Review, ReviewState, ReviewChangeLog
from .models import ReviewStateTransition

# class ReviewFlow(object):
#     """Review process definition."""
#
#     stage = fsm.State(ReviewState, default=ReviewState.NEW)
#
#     def __init__(self, review: Review, user, ip_address=None):
#         self.review = review
#         self.initial_text = self.review.text
#         self.user = user
#         self.ip_address = ip_address
#
#     @stage.setter()
#     def _set_review_stage(self, state_value):
#         self.review.stage = state_value.value
#
#     @stage.getter()
#     def _get_review_stage(self):
#         if self.review.stage:
#             return ReviewState(self.review.stage)
#
#     @stage.on_success()
#     def _on_success_transition(self, descriptor, source, target):
#         if self.review is None:
#             return
#
#         with transaction.atomic():
#             self.review.save()
#             ReviewChangeLog.objects.create(
#                 review=self.review,
#                 source=source.value,
#                 target=target.value,
#                 author=self.user,
#                 ip_address=self.ip_address,
#                 diff="\n".join(
#                     difflib.unified_diff([self.initial_text], [self.review.text])
#                 )
#                 if self.initial_text != self.review.text
#                 else "",
#             )
#             self.initial_text = self.review.text
#
#     @stage.transition(
#         source=ReviewState.NEW, target=ReviewState.APPROVED, permission=this.is_approver
#     )
#     def approve(self):
#         self.review.approver = self.user
#
#     @stage.transition(
#         source=ReviewState.NEW, target=ReviewState.REJECTED, permission=this.is_approver
#     )
#     def reject(self):
#         self.review.approver = self.user
#
#     @stage.transition(
#         source=ReviewState.APPROVED,
#         target=ReviewState.PUBLISHED,
#         permission=lambda flow, user: True,
#     )
#     def publish(self):
#         self.review.published = timezone.now()
#
#     @stage.transition(
#         source=fsm.State.ANY,
#         target=ReviewState.REMOVED,
#         permission=lambda flow, user: True,
#     )
#     def remove(self):
#         pass
#
#     @stage.transition(source=ReviewState.REMOVED, permission=lambda flow, user: True)
#     def delete(self):
#         self.review.delete()
#         self.review = None
#
#     def is_approver(self, user):
#         return user.is_staff


class ReviewFlow(object):
    """Review process definition."""

    stage = fsm.State(ReviewState, default=ReviewState.objects.get(name="New"))

    def __init__(self, review: Review, user, ip_address=None):
        self.review = review
        self.initial_text = self.review.text
        self.user = user
        self.ip_address = ip_address
        self.configure_transitions()

    def configure_transitions(self):
        transitions = ReviewStateTransition.objects.all()
        for transition in transitions:
            source_state = transition.source
            target_state = transition.target
            permission_check = (
                eval(transition.permission_check)
                if transition.permission_check
                else lambda flow, user: True
            )

            self.stage.transition(
                source=source_state, target=target_state, permission=permission_check
            )(self.get_transition_method(source_state, target_state))

    def get_transition_method(self, source_state, target_state):
        transition_logic = {
            (
                ReviewState.objects.get(name="New"),
                ReviewState.objects.get(name="Approved"),
            ): self.approve,
            (
                ReviewState.objects.get(name="New"),
                ReviewState.objects.get(name="Rejected"),
            ): self.reject,
            (
                ReviewState.objects.get(name="Approved"),
                ReviewState.objects.get(name="Published"),
            ): self.publish,
            (
                ReviewState.objects.get(name="New"),
                ReviewState.objects.get(name="Published"),
            ): self.publish,  # Example of a direct transition
            (fsm.State.ANY, ReviewState.objects.get(name="Removed")): self.remove,
            (ReviewState.objects.get(name="Removed"), fsm.State.ANY): self.delete,
        }

        def transition_method():
            logic = transition_logic.get((source_state, target_state))
            if logic:
                logic()
            else:
                raise ValueError(
                    f"No transition logic defined for {source_state.name} -> {target_state.name}"
                )

        return transition_method

    @stage.setter()
    def _set_review_stage(self, state_value):
        self.review.stage = state_value

    @stage.getter()
    def _get_review_stage(self):
        if self.review.stage:
            return self.review.stage

    @stage.on_success()
    def _on_success_transition(self, descriptor, source, target):
        if self.review is None:
            return

        with transaction.atomic():
            self.review.save()
            ReviewChangeLog.objects.create(
                review=self.review,
                source=source.name,
                target=target.name,
                author=self.user,
                ip_address=self.ip_address,
                diff="\n".join(
                    difflib.unified_diff([self.initial_text], [self.review.text])
                )
                if self.initial_text != self.review.text
                else "",
            )
            self.initial_text = self.review.text

    def approve(self):
        self.review.approver = self.user

    def reject(self):
        self.review.approver = self.user

    def publish(self):
        self.review.published = timezone.now()

    def remove(self):
        pass

    def delete(self):
        self.review.delete()
        self.review = None

    def is_approver(self, user):
        return user.is_staff
