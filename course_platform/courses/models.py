from django.db import models
from accounts.models import Student, Instructor


class Topics(models.Model):
    """Course topics"""
    name = models.CharField(max_length=100, primary_key=True)
    field = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'topics'
        verbose_name_plural = 'Topics'
    
    def __str__(self):
        return f"{self.name} ({self.field})"


class Books(models.Model):
    """Reference books"""
    isbn_code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=150)
    authors = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'books'
        verbose_name_plural = 'Books'
    
    def __str__(self):
        return self.name


class University(models.Model):
    """Partner universities"""
    university_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique='true')
    country = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'university'
        verbose_name_plural = 'Universities'
    
    def __str__(self):
        return f"{self.name}, {self.country}"


class Course(models.Model):
    """Main course entity"""
    PROGRAM_TYPE_CHOICES = [
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('degree', 'Degree'),
    ]
    
    course_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,unique=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, default='certificate')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    videos = models.TextField(blank=True, null=True)  
    notes = models.TextField(blank=True, null=True)   
    
    books = models.ManyToManyField(Books, through='CourseBooks', related_name='courses')
    topics = models.ManyToManyField(Topics, related_name='courses', blank=True)
    
    class Meta:
        db_table = 'course'
    
    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"


class CourseBooks(models.Model):
    """Links Course to Books"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, db_column='isbn_code')
    
    class Meta:
        db_table = 'course_books'
        unique_together = ('course', 'book')


class Takes(models.Model):
    """Student enrollment in courses"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    evaluation = models.IntegerField(default=0)  
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'takes'
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.name} enrolled in {self.course.name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.evaluation < 0 or self.evaluation > 100:
            raise ValidationError('Evaluation must be between 0 and 100')


class Teaches(models.Model):
    """Instructor assignment to courses"""
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'teaches'
        unique_together = ('instructor', 'course')
    
    def __str__(self):
        return f"{self.instructor.name} teaches {self.course.name}"


class Partner(models.Model):
    """University partnership with courses"""
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'partner'
        unique_together = ('university', 'course')
    
    def __str__(self):
        return f"{self.university.name} partners with {self.course.name}"
