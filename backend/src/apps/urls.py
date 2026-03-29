from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'clinics', views.ClinicViewSet, basename='clinic')
router.register(r'staff', views.StaffViewSet, basename='staff')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'pets', views.PetViewSet, basename='pet')
router.register(r'vaccinations', views.VaccinationRecordViewSet, basename='vaccination')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'medical-records', views.MedicalRecordViewSet, basename='medical-record')
router.register(r'medications', views.MedicationViewSet, basename='medication')
router.register(r'prescriptions', views.PrescriptionViewSet, basename='prescription')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),
    
    path('', include(router.urls)),
]