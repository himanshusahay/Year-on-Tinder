from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models

@python_2_unicode_compatible
class Category(models.Model):
	category_name = models.CharField(max_length = 50)
	 
	def __str__(self):
		return self.category_name + "\n"

	class Meta:
		ordering = ('category_name', )
		verbose_name_plural = "categories"



@python_2_unicode_compatible
class Tag(models.Model):
	tag_name = models.CharField(max_length = 100)
	 
	def __str__(self):
		return self.tag_name + "\n"

	class Meta:
		ordering = ('tag_name', )


class User(models.Model):
	# Count of number of matches
	num_matches = models.IntegerField()


@python_2_unicode_compatible
class Line(models.Model):
	line_text = models.TextField()
	tags = models.ManyToManyField(Tag)
	categories = models.ManyToManyField(Category)
	 
	def __str__(self):
		return self.line_text + "\n"

	class Meta:
		ordering = ('line_text', )

# @python_2_unicode_compatible
class Match(models.Model):
	# Someone could have matched with many people
 	user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
	match_age = models.IntegerField()
	match_distance = models.IntegerField()


	# def __str__(self):
	# 	return self.match_name

	# class Meta:
	# 	ordering = ('match_name', )


@python_2_unicode_compatible
class PictureTag(models.Model):
	tag_name = models.CharField(max_length = 100)
	users = models.ManyToManyField(User)
	 
	def __str__(self):
		return self.tag_name + "\n"

	class Meta:
		ordering = ('tag_name', )

