# from django.http import HttpResponse
from django.shortcuts import render
from .forms import BookingForm
from .models import Menu
from django.core import serializers
from .models import Booking
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    #This line retrieves the value of the 'date' parameter from the GET request. If the 'date' parameter is not present in the request, it defaults to today's date. It seems like this code is using Django's HttpRequest object (request) to get parameters from a URL.
    date = request.GET.get('date',datetime.today().date())
    #This line queries the database for all objects of the Booking model using Django's Object-Relational Mapping (ORM). Booking seems to be a model defined elsewhere in the Django application.
    bookings = Booking.objects.all()
    #This line serializes the queryset of Booking objects into JSON format using Django's built-in serialization framework. This will convert the queryset into a JSON string representation.
    booking_json = serializers.serialize('json', bookings)
    #This line renders a template named 'bookings.html', passing in a dictionary as the context. The context includes a key 'bookings' with the value booking_json, which contains the serialized JSON data of all bookings. The template will likely use this data to display information about the bookings.
    return render(request, 'bookings.html',{"bookings":booking_json})

def book(request):
    #if request.method == 'POST':: Checks if the request method is POST, indicating that the form has been submitted
    if request.method == 'POST':
        #form = BookingForm(request.POST): Binds the form data from the POST request to a form instance.
        form = BookingForm(request.POST)
        #Checks if the form data passes validation based on the form's defined rules.
        if form.is_valid():
            #Saves the validated form data to the database.
            form.save()
    #else:: Executes if the request method is not POST, meaning the user is accessing the page for the first time or via a GET request.
    else:
        #form = BookingForm(): Creates a new instance of the form to render an empty form for the user to fill out.
        form = BookingForm()
    #Prepares the form to be passed to the template for rendering.
    context = {'form':form}
    #Renders the 'book.html' template with the form data included in the context.
    return render(request, 'book.html', context)

# Add your code here to create new views
def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"rawmenu": menu_data} #Django template tag {% for item in menu.menu %}:2nd "menu" refers to the attribute or key within the main_data dictionary that contains the menu data. So, it's essentially iterating over the menu data passed from the view.

    return render(request, 'menu.html', {"storedmenu": main_data}) #Django template tag {% for item in menu.menu %}:1st "menu" refers to the variable name used to pass data from the view to the template. main_data dictionary contains the menu key, which holds the menu data retrieved from the database.

def display_menu_item(request, pk=None):
    #menu_item = Menu.objects.get(pk=pk): If pk has a truthy value, this line queries the Menu model (assuming it's a Django model) to retrieve an object with the primary key specified by pk. It uses .get() method which raises a Menu.DoesNotExist exception if the object is not found
    #if pk:: This line checks if the pk parameter has a truthy value. In Python, an integer primary key will be considered truthy unless it's 0, and None is considered falsy. So, this condition checks if pk is not None
    if pk:
        menu_item = Menu.objects.get(pk=pk)

    else:
        menu_item = "" #else:: If the pk parameter is None, this block of code is executed.menu_item = "": In this case, it assigns an empty string to the menu_item variable. This seems to be done to avoid errors when rendering the template if there is no specific menu item to display.
    return render(request, 'menu_item.html', {"menu_item": menu_item})

@csrf_exempt #This is a decorator in Django framework to exempt the view from CSRF (Cross-Site Request Forgery) protection. It's used when you want to allow POST requests from external sources without requiring CSRF tokens.
def bookings(request):
    if request.method == 'POST':
        #Parses the JSON data sent with the POST request. It loads the JSON data from the request object into a Python dictionary named data
        data = json.load(request)

        #Checks if there's already a booking with the same reservation date and slot in the database. If such a booking exists, exist will be True; otherwise, it will be False.
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(
            reservation_slot=data['reservation_slot']).exists()

        #Checks if exist is False, indicating that the booking doesn't already exist in the database.
        if exist==False:
            #Creates a new Booking object using the data from the POST request. It extracts first_name, reservation_date, and reservation_slot from the data dictionary.
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )
            #Saves the newly created Booking object to the database.
            booking.save()
        #If the booking already exists, this returns a JSON response indicating an error with a status code of 1.
        else:
            return HttpResponse("{'error':1}", content_type='application/json')
    """
    # this can be used to force the date format to match that of django, but it is better to use the Java Script code in the Book template "const date = new Date()
    #document.getElementById('reservation_date').value = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, "0")}-${date.getDate().toString().padStart(2, "0")}`" focus: .toString().padStart(2, "0"), for both month and date.
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format. Please use YYYY-MM-DD', status=400)
    else:
        date = datetime.today().date()
    """
    #Gets the value of the date parameter from the query string of the GET request. If the parameter is not present in the request, it defaults to today's date.
    date = request.GET.get('date', datetime.today().date())
    #Fetches all bookings from the database that match the specified reservation date.
    bookings = Booking.objects.all().filter(reservation_date=date)
    #Converts the queryset of Booking objects into JSON format.
    booking_json = serializers.serialize('json', bookings)
    #Returns a JSON response containing the bookings for the specified date.
    return HttpResponse(booking_json, content_type='application/json')
