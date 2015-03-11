from django.db.models import ImageField
from PIL import Image
from cStringIO import StringIO
from django.db.models import signals
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class ImageConvertField(ImageField):
    
    def __init__(self, output_format='png', **kwargs):
        self.output_format = output_format.lower()
        ImageField.__init__(self, **kwargs)

    def contribute_to_class(self, cls, name):
        super(ImageConvertField, self).contribute_to_class(cls, name)
        signals.pre_save.connect(self.convert_image, sender=cls)

    def convert_image(self, instance, force=False, *args, **kwargs):
        file = getattr(instance, self.attname)
        if file:
            try:
                im = Image.open(StringIO(file.read()))
            except IOError:
                # file does not exist
                return
            if im.format.lower() != self.output_format:
                if im.mode != 'RGB':
                    im = im.convert('RGB')
                temp_handle = StringIO()
                im.save(temp_handle, self.output_format)
                temp_handle.seek(0)
                suf = SimpleUploadedFile("%s.%s" % (os.path.splitext(os.path.basename(file.name))[0], self.output_format), temp_handle.read())
                getattr(instance, self.attname).save(suf.name, suf)
