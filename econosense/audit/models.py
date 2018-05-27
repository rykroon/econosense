from django.db import models

# Create your models here.

class RequestAudit(models.Model):
    scheme          = models.TextField()
    path            = models.TextField()
    method          = models.TextField()
    get             = models.TextField()
    post            = models.TextField()

    #from meta dict
    #meta        = models.TextField()
    remote_addr     = models.TextField()
    #http_user_agent = models.TextField()

    timestamp    = models.DateTimeField(auto_now_add=True)

    #should only be called when creating a new RequestAudit
    def populate_fields(self,request):
        self.scheme = request.scheme
        self.path   = request.path
        self.method = request.method
        self.get    = request.GET.dict()
        self.post   = request.POST.dict()

        try:    self.remote_addr   = request.META['REMOTE_ADDR']
        except: pass

        # try:    self.http_user_agent = request.META['HTTP_USER_AGENT']
        # except: pass


    def __str__(self):
        return self.method + ' request to path ' + self.path
