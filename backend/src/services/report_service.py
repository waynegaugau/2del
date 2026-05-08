from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth

from src.models import Appointment, Clinic, Payment, Pet, Service, User


class ReportService:
    @staticmethod
    def _date_range_payload(date_from=None, date_to=None):
        return {
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
        }

    @staticmethod
    def _format_decimal(value):
        return f"{value or Decimal('0.00'):.2f}"

    @staticmethod
    def _apply_datetime_date_range(queryset, field_name, date_from=None, date_to=None):
        if date_from:
            queryset = queryset.filter(**{f"{field_name}__date__gte": date_from})
        if date_to:
            queryset = queryset.filter(**{f"{field_name}__date__lte": date_to})
        return queryset

    @staticmethod
    def _appointment_status_counts(queryset):
        counts = {
            status: 0
            for status, _label in Appointment.STATUS_CHOICES
        }
        rows = queryset.values("status").annotate(total=Count("id"))
        for row in rows:
            counts[row["status"]] = row["total"]
        return counts

    @staticmethod
    def get_overview(date_from=None, date_to=None):
        paid_payments = ReportService._apply_datetime_date_range(
            Payment.objects.filter(status=Payment.STATUS_PAID),
            "paid_at",
            date_from,
            date_to,
        )
        appointments = ReportService._apply_datetime_date_range(
            Appointment.objects.all(),
            "created_at",
            date_from,
            date_to,
        )
        new_pet_owners = ReportService._apply_datetime_date_range(
            User.objects.filter(role=User.ROLE_PET_OWNER),
            "created_at",
            date_from,
            date_to,
        )
        new_pets = ReportService._apply_datetime_date_range(
            Pet.objects.all(),
            "created_at",
            date_from,
            date_to,
        )

        total_revenue = paid_payments.aggregate(total=Sum("amount"))["total"]

        return {
            **ReportService._date_range_payload(date_from, date_to),
            "total_revenue": ReportService._format_decimal(total_revenue),
            "paid_payment_count": paid_payments.count(),
            "appointment_count": appointments.count(),
            "appointment_status": ReportService._appointment_status_counts(appointments),
            "new_pet_owner_count": new_pet_owners.count(),
            "new_pet_count": new_pets.count(),
            "clinic_count": Clinic.objects.count(),
            "service_count": Service.objects.count(),
        }

    @staticmethod
    def get_revenue_report(date_from=None, date_to=None, group_by="day"):
        paid_payments = ReportService._apply_datetime_date_range(
            Payment.objects.filter(status=Payment.STATUS_PAID),
            "paid_at",
            date_from,
            date_to,
        )

        trunc_function = TruncMonth if group_by == "month" else TruncDate
        rows = (
            paid_payments
            .annotate(period=trunc_function("paid_at"))
            .values("period")
            .annotate(
                revenue=Sum("amount"),
                paid_payment_count=Count("id"),
            )
            .order_by("period")
        )

        series = []
        for row in rows:
            period = row["period"]
            period_value = period.strftime("%Y-%m") if group_by == "month" else period.isoformat()
            series.append(
                {
                    "period": period_value,
                    "revenue": ReportService._format_decimal(row["revenue"]),
                    "paid_payment_count": row["paid_payment_count"],
                },
            )

        total_revenue = paid_payments.aggregate(total=Sum("amount"))["total"]

        return {
            **ReportService._date_range_payload(date_from, date_to),
            "group_by": group_by,
            "total_revenue": ReportService._format_decimal(total_revenue),
            "series": series,
        }

    @staticmethod
    def get_clinic_report(date_from=None, date_to=None):
        clinics = {
            clinic.id: {
                "clinic_id": clinic.id,
                "clinic_name": clinic.name,
                "appointment_count": 0,
                "completed_appointment_count": 0,
                "paid_payment_count": 0,
                "revenue": Decimal("0.00"),
            }
            for clinic in Clinic.objects.all()
        }

        appointments = ReportService._apply_datetime_date_range(
            Appointment.objects.all(),
            "created_at",
            date_from,
            date_to,
        )
        appointment_rows = (
            appointments
            .values("clinic_id")
            .annotate(
                appointment_count=Count("id"),
                completed_appointment_count=Count(
                    "id",
                    filter=Q(status=Appointment.STATUS_COMPLETED),
                ),
            )
        )
        for row in appointment_rows:
            clinic_data = clinics.get(row["clinic_id"])
            if clinic_data:
                clinic_data["appointment_count"] = row["appointment_count"]
                clinic_data["completed_appointment_count"] = row["completed_appointment_count"]

        paid_payments = ReportService._apply_datetime_date_range(
            Payment.objects.filter(status=Payment.STATUS_PAID),
            "paid_at",
            date_from,
            date_to,
        )
        payment_rows = (
            paid_payments
            .values("clinic_id")
            .annotate(
                paid_payment_count=Count("id"),
                revenue=Sum("amount"),
            )
        )
        for row in payment_rows:
            clinic_data = clinics.get(row["clinic_id"])
            if clinic_data:
                clinic_data["paid_payment_count"] = row["paid_payment_count"]
                clinic_data["revenue"] = row["revenue"] or Decimal("0.00")

        items = sorted(
            clinics.values(),
            key=lambda item: (-item["revenue"], item["clinic_name"]),
        )
        for item in items:
            item["revenue"] = ReportService._format_decimal(item["revenue"])

        return {
            **ReportService._date_range_payload(date_from, date_to),
            "clinics": items,
        }
