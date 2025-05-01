from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField("nama matkul", max_length=100)
    description = models.TextField("deskripsi", default='-')
    price = models.IntegerField("harga", default=10000)
    image = models.ImageField("gambar", upload_to='course_images/', null=True, blank=True)
    teacher = models.ForeignKey(User, verbose_name="pengajar", on_delete=models.RESTRICT, related_name='courses_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
        #return self.name+":"+str(self.price) 

# --- Model CourseMember (dari PDF hal 8) ---
ROLE_OPTIONS = [('std', "Siswa"), ('ast', "Asisten")]

class CourseMember(models.Model):
    course = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    user = models.ForeignKey(User, verbose_name="siswa", on_delete=models.RESTRICT)
    roles = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber Matkul"
        verbose_name_plural = "Subscriber Matkul"
        unique_together = ('course', 'user')

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.name} ({self.roles})"
        # return str(self.course_id)+" : "+str(self.user_id)

# --- Model CourseContent (dari PDF hal 8) ---
class CourseContent(models.Model):
    name = models.CharField("judul konten", max_length=200)
    description = models.TextField("deskripsi", default='-')
    video_url = models.CharField('URL Video', max_length=200, null=True, blank=True)
    file_attachment = models.FileField("File", upload_to='course_files/', null=True, blank=True)
    course = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    parent = models.ForeignKey("self", verbose_name="induk",
                                on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='children') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"
        ordering = ['created_at']

    def __str__(self) -> str:
        return f"[{self.course.name}] {self.name}"
        # return '['+str(self.course_id)+"] "+self.name # Error jika di-rename

class Comment(models.Model):
    content = models.ForeignKey(CourseContent, verbose_name="konten", on_delete=models.CASCADE)
    member = models.ForeignKey(CourseMember, verbose_name="pengguna", on_delete=models.CASCADE)
    comment = models.TextField('komentar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"
        ordering = ['created_at'] 

    def __str__(self) -> str:
        return f"Comment by {self.member.user.username} on {self.content.name}"
        # return "Komen: "+self.content_id.name+"-"+str(self.user_id)