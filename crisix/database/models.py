from django.db import models
import datetime

# Create your models here.
class Entity(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.TextField(blank=True, null=True)
    kind = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    def __lt__(self, rhs):
        return self.created < rhs.created
    def __unicode__(self):
        return u'%s%s%s%s%s%s' % (
            self.id + '\n', 
            self.name + '\n', 
            self.kind + '\n' if self.kind is not None else '', 
            self.location + '\n' if self.location is not None else '', 
            self.summary + '\n' if self.summary is not None else '',
            '\n'.join([str(w) for w in self.elements.all()]) + '\n',
        )

class Crisis(Entity):
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    himpact = models.TextField(blank=True, default='')
    eimpact = models.TextField(blank=True, default='')
    resources = models.TextField(blank=True, default='')
    help = models.TextField(blank=True, default='')
    organizations = models.ManyToManyField('Organization', related_name='crises')
    people = models.ManyToManyField('Person', related_name='crises')
    def __unicode__(self):
        return u'%s%s%s%s%s%s%s%s%s' % (
            super(Crisis, self).__unicode__(),
            str(self.date) + '\n' if self.date is not None else '', 
            str(self.time) + '\n' if self.time is not None else '', 
            self.himpact + '\n' if self.himpact is not None else '', 
            self.eimpact + '\n' if self.eimpact is not None else '',
            self.resources + '\n' if self.resources is not None else '',
            self.help + '\n' if self.help is not None else '',
            '\n'.join([o.id for o in self.organizations.all()]) + '\n',
            '\n'.join([p.id for p in self.people.all()]) + '\n',
        )

class Organization(Entity):
    history = models.TextField(blank=True, default='')
    contact = models.TextField(blank=True, default='')
    people = models.ManyToManyField('Person', related_name='organizations')
    def __unicode__(self):
        return u'%s%s%s%s%s' % (
            super(Organization, self).__unicode__(),
            self.history + '\n' if self.history is not None else '',
            self.contact + '\n' if self.history is not None else '',
            '\n'.join([c.id for c in self.crises.all()]) + '\n',
            '\n'.join([p.id for p in self.people.all()]) + '\n',
        )

class Person(Entity):
    def __unicode__(self):
        return u'%s%s%s' % (
            super(Person, self).__unicode__(),
            '\n'.join([c.id for c in self.crises.all()]) + '\n',
            '\n'.join([o.id for o in self.organizations.all()]) + '\n',
        )

class WebElement(models.Model):
    entity = models.ForeignKey(Entity, related_name='elements')
    ctype = models.CharField(max_length=10)
    href = models.URLField(blank=True, null=True)
    embed = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, default='', null=True)
    def __unicode__(self):
        return u'%s%s%s%s' % (
            self.ctype + '\n',
            self.href + '\n' if self.href is not None else '',
            self.embed + '\n' if self.embed is not None else '',
            self.text + '\n' if self.text is not None else '',
        )
