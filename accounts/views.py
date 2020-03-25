from django.shortcuts import render, redirect
from accounts.models import *
from accounts.forms import OrderForm, CreateUserForm, CustomerForm
from django.forms import inlineformset_factory
from accounts.filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from accounts.decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group


# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def settingsPage(request):
	form = CustomerForm(instance=request.user.customer)
	customer = request.user.customer
	if request.method == 'POST':
		form = CustomerForm(request.POST,request.FILES,instance=customer)
		if form.is_valid():			
			form.save()
	context = {'form':form}
	
	return render(request,'accounts/account_settings.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()
	context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending}
	
	return render(request,'accounts/user.html', context)

@unauthenticated_user
def registerPage(request):
	form = CreateUserForm()

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()			
			username = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for : '+ username)
			return redirect('login')

	return render(request, 'accounts/register.html',{'form':form})

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request,user)
			return redirect('home')
		else:
			messages.info(request,'Username or Password is incorrect...')
			
	return render(request, 'accounts/login.html')

def logoutPage(request):
	logout(request)
	return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
	customers = Customer.objects.all()
	orders =  Order.objects.all()
	total_orders = Order.objects.all().count()
	delivered = Order.objects.filter(status='Delivered').count()
	pending = Order.objects.filter(status='Pending').count()

	return render(request, 'accounts/dashboard.html',context={'customers':customers,'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending})

@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products':products})

@login_required(login_url='login')
def customer(request,pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.all()

	myfilter = OrderFilter(request.GET,queryset=orders)
	orders = myfilter.qs

	total_orders = orders.count()
	context = {'customer': customer, 'orders': orders, 'total_orders':total_orders,'myfilter':myfilter}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
def createOrder(request,pk):
	Orderformset = inlineformset_factory(Customer,Order,fields=('product','status'),extra=2)
	customer = Customer.objects.get(id=pk)
	formset = Orderformset(queryset= Order.objects.none(), instance=customer)
	if request.method == 'POST':
		formset = Orderformset(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('home')
	context = {'formset':formset}
	return render(request,'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
	# print("Request: )
	order = Order.objects.get(id=pk)	
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()			
			return redirect('home')
	context = {'form':form}
	return render(request,'accounts/order_form.html',context)

@login_required(login_url='login')
def deleteOrder(request,pk):

	order = Order.objects.get(id=pk)	
	if request.method == 'POST':
		order.delete()		
		return redirect('home')
	context = {'item':order}
	return render(request,'accounts/delete_order.html',context)