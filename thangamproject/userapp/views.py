from django.conf import settings
from django.shortcuts import render
import razorpay
from .models import CustomUser,UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate ,login as auth_login,logout
from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import CustomUser
from .models import *
from reportlab.pdfgen import canvas
from thangamproject.settings import BASE_DIR

def loginview(request):
    username = request.session.get('username', None)  # Retrieve the username from the session
    return render(request, 'loginview.html', {'username': username})

 
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        gender = request.POST.get('gender')

        # Perform server-side validation as needed
        if len(username) < 3 or len(password) < 6:
            messages.error(request, 'Invalid input. Please check your username and password.')
            return redirect('register')  # Replace 'registration_page' with your actual registration page URL

        # Check if the username or email already exists
        if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Username or email already exists.')
            return redirect('register')

        # Create a new user and save to the database
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            address=address,
            pincode=pincode,
            gender=gender
        )

        messages.success(request, 'Registration successful. You can now log in.')
        return redirect('login')  # Replace 'login' with your actual login page URL

    return render(request, 'register.html')  # Replace 'registration_page.html' with your actual registration page template

# views.py
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from .models import CustomUser  # Import your CustomUser model

@never_cache
def login(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if request.user.user_type == CustomUser.CUSTOMER:
                    return redirect('/loginview')  # Redirect to the homepage
                elif request.user.user_type == CustomUser.STAFF:
                    print("user is staff")
                    return redirect('order_list')
                elif request.user.user_type == CustomUser.ADMIN:
                    print("user is admin")
                    return redirect('/adminpage')
            else:
                messages.success(request, "Invalid Username or Password.")
                return redirect('login')  # Make sure this is the correct URL for your login page

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')  # Replace 'login' with the URL name of your login page

@login_required(login_url='login')
def logview(request):
     return render(request,'loginview.html')
 
# Create your views here.
def adminpage(request):
    # Query all User objects (using the custom user model) from the database
    User = get_user_model()
    customer_users = User.objects.filter(user_type=3)    
    # Pass the data to the template
    context = {'user_profiles': customer_users}
    
    # Render the HTML template
    return render(request, 'adminpage.html', context)


def customer_list(request):
    User = get_user_model()
    customer_users = User.objects.filter(user_type=3)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('status')
        user = User.objects.get(id=user_id)
        if new_status in ['active', 'inactive']:
            user.user_status = new_status
            user.save()
            messages.success(request, f'Status for {user.username} has been changed to {new_status}.')
        user.save()

    context = {'user_profiles': customer_users}
    return render(request, 'customer_list.html', context)

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def change_status(request, user_id):
    if request.method == 'POST':
        User = get_user_model()
        user = User.objects.get(id=user_id)
        new_status = request.POST.get('status')

        if new_status == 'active':
            # Activate the user
            user.is_active = True

            # Send an activation email
            subject = 'Account Activation'
            message = render_to_string('activation_email.html', {'user': user})
            from_email = 'mailtoshowvalidationok@gmail.com'  
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        elif new_status == 'inactive':
            # Deactivate the user
            user.is_active = False

            # Send a deactivation email
            subject = 'Account Deactivation'
            message = render_to_string('deactivation_email.html', {'user': user})
            from_email = 'mailtoshowvalidationok@gmail.com' 
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        user.save()
        messages.success(request, f'Status for {user.username} has been changed to {new_status}.')
    
    return redirect('customer_list')

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

def send_deactivation_email(user):
    subject = "Your Account Deactivation"
    from_email = "mailtoshowvalidationok@gmail.com"  # Replace with your email address
    recipient_list = [user.email]

    # Render the deactivation email template
    context = {'user': user}
    html_message = render_to_string('deactivation_email.html', context)

    # Send the email
    msg = EmailMultiAlternatives(subject, strip_tags(html_message), from_email, recipient_list)
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def deactivate_user(request, user_id):
    if request.method == 'POST':
        User = get_user_model()
        user = User.objects.get(id=user_id)
        new_status = request.POST.get('status')

        if new_status == 'inactive':
            # Deactivate the user
            user.is_active = False
            user.save()

            # Send deactivation email
            send_deactivation_email(user)

    return redirect('customer_list')


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

def send_activation_email(user):
    subject = "Your Account Activation"  # Update the subject to match activation
    from_email = "mailtoshowvalidationok@gmail.com"  # Replace with your email address
    recipient_list = [user.email]

    # Render the activation email template
    context = {'user': user}
    html_message = render_to_string('activation_email.html', context)  # Update template name

    # Send the email
    msg = EmailMultiAlternatives(subject, strip_tags(html_message), from_email, recipient_list)
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def activate_user(request, user_id):  # Update the function name to be consistent
    if request.method == 'POST':
        User = get_user_model()
        user = User.objects.get(id=user_id)
        new_status = request.POST.get('status')

        if new_status == 'active':  # Update the condition to match activation
            # Activate the user
            user.is_active = True  # Update the activation action
            user.save()

            # Send activation email
            send_activation_email(user)  # Update the email function name

    return redirect('customer_list')


def contact(request):
    return render(request, 'contact.html')

def adminprofile(request):
    return render(request, 'adminprofile.html')


def delete_product(request, product_id):
    if request.method == 'POST':
        # Delete the product from the database
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return redirect('viewproduct')
        except Product.DoesNotExist:
            pass
    return redirect('viewproduct')  # Redirect back to the product list view

def view_product(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'viewproduct.html', {'products': products})

from django.shortcuts import render, get_object_or_404
from .models import Product
from django.http import JsonResponse

def product_grid(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


def adminpage(request):
    # Query all User objects (using the custom user model) from the database
    User = get_user_model()
    customer_users = User.objects.filter(user_type=3)    
    # Pass the data to the template
    context = {'user_profiles': customer_users}
    
    # Render the HTML template
    return render(request, 'adminpage.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def profile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'user': user, 'user_profile': user_profile, 'form': form})

from .models import Product

def featured_product(request):
    products = Product.objects.all()
    return render(request, 'loginview.html', {'products': products})



from django.shortcuts import render, redirect
from .models import Product

def edit_product(request, product_id):
    # Retrieve the product based on the product_id
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        try:
            
            product.product_name = request.POST.get('product-name')
            product.category = request.POST.get('category-name')
            product.subcategory = request.POST.get('subcategory-name')
            product.quantity = request.POST.get('quantity')
            product.description = request.POST.get('description')
            product.price = float(request.POST.get('price', 0))
            product.discount = float(request.POST.get('discount', 0))
            product.status = request.POST.get('status')
            product_image = request.FILES.get('product-image')

            
            if product_image:
                product.product_image = product_image

            product.making_charge = float(request.POST.get('making-charge', 0))
            product.gold_value = float(request.POST.get('gold-value', 0))
            product.gold_weight = float(request.POST.get('gold-weight', 0))  # Add this line for gold weight
            product.stone_cost = float(request.POST.get('stone-cost', 0))
            product.gst_rate = float(request.POST.get('gst-rate', 0))

            
            product.purity_of_gold = request.POST.get('purity-of-gold')

            
            product.calculate_sale_price()

            
            product.save()

            
            return redirect('adminpage')

        except Exception as e:
            
            print(f"An error occurred: {e}")

    return render(request, 'edit_product.html', {'product': product})







from django.shortcuts import render, redirect
from .models import Category, Subcategory

def load_add_product_form(request):
    categories = Category.objects.all()
    return render(request, 'your_template.html', {'categories': categories})


from django.shortcuts import render
from .models import Category, Subcategory

def category_view(request):
    categories = Category.objects.all()
    return render(request, 'category.html', {'categories': categories})

def subcategory_view(request):
    subcategories = Subcategory.objects.all()
    return render(request, 'subcategory.html', {'subcategories': subcategories})




from django.shortcuts import render, redirect
from .models import Feedback

def feedback_submit(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        feedback = Feedback.objects.create(
            username=username,
            email=email,
            subject=subject,
            message=message
        )
       
        return redirect('contact')  
    else:
       
        pass


from django.shortcuts import render
from .models import Feedback

def feedback_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

from django.shortcuts import render
from .models import UserProfile

def staff_list(request):
   User = get_user_model()
   staff_members = User.objects.filter(user_type=2)
   context = {'staff_members': staff_members}
   return render(request, 'staff_list.html', context)





def change_staff_status(request, staff_id):
    User = get_user_model()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        staff_member = User.objects.get(id=staff_id)

        if new_status == 'active':
            staff_member.is_active = True
            messages.success(request, f'{staff_member.username} is now active.')
        elif new_status == 'inactive':
            staff_member.is_active = False
            messages.success(request, f'{staff_member.username} is now inactive.')

        staff_member.save()

    return redirect('staff_list')


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

def change_staff_status(request, staff_id):
    if request.method == 'POST':
        User = get_user_model()
        try:
            staff = User.objects.get(id=staff_id)
        except User.DoesNotExist:
            messages.error(request, "Staff member does not exist.")
            return redirect('staff_list')

        new_status = request.POST.get('status')

        if new_status == 'active':
            # Activate the staff member
            staff.is_active = True

            # Send an activation email
            subject = 'Staff Account Activation'
            message = render_to_string('activation_email.html', {'user': staff})
            from_email = 'mailtoshowvalidationok@gmail.com'  # Update with your email
            recipient_list = [staff.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        elif new_status == 'inactive':
            # Deactivate the staff member
            staff.is_active = False

            # Send a deactivation email
            subject = 'Staff Account Deactivation'
            message = render_to_string('deactivation_email.html', {'user': staff})
            from_email = 'mailtoshowvalidationok@gmail.com'  # Update with your email
            recipient_list = [staff.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        staff.save()
        messages.success(request, f'Status for {staff.username} has been changed to {new_status}.')
    
    return redirect('staff_list')

def send_activation_email(user):
    subject = "Your Account Activation"
    from_email = "mailtoshowvalidationok@gmail.com"
    recipient_list = [user.email]

    # Render the activation email template
    context = {'user': user}
    html_message = render_to_string('activation_email.html', context)

    # Send the email
    send_mail(subject, strip_tags(html_message), from_email, recipient_list, html_message=html_message)

def send_deactivation_email(user):
    subject = "Your Account Deactivation"
    from_email = "mailtoshowvalidationok@gmail.com"
    recipient_list = [user.email]

    # Render the deactivation email template
    context = {'user': user}
    html_message = render_to_string('deactivation_email.html', context)

    # Send the email
    send_mail(subject, strip_tags(html_message), from_email, recipient_list, html_message=html_message)


    
    
    



    
    










    


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from django.template.loader import render_to_string
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(request, gold_item_id):
    
    gold_item = get_object_or_404(GoldItemNew, pk=gold_item_id)
    product = gold_item.product 

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="gold_item_details_{gold_item_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
    elements = []

    header_text = '<font size="24" color="red"><b>THANGAM JEWELLERY</b></font>'
    header_style = getSampleStyleSheet()['Title']
    header_paragraph = Paragraph(header_text, header_style)
    elements.append(header_paragraph)
 
    elements.append(Spacer(1, 24))  

    product_image = Image(product.product_image.path, width=100, height=100)
    elements.append(product_image)

    elements.append(Spacer(1, 12))  

    product_details = [
        ["Product Name", product.product_name],
        ["Gold Weight", f"{gold_item.weight} Grams"],
        ["Purity of Gold", product.purity_of_gold],
        ["Volume", gold_item.volume],
        ["predicted_purity_percentage (%)", f"{product.predicted_purity_percentage}%"],
    ]
    details_table = Table(product_details, style=[
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONT_SIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    elements.append(details_table)
    elements.append(Spacer(1, 12)) 

    description_text = """
    <b>Gold Weight:</b><br/>
    Refers to the mass of the gold, typically measured in grams (g) or ounces (oz).<br/>
    The weight of gold determines its value, with heavier pieces generally being more valuable.<br/>
    Used in calculations to determine the overall value of gold items.<br/><br/>

    <b>Purity of Gold:</b><br/>
    Denoted in karats (K) or fineness, indicating the proportion of pure gold in an alloy.<br/>
    Common purities include 24K (99.9% pure), 22K (91.7% pure), and 18K (75% pure), among others.<br/>
    Higher purity gold typically has a brighter yellow color and is more valuable but may also be softer and less durable.<br/><br/>

    <b>Volume of Gold:</b><br/>
    Represents the space occupied by the gold, measured in cubic centimeters (cm³) or milliliters (ml).<br/>
    Determined by measuring the length, width, and height of the gold object or by displacement in a liquid.<br/>
    Used in density calculations to predicted_purity_percentage when combined with weight.<br/><br/>

    <b>predicted_purity_percentage (%):</b><br/>
    Calculated based on the gold's weight, volume, and density.<br/>
    Provides an approximation of the gold's purity, often expressed as a percentage.<br/>
    Helpful for assessing the value and quality of gold items, especially when purity testing methods are unavailable or impractical.<br/>
    """
    description_box = Paragraph(description_text, getSampleStyleSheet()['Normal'])
    elements.append(description_box)

    # Build the PDF
    doc.build(elements)

    return response

  
    
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def product_pdf(request, gold_item_id):
    gold_item = get_object_or_404(GoldItemNew, pk=gold_item_id)
    product = gold_item.product 

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="gold_item_details_{gold_item_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
    elements = []

    header_text = '<font size="24" color="red"><b>THANGAM JEWELLERY</b></font>'
    header_style = getSampleStyleSheet()['Title']
    header_paragraph = Paragraph(header_text, header_style)
    elements.append(header_paragraph)
 
    elements.append(Spacer(1, 24))  

    product_image = Image(product.product_image.path, width=100, height=100)
    elements.append(product_image)

    elements.append(Spacer(1, 12))  

    product_details = [
        ["Product Name", product.product_name],
        ["Gold Weight", f"{gold_item.weight} Grams"],
        ["Purity of Gold", product.purity_of_gold],
        ["Volume", gold_item.volume],
        ["predicted_purity_percentage (%)", f"{product.predicted_purity_percentage}%"],
    ]
    details_table = Table(product_details, style=[
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONT_SIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    elements.append(details_table)
    elements.append(Spacer(1, 12)) 

    description_text = """
    <b>Gold Weight:</b><br/>
    Refers to the mass of the gold, typically measured in grams (g) or ounces (oz).<br/>
    The weight of gold determines its value, with heavier pieces generally being more valuable.<br/>
    Used in calculations to determine the overall value of gold items.<br/><br/>

    <b>Purity of Gold:</b><br/>
    Denoted in karats (K) or fineness, indicating the proportion of pure gold in an alloy.<br/>
    Common purities include 24K (99.9% pure), 22K (91.7% pure), and 18K (75% pure), among others.<br/>
    Higher purity gold typically has a brighter yellow color and is more valuable but may also be softer and less durable.<br/><br/>

    <b>Volume of Gold:</b><br/>
    Represents the space occupied by the gold, measured in cubic centimeters (cm³) or milliliters (ml).<br/>
    Determined by measuring the length, width, and height of the gold object or by displacement in a liquid.<br/>
    Used in density calculations to predicted_purity_percentage when combined with weight.<br/><br/>

    <b>predicted_purity_percentage (%):</b><br/>
    Calculated based on the gold's weight, volume, and density.<br/>
    Provides an approximation of the gold's purity, often expressed as a percentage.<br/>
    Helpful for assessing the value and quality of gold items, especially when purity testing methods are unavailable or impractical.<br/>
    """
    description_box = Paragraph(description_text, getSampleStyleSheet()['Normal'])
    elements.append(description_box)

    # Build the PDF
    doc.build(elements)

    return response






from django.http import JsonResponse
from userapp.models import GoldItemNew

def product_data_endpoint_view(request):
    # Fetch all GoldItemNew objects
    gold_items = GoldItemNew.objects.all()

    # Prepare data for the graph
    product_data = {
        'labels': [],
        'data': {
            'weight': [],
            'volume': [],
            'purity_of_gold': [],
            'predicted_purity_percentage': [],
        }
    }

    # Populate the data dictionary
    for item in gold_items:
        product_data['labels'].append(item.product.product_name)
        product_data['data']['weight'].append(item.weight)
        product_data['data']['volume'].append(item.volume)
        product_data['data']['purity_of_gold'].append(item.product.purity_of_gold)
        product_data['data']['predicted_purity_percentage'].append(item.predicted_purity_percentage)

    # Return the data as JSON response
    return JsonResponse(product_data)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def manage(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.pincode = request.POST.get('pincode')
        user.address = request.POST.get('address')
        user.save()
        messages.success(request, 'Your information has been updated successfully.')
        return redirect('manage')  # Redirect to the 'manage' URL pattern after updating
    return render(request, 'manage.html')  # Render the 'manage.html' template for GET requests








def product_details(request, product_id):
    request.session['product_id'] = product_id
    product = get_object_or_404(Product, product_id=product_id)  # Use 'product_id' instead of 'id'
    amount=product.sale_price
    
    # Create a Razorpay Order
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    currency = 'INR'
    amount = int(amount * 100)

    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    
    # Get the order ID of the newly created order
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'  # Make sure to provide the correct callback URL
    
    # Pass necessary details to the frontend
    context = {
        'product': product,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
    }
    
    return render(request, 'product_details.html', context=context)


from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            print(payment_id,razorpay_order_id)

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            
            print(result)
            
            if result is not None:
                # Capture the payment
                print(payment_id)
                product_id = request.session.get('product_id')
                product = get_object_or_404(Product, product_id=product_id)
                print(product.product_name)
                print(request.user)
               
                

                # Save payment details to database
                payment = Payment.objects.create(
                    user=request.user,  # Assuming user is logged in
                    product=product,
                    razorpay_payment_id=payment_id,
                    razorpay_order_id=razorpay_order_id,
                    razorpay_signature="hhhhhhhhhhh",
                    payment_status='Success',  # Assuming payment is successful
                )
                
                
                # Render success page
                # return render(request, 'payment_success.html', {'payment': payment})
                return redirect('orderdetails')
            else:
                # If signature verification fails
                return HttpResponse("FAIL")
        except:
            # Handle exceptions
            return HttpResponse("fail")
    else:
        # Handle non-POST requests
        return HttpResponse("nothing")
    
    
    
def orderdetails(request):
    payments = Payment.objects.filter(user=request.user)

    context = {
        'payments': payments
    }
    return render(request, 'payment_success.html',context)



def payment_success(request):
    payments = Payment.objects.filter(user=request.user)
    payment_id = 123
    context = {
        'payments': payments,
        'payment_id': payment_id,
    }
    return render(request, 'payment_success.html', context)


    
    
    
from .models import CustomUser, Payment 

def order_list(request):
    
    
    customers = CustomUser.objects.filter(user_type=CustomUser.CUSTOMER)
    for customer in customers:
        customer.orders = Payment.objects.filter(user=customer)  # Filter payments by user (customer)
        
    return render(request, 'order_list.html', {'customers': customers})




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Payment

def generate_pdf_bill(request, payment_id):
    try:
        # Fetch payment details based on payment_id
        payment = Payment.objects.get(id=payment_id)

        # Ensure purity is a 6-digit value
        purity = payment.product.predicted_purity_percentage
        if len(str(purity)) > 6:
            purity = str(purity)[:6]

        context = {
            'num_of_products': payment.product.quantity,
            'product_name': payment.product.product_name,
            'price': payment.product.price,
            'discount': payment.product.discount,
            'making_charge': payment.product.making_charge,
            'gold_value': payment.product.gold_value,
            'gold_weight': payment.product.gold_weight,
            'stone_cost': payment.product.stone_cost,
            'gst_rate': payment.product.gst_rate,
            'total_price': payment.product.sale_price,
            'purity': purity,  # Use the adjusted purity value
            'payment_date': payment.payment_date.strftime("%d-%b-%Y"),
        }

        # Render HTML template with context
        template = get_template('bill.html')
        html = template.render(context)

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bill.pdf"'

        # Convert HTML to PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)

        return response

    except Payment.DoesNotExist:
        return HttpResponse("Payment not found.", status=404)







import pandas as pd
from django.shortcuts import render, redirect
from .models import Product, GoldItemNew
from sklearn.linear_model import LinearRegression
import numpy as np
from django.http import JsonResponse



def add_product(request):
    if request.method == 'POST':
        # Extract data from the form 
        gold_weight = float(request.POST.get('gold-weight', 0))  # Extract gold weight from POST data
        volume = float(request.POST.get('volume', 0))
        
        # Validate user input
        if gold_weight <= 0 or volume <= 0:
            raise ValueError("Gold weight and volume must be positive.")
            
        # Calculate density of gold alloy
        gold_value_str = request.POST.get('gold-value', '')  # Get gold value as string
        gold_value = float(gold_value_str) if gold_value_str else 0
        
        density_gold_alloy = gold_weight / volume
        
        # Make prediction using the trained model
      
        
        # Calculate predicted purity percentage using the formula
        density_pure_gold = 19.32  # Assuming density of pure gold is 19.32 g/cm³
        predicted_purity_percentage = (density_gold_alloy/density_pure_gold ) * 100
        
       
     
        if gold_value < 0:
            raise ValueError("Gold value must be non-negative.")
       
        # Determine purity category based on predicted purity
        if predicted_purity_percentage >= 95:
            purity_of_gold = '24k'
        elif predicted_purity_percentage >= 91:
            purity_of_gold = '22k'
        else:
            purity_of_gold = '18k'
        
        
        product = Product(
            product_name=request.POST.get('product-name'),
            category=request.POST.get('category-name'),
            subcategory=request.POST.get('subcategory-name'),
            quantity=request.POST.get('quantity'),
            description=request.POST.get('description'),
            status=request.POST.get('status'),
            product_image=request.FILES.get('product-image'),
            price=float(request.POST.get('price', 0)),
            discount=float(request.POST.get('discount', 0)),
            making_charge=float(request.POST.get('making-charge', 0)),
            gold_value=gold_value, 
            stone_cost=float(request.POST.get('stone-cost', 0)),
            gst_rate=float(request.POST.get('gst-rate', 0)),
            sale_price=float(request.POST.get('price', 0)) - (float(request.POST.get('price', 0)) * (float(request.POST.get('discount', 0)) / 100)) + float(request.POST.get('making-charge', 0)) + (float(request.POST.get('gold-value', 0)) * float(request.POST.get('gold-weight', 0))) + float(request.POST.get('stone-cost', 0)),
            purity_of_gold=purity_of_gold,  # Use determined purity here
            gold_weight=gold_weight,
            density_gold_alloy=density_gold_alloy,  # Use calculated density here
            predicted_purity_percentage=predicted_purity_percentage  # Save predicted purity percentage
        )
        product.save()
        
        # Save gold item data
        gold_item = GoldItemNew(
            product=product,
            weight=gold_weight,
            volume=volume,
            predicted_purity_percentage=predicted_purity_percentage 
        )
        gold_item.save()

        return redirect('adminpage')  # Redirect to admin page after successful addition

    return render(request, 'adminpage.html')




def golditem_list(request):
    # Retrieve all GoldItemNew objects from the database
    gold_items = GoldItemNew.objects.all()

    # Update predicted purity percentage for each GoldItemNew instance
    for item in gold_items:
        # Calculate predicted purity percentage using the formula
        density_pure_gold = 19.32  # Assuming density of pure gold is 19.32 g/cm³
        density_gold_alloy = item.weight / item.volume
        predicted_purity_percentage = ( density_gold_alloy/density_pure_gold ) * 100
        # Update the predicted_purity_percentage field for the current item
        item.predicted_purity_percentage = predicted_purity_percentage
        item.save()

    # Pass gold_items queryset to the template context
    return render(request, 'calculate_purity.html', {'gold_items': gold_items})




def predict_purity(request):
    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        volume = float(request.POST.get('volume'))
        
        # Assuming you have trained a linear regression model and stored it in a variable called 'model'
        
        # Create a new GoldItemNew instance and save it
        gold_item = GoldItemNew(weight=weight, volume=volume)
        gold_item.save()
        
        return render(request, 'calculate_purity.html')



