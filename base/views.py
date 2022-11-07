from django.shortcuts import render
from rest_framework import generics
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.http import JsonResponse
from base.services.get_todo import GetToDoService


class DetailTodo(generics.RetrieveUpdateAPIView):
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer


class CreateTodo(generics.CreateAPIView):
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer


class DeleteTodo(generics.DestroyAPIView):
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer


class GetTodoList(APIView):
    def get(self, request) -> JsonResponse:
        all = request.query_params.get("all", "0") == "1"
        (success, detail, todos) = GetToDoService(all=all).perform()

        status_code = 200 if success else 400
        return JsonResponse(
            {
                "success": success,
                "detail": detail,
                "todo": todos,
            },
            status=status_code
        )
