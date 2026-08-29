from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Credentials(models.Model):
    """Central login table for all user types"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('analyst', 'Data Analyst'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    username = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    class Meta:
        db_table = 'credentials'
        verbose_name_plural = 'Credentials'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Admin(models.Model):
    """System Administrator"""
    admin_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'admin'
    
    def __str__(self):
        return self.name


class DataAnalyst(models.Model):
    """Data Analyst user"""
    analyst_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'data_analyst'
    
    def __str__(self):
        return self.name


class Instructor(models.Model):
    """Course Instructor/Teacher"""
    instructor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email_id = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'instructor'
    
    def __str__(self):
        return self.name


class Student(models.Model):
    """Student user"""
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email_id = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    profile_pic = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    skill_level = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'student'
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"


class AdminCredential(models.Model):
    """Links Admin to Credentials"""
    admin = models.OneToOneField(Admin, on_delete=models.CASCADE, primary_key=True)
    username = models.OneToOneField(Credentials, on_delete=models.CASCADE, db_column='username')
    
    class Meta:
        db_table = 'admin_credential'


class AnalystCredential(models.Model):
    """Links Data Analyst to Credentials"""
    analyst = models.OneToOneField(DataAnalyst, on_delete=models.CASCADE, primary_key=True)
    username = models.OneToOneField(Credentials, on_delete=models.CASCADE, db_column='username')
    
    class Meta:
        db_table = 'analyst_cred'


class InstructorCredential(models.Model):
    """Links Instructor to Credentials"""
    instructor = models.OneToOneField(Instructor, on_delete=models.CASCADE, primary_key=True)
    username = models.OneToOneField(Credentials, on_delete=models.CASCADE, db_column='username')
    
    class Meta:
        db_table = 'instructor_cred'


class StudentCredential(models.Model):
    """Links Student to Credentials"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    username = models.OneToOneField(Credentials, on_delete=models.CASCADE, db_column='username')
    
    class Meta:
        db_table = 'student_cred'
