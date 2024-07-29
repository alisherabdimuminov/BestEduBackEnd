from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpRequest
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from .models import User
from .serializers import UserGETSerializer, UserPOSTSerializer, UserSignUpSerializer
from courses.serializers import RatingModelSerializer
from courses.models import CourseRating, Rating


# get all users handler
@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_users(request: HttpRequest):
    role = request.GET.get("role")
    users_queryset = User.objects.all()
    if role:
        if role == "student":
            users_queryset = User.objects.filter(is_student=True)
        elif role == "teacher":
            users_queryset = User.objects.filter(is_student=False)
    users = UserGETSerializer(users_queryset, many=True).data
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "users": users
        }
    })

@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_users_count(request: HttpRequest):
    users_queryset = User.objects.all()
    s = users_queryset.filter(is_student=True).count()
    t = users_queryset.filter(is_student=False).count()
    u = users_queryset.filter().count()
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "students": s,
            "teachers": t,
            "users": u
        }
    })

# get one user handler
@api_view(http_method_names=["GET"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def get_one_user(request: HttpRequest, id):
    user_queryset = get_object_or_404(User, pk=id)
    user = UserGETSerializer(user_queryset).data
    ratings_obj = Rating.objects.filter(author=user_queryset)
    ratings = RatingModelSerializer(ratings_obj, many=True)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "user": user,
            "ratings": ratings.data
        }
    })

# update user handler
@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def update_user(request: HttpRequest, id):
    data = request.data
    user = get_object_or_404(User, pk=id)
    serializer = UserPOSTSerializer(user, data=data)
    if (serializer.is_valid()):
        serializer.save()
        return Response({
            "status": "success",
            "errors": {},
            "data": None
        })
    else:
        errors = {}
        for error in serializer.errors:
            errors[error] = str(serializer.errors[error][0])
        return Response({
            "status": "error",
            "errors": errors,
            "data": None
        })
    
@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def change_password(request: HttpRequest):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    
    if not old_password:
        return Response({
            "status": "error",
            "errors": {
                1: "old_password topilmadi.",
            }
        })
    if not new_password:
        return Response({
            "status": "error",
            "errors": {
                1: "new_password topilmadi.",
            }
        })
    check = user.check_password(old_password)
    if check:
        user.set_password(raw_password=new_password)
        user.save()
        return Response({
            "status": "success",
            "errors": {},
            "data": {}
        })
    else:
        return Response({
            "status": "error",
            "errors": {
                "old_password": "Eski kalit so'z xato kiritildi."
            },
            "data": {}
        })


# login handler
@api_view(['POST'])
def login(request: HttpRequest):
    user = None
    token = None
    username = request.data.get("username")
    password = request.data.get("password")
    try:
        user = User.objects.filter(username=username).first()
        print("user", user)
        check_password = user.check_password(password)
        if not check_password:
            return Response({
                "status": "error",
                "errors": {
                    "1": "Kalit so'z noto'g'ri"
                },
                "data": None
            })
    except Exception as e:
        print(e)
        return Response({
            "status": "error",
            "errors": {
                "1": "Telefon raqam topilmadi"
            },
            "data": None
        })
    try:
        token = Token.objects.get_or_create(user=user)
        token[0].delete()
        token = Token.objects.create(user=user)
    except Exception as e:
        print(e)
        return Response({
            "status": "error",
            "errors": {
                "1": "Token topilmadi"
            },
            "data": None
        })
    image = user.image
    if image:
        image = request.build_absolute_uri(image.url)
    else:
        image = None
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "token": str(token),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id": user.pk,
            "image": image
        },
    })

# signup handler
@api_view(http_method_names=["POST"])
def signup(request: HttpRequest):
    data = request.data
    user = UserSignUpSerializer(data=data)
    if user.is_valid():
        user.save()
        return Response({
            "status": "success",
            "errors": {},
            "data": None
        })
    else:
        errors = {}
        for error in user.errors:
            errors[error] = str(user.errors[error][0])
        return Response({
            "status": "error",
            "errors": errors,
            "data": None
        })

@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def logout(request: HttpRequest):
    user = request.user
    token = Token.objects.filter(user=user)
    if token:
        token.first().delete()
        Token.objects.create(user=user)
    return Response({
        "status": "success",
        "errors": {},
        "data": {}
    })


@api_view(http_method_names=["POST"])
@authentication_classes(authentication_classes=[TokenAuthentication])
@permission_classes(permission_classes=[IsAuthenticated])
def upload_image(request: HttpRequest):
    image = request.FILES.get("image")
    user = request.user
    user.image = image
    user.save()
    user_serializer = UserGETSerializer(user, many=False)
    return Response({
        "status": "success",
        "errors": {},
        "data": {
            "message": "rasm cho'tki yuklandi.",
            "image": user_serializer.data,
        }
    })
