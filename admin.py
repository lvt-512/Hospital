from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user
from flask import redirect, request

from my_clinic.models import Time, Medicine, Patient, Assistant, Books, ClinicalRecords, Receipt, ReceiptDetails, \
    Question, Advisory, Policy, Disease
from my_clinic import admin, db

import utils


class PolyModel(ModelView):
    excluded_form_columns = ('type',)

    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class DoctorModelView(PolyModel):
    can_export = True


class AssistantModelView(PolyModel):
    can_export = True


class QuestionModelView(AuthenticatedView):
    can_export = True


class AdvisoryModelView(AuthenticatedView):
    can_export = True


class PolicyModelView(AuthenticatedView):
    can_export = True


class MedicineModelView(AuthenticatedView):
    can_export = True


class PatientModelView(AuthenticatedView):
    can_export = True


class TimeModelView(AuthenticatedView):
    can_export = True


class ClinicalRecordsModelView(AuthenticatedView):
    can_export = True


class ReceiptDetailsModelView(AuthenticatedView):
    can_export = True


class ReceiptModelView(AuthenticatedView):
    can_export = True


class BookModelView(AuthenticatedView):
    can_export = True

    column_filters = ('booked_date',)


class DiseaseModelView(AuthenticatedView):
    can_export = True


class OderView(BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/receipt-list.html")

    def is_accessible(self):
        return current_user.is_authenticated


class ProfilePatinetView(BaseView):
    @expose("/")
    def index(self):
        name_patient = request.args.get("namepatient")
        getPatient = utils.get_profile_customer(name_patient= name_patient)
        if getPatient:
            mes = "co du lieu"
            return self.render("admin/search-patient.html", getPatient=getPatient, mes=mes)
        else:
            mes = "chua co du lieu"
            return self.render("admin/search-patient.html", getPatient=getPatient, mes=mes)

    def is_accessible(self):
        return current_user.is_authenticated


class MenuView(BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/stats.html")

    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class AllDetailsModelView(BaseView):
    @expose("/")
    def index(self):
        detail = utils.get_all_receipts()
        return self.render("admin/receipt-list.html", detail=detail)

    def is_accessible(self):
        return current_user.is_authenticated


class StatsView(BaseView):
    @expose("/")
    def index(self):
        date_start = request.args.get("date_start")
        date_end = request.args.get("date_end")
        stats = utils.get_stats_by_date(date_start=date_start, date_end=date_end)
        if stats:
            mes = "Valid data!"
            return self.render("admin/stats.html", stats=stats, mes=mes)
        else:
            mes = "Invalid data!"
            return self.render("admin/stats.html", stats=stats, mes=mes)

    def is_accessible(self):
        return current_user.is_authenticated


class GetDetailView(BaseView):
    @expose("/")
    def index(self):
        name = request.args.get("namepatient")
        getDetail = utils.get_name_receipt_detail(name)
        if getDetail:
            mes = "Valid data!"
            return self.render("admin/receipt-details.html", getDetail=getDetail, mes=mes)
        else:
            mes = "Invalid data!"
            return self.render("admin/receipt-details.html", getDetail=getDetail, mes=mes)

    def is_accessible(self):
        return current_user.is_authenticated


class DetailByDateView(BaseView):
    @expose("/")
    def index(self):
        date1 = request.args.get("date_start")
        date2 = request.args.get("date_end")
        detail_date = utils.get_all_detail_by_date(date1=date1, date2=date2)
        totaldetail_date = utils.get_totaldetail_by_date(date1=date1, date2=date2)
        if detail_date and totaldetail_date:
            mes = "co du lieu"
            return self.render("admin/detail-date.html", detail_date=detail_date, totaldetail_date=totaldetail_date, mes=mes)
        else:
            mes = "chua co du lieu"
            return self.render("admin/detail-date.html", detail_date=detail_date, totaldetail_date=totaldetail_date, mes=mes)

    def is_accessible(self):
        return current_user.is_authenticated


admin.add_view(TimeModelView(Time, db.session, name="Time"))

admin.add_view(MedicineModelView(Medicine, db.session, name="Medicines", category='Lists'))
admin.add_view(PatientModelView(Patient, db.session, name="Patients", category='Lists'))
admin.add_view(AssistantModelView(Assistant, db.session, name="Assistants", category='Lists'))
admin.add_view(BookModelView(Books, db.session, name="Books", endpoint='book-lists', category='Lists'))
admin.add_view(ProfilePatinetView(name="Information Patient", category='Lists'))

admin.add_view(ClinicalRecordsModelView(ClinicalRecords, db.session, name="Type Info Checking", endpoint="Record", category='Medical Examination'))
admin.add_view(ReceiptModelView(Receipt, db.session, name="Choose Doctor", category='Medical Examination'))
admin.add_view(ReceiptDetailsModelView(ReceiptDetails, db.session, name="Get Medicines", category='Medical Examination'))
admin.add_view(AllDetailsModelView(name="Receipt", category="Medical Examination"))
admin.add_view(GetDetailView(name="Receipt Details", category="Medical Examination"))

admin.add_view(QuestionModelView(Question, db.session, name="Question", category="Q&A"))
admin.add_view(AdvisoryModelView(Advisory, db.session, name="Advisory", category="Q&A"))

admin.add_view(PolicyModelView(Policy, db.session, name="Rules"))

admin.add_view(DiseaseModelView(Disease, db.session, name="Disease"))

admin.add_view(StatsView(name="Monthly Report", category="Statistics"))
admin.add_view(DetailByDateView(name="Stats", category="Statistics"))

admin.add_view(MenuView(name="My Profile", endpoint="profile", category="menu"))
admin.add_view(LogoutView(name="Logout", endpoint="logout", category="menu"))
