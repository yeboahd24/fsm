# views.py
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Review, ReviewState
from .serializers import ReviewSerializer
from .flows import ReviewFlow


class ReviewListView(View):
    def get(self, request):
        reviews = Review.objects.all()
        data = [ReviewSerializer().to_representation(review) for review in reviews]
        return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class ReviewDetailView(View):
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            data = ReviewSerializer().to_representation(review)
            return JsonResponse(data)
        except Review.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)

    def post(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            data = json.loads(request.body)
            serializer = ReviewSerializer(data=data, instance=review)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.to_representation(review))
            return JsonResponse(serializer.errors, status=400)
        except Review.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)


@method_decorator(csrf_exempt, name="dispatch")
class ReviewTransitionView(View):
    def post(self, request, pk, action):
        try:
            review = Review.objects.get(pk=pk)
            user = request.user  # Assuming user is authenticated
            ip_address = request.META.get("REMOTE_ADDR")

            # Initialize the review flow
            review_flow = ReviewFlow(review, user, ip_address=ip_address)

            # Perform transition based on action
            if action == "approve":
                review_flow.approve()
            elif action == "reject":
                review_flow.reject()
            elif action == "publish":
                review_flow.publish()
            elif action == "remove":
                review_flow.remove()
            elif action == "delete":
                review_flow.delete()
            else:
                return JsonResponse({"error": "Invalid action"}, status=400)

            # After successful transition
            if review_flow.review:
                return JsonResponse(
                    ReviewSerializer().to_representation(review_flow.review)
                )
            else:
                return JsonResponse(
                    {"message": "Review deleted successfully"}, status=200
                )
        except Review.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# @method_decorator(csrf_exempt, name="dispatch")
# class ReviewCreateView(View):
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return JsonResponse({"error": "Authentication required."}, status=401)
#
#         data = json.loads(request.body)
#         serializer = ReviewSerializer(data=data)
#
#         if serializer.is_valid():
#             review = serializer.save(commit=False)
#             review.author = request.user
#             if not review.stage:
#                 review.stage = ReviewState.NEW  # Default stage if not provided
#             review.save()
#
#             return JsonResponse(
#                 ReviewSerializer().to_representation(review), status=201
#             )
#
#         return JsonResponse(serializer.errors, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class ReviewCreateView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)

        data = json.loads(request.body)
        serializer = ReviewSerializer(data=data)

        if serializer.is_valid():
            review_flow = ReviewFlow.create_new_review(
                user=request.user,
                data=data,
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            return JsonResponse(
                ReviewSerializer().to_representation(review_flow.review), status=201
            )

        return JsonResponse(serializer.errors, status=400)
