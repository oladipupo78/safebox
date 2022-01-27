from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Member
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework import generics
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import  IsAuthenticated
from rest_framework.views import APIView
from .serializers import MemberSerializer
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from repo.models import File,FileRepo
from django.views.decorators.cache import cache_page
from .tasks import test_func
import zipfile


def test(request):
    test_func.delay()
    return HttpResponse('Done')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            u = User.objects.get(username=email)
            member = Member(email=u, name =name)
            member.save()
            auth.login(request, user)
            return redirect('dashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'PSignup.html', {'mg': mg})
    else:
        return render(request, 'PSignup.html')

def signin(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['email'], password=request.POST['password'])
        try:
            auth.login(request, user)
            return redirect('dashboard')
        except user is not None:
            return render(request, 'Signin.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'Signin.html')

def dashboard(request):
    u = User.objects.get(username=request.user.get_username())
    member = Member.objects.get(email=u)
    privatefile = File.objects.filter(uploaded_by=u,filetype ='private')
    publicfile = File.objects.filter(uploaded_by=u, filetype='public')
    return render(request, 'user-profile.html', {'member': member, 'privatefiles': privatefile, 'publicfiles': publicfile})

def uploadfile(request):
    user = User.objects.get(username=request.user.get_username())
    filename = request.POST['file_name']
    filetype = request.POST['file_type']
    file = File(uploaded_by=user, name=filename,filetype =filetype )
    file.save()
    return redirect('dashboard')

@cache_page(60 * 15)
def uploaddocument(request):
    if request.method == 'POST' and request.FILES['document_src']:
        document_name = request.POST['document_name']
        document_src = request.FILES['document_src']
        fs = FileSystemStorage()
        doc = fs.save(document_src.name, document_src)
        filename = request.POST['file_name']
        user = User.objects.get(username=request.user.get_username())
        file = File.objects.get(uploaded_by=user,name=filename)
        document = FileRepo(file=file, document_name =document_name, document_src =doc)
        document.save()
        return redirect('dashboard')
    else:
        user = User.objects.get(username=request.user.get_username())
        file = File.objects.filter(uploaded_by=user)
        return render(request, 'edit-userprofile.html', {'files': file})

def filedescription(request,id):
    file = File.objects.get(id=id)
    documents = FileRepo.objects.filter(file=file)
    return render(request, 'filedescription.html', {'documents': documents, 'file': file})

def publicfiledescription(request,id):
    file = File.objects.get(id=id)
    documents = FileRepo.objects.filter(file=file)
    return render(request, 'filedescription2.html', {'documents': documents, 'file': file})

def changetype(request,id):
    file = File.objects.get(id=id)
    if file.filetype == 'public':
        file.filetype = 'private'
        file.save()
    elif file.filetype == 'private':
        file.filetype = 'public'
        file.save()
    return redirect('filedescription')

def deletefile(request,id):
    file = File.objects.get(id=id)
    file.delete()
    return redirect('dashboard')

def download(request,id):
    filename = 'Safebox_download.zip'
    response = HttpResponse(content_type='application/zip')
    zf = zipfile.ZipFile(response,'w')
    file = File.objects.get(id=id)
    documents = FileRepo.objects.filter(file=file)
    for document in documents:
        zf.write('./media/'+ str(document.document_src))
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@api_view(['GET','POST'])
def member_list(request):
    if request.method == 'GET':
        members = Member.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT', 'DELETE'])
def member_detail(request,pk):
    try:
        member = Member.objects.get(pk=pk)

    except Member.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        serializer = MemberSerializer(member,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        member.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

class MemberViewset(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class MemberAPIView(APIView):

    def get(self,request):
        members = Member.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class mygeneric(generics.GenericAPIView,mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.ListModelMixin,mixins.DestroyModelMixin,mixins.RetrieveModelMixin):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    lookup_field = 'id'
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request, id=None):
        if id:
            return self.retrieve(request,id)
        else:
            return self.list(request)

    def post(self,request):
        return self.create(request)

    def put(self,request, id=None):
        return self.update(request,id)


    def delete(self,request, id=None):
        return self.destroy(request,id)