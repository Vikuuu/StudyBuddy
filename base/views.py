from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms =[
#    {'id':1 , 'name': 'Lets learn pyhton!'},
#    {'id':2 , 'name': 'Design with me'},
#    {'id':3 , 'name': 'Front-end development'},
# ]


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        # getting the username and then converting the username into lowercase
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User Does not exist.")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or Password does not exists")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    form = MyUserCreationForm()
    context = {"form": form}

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # using the 'commit' to instantly save the user
            user = form.save(commit=False)
            user.username = (
                user.username.lower()
            )  # converting the username into lowercase
            user.save()
            login(request, user)  # loging in the user
            # Now redirecting the logged in user to the home page
            return redirect("home")
        else:
            messages.error(request, "An error occured during registration ! ")
    return render(request, "base/login_register.html", context)


def home(request):
    # Description:
    # Retrieve the 'q' query parameter from the GET request of the Search bar on the Home Page.
    # If it doesn't exist, set 'q' to an empty string.

    # Comments:
    # Check if the 'q' query parameter exists in the GET request.
    # - If it exists (is not None), assign its value to the variable 'q'.
    # - If it doesn't exist (is None), set 'q' to an empty string ('').
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    # Perform a query to filter rooms based on search criteria.
    rooms = Room.objects.filter(
        # Filter by topic name containing the search query
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        |  # Filter by room name containing the search query
        # Filter by description containing the search query
        Q(description__icontains=q)
    )

    # Retrieve all topics from the database.
    topics = Topic.objects.all()[0:5]

    # Count the number of rooms matching the search criteria.
    room_count = rooms.count()

    # used to display the room messages in the "Recent Activity" feed
    room_messages = Message.objects.filter(
        # when user in the certain topic, user will only see the "recent activity" feed of that certain topic only.
        Q(room__topic__name__icontains=q)
    )

    # Prepare the context dictionary with data to be passed to the template.
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }

    # Render the Home Page template with the context data.
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # in this "room.messege_set.all()" message is the name of the class in the models.py, that holds all the messeages and all the messages are fetched
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("You are not eligible !")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not eligible !")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    context = {"obj": room}
    return render(request, "base/delete.html", context)


login_required(login_url="login")


def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not eligible")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    context = {"obj": message}
    return render(request, "base/delete.html", context)


login_required(login_url="login")


def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    return render(request, "base/update-user.html", {"form": form})


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(Q(name__icontains=q))
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
